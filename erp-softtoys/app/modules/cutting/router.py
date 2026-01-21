"""
Cutting Module API Endpoints
Production workflow: SPK reception → Material allocation → Cutting execution → QC → Transfer
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List
from datetime import datetime

from app.core.dependencies import get_db, require_permission
from app.core.models.users import User
from app.modules.cutting.models import (
    MaterialIssueRequest, StartCuttingRequest, CompleteCuttingRequest,
    ShortageHandlingRequest, LineTransferRequest, CuttingWorkOrderResponse,
    LineClearanceCheckResponse
)
from app.modules.cutting.services import CuttingService


router = APIRouter(prefix="/production/cutting", tags=["Cutting Module"])


@router.post("/spk/receive", response_model=dict)
async def receive_spk_and_allocate_material(
    request: MaterialIssueRequest,
    current_user: User = Depends(require_permission("cutting.allocate_material")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 200: Receive SPK & Allocate Material
    
    Workflow:
    1. Validate SPK for Cutting department
    2. Check BOM material requirements
    3. Verify warehouse stock availability (FIFO)
    4. Create material issue slip
    5. Reserve stock for this work order
    6. Return material allocation list
    
    Requires: SPV Cutting or Admin role
    """
    return CuttingService.receive_spk_and_allocate_material(
        db=db,
        work_order_id=request.work_order_id,
        operator_id=current_user.id
    )


@router.post("/start", response_model=dict)
async def start_cutting_operation(
    request: StartCuttingRequest,
    current_user: User = Depends(require_permission("cutting.complete_operation")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 210: Begin Cutting Operation
    
    Updates work order status to RUNNING with operator assignment.
    Marks start time for production tracking.
    
    Response includes current line status and material allocation confirmation.
    """
    from app.core.models.manufacturing import WorkOrder, WorkOrderStatus
    
    wo = db.query(WorkOrder).filter(WorkOrder.id == request.work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    wo.status = WorkOrderStatus.RUNNING
    wo.start_time = datetime.utcnow()
    wo.worker_id = request.operator_id
    db.commit()
    
    return {
        "message": "Cutting operation started",
        "work_order_id": request.work_order_id,
        "operator_id": request.operator_id,
        "start_time": wo.start_time.isoformat(),
        "status": "Running"
    }


@router.post("/complete", response_model=dict)
async def complete_cutting_operation(
    request: CompleteCuttingRequest,
    current_user: User = Depends(require_permission("cutting.complete_operation")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 220: Record Output & Detect Shortage/Surplus
    
    Records actual cutting output and initiates variance handling:
    
    - **SHORTAGE** (output < target):
      - Generate Waste Report (Step 230)
      - Request SPV approval for additional material (Step 240)
      - Automatic requisition to warehouse (Step 250)
    
    - **SURPLUS** (output > target):
      - System logs surplus quantity (Step 270)
      - **Auto-triggers SPK Sewing revision** (Step 280)
      - Updates downstream BOM quantities
    
    - **EXACT** (output = target):
      - Ready for transfer to next department
    
    Requires: QC Inspector, SPV Cutting, or Admin
    """
    return CuttingService.complete_cutting_operation(
        db=db,
        work_order_id=request.work_order_id,
        actual_output=request.actual_output,
        reject_qty=request.reject_qty,
        notes=request.notes
    )


@router.post("/shortage/handle", response_model=dict)
async def handle_material_shortage(
    request: ShortageHandlingRequest,
    current_user: User = Depends(require_permission("cutting.handle_variance")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 230-250: SHORTAGE LOGIC Handling
    
    When actual output < target, this endpoint:
    1. Creates Waste Report with shortage details
    2. Generates Unplanned Material Requisition (Step 240)
    3. Sends to SPV for approval (decision logic: Step 240)
    4. If approved: Warehouse auto-issues additional material (Step 250)
    5. Resumes cutting operation
    
    This implements the shortage escalation workflow.
    
    Requires: SPV Cutting (approval authority)
    """
    return CuttingService.handle_shortage(
        db=db,
        work_order_id=request.work_order_id,
        shortage_qty=request.shortage_qty,
        reason=request.reason
    )


@router.get("/line-clear/{work_order_id}", response_model=LineClearanceCheckResponse)
async def check_line_clearance(
    work_order_id: int,
    destination_dept: str,
    current_user: User = Depends(require_permission("cutting.line_clearance")),
    db: Session = Depends(get_db)
) -> LineClearanceCheckResponse:
    """
    **GET** - Step 290: LINE CLEARANCE CHECK (QT-09 Requirement)
    
    Before Cutting can transfer output to Sewing/Embroidery:
    
    **Mandatory QT-09 Cek 1-2 Validation:**
    - ✅ Destination line must be CLEAR (no previous batch)
    - ✅ If destination line OCCUPIED → BLOCK transfer (prevents article mixing)
    - ⚠️ Alert SPV if line not clear (manual segregation delay required)
    
    Response indicates:
    - `can_transfer`: True if line clear, False if blocked
    - `blocking_reason`: Why transfer blocked (if applicable)
    
    **Gold Standard (QT-09-TCK03):** Prevents batch contamination
    
    Requires: SPV Cutting
    """
    is_clear, blocking_reason, info = CuttingService.check_line_clearance(
        db=db,
        work_order_id=work_order_id,
        destination_dept=destination_dept
    )
    
    return LineClearanceCheckResponse(
        work_order_id=info["work_order_id"],
        destination_dept=info["destination_dept"],
        current_line_status=info["line_status"],
        last_article=info["current_article"],
        can_transfer=info["can_transfer"],
        blocking_reason=info["blocking_reason"]
    )


@router.post("/transfer", response_model=dict)
async def transfer_to_next_department(
    request: LineTransferRequest,
    current_user: User = Depends(require_permission("cutting.create_transfer")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 291-293: TRANSFER & HANDSHAKE DIGITAL
    
    **QT-09 Gold Standard Implementation:**
    
    **Step 291:** Print Surat Jalan Transfer
    - Verified line clearance (CUT-SEW or CUT-EMBO)
    - Generate transfer slip with QT-09 reference
    
    **Step 293:** HANDSHAKE DIGITAL - Lock Stock
    - Stock WIP CUT is LOCKED in database (status = LOCKED)
    - Qty held in reserve pending receiving dept ACCEPT
    - **Prevents double-counting or lost stock**
    
    **Handshake Flow:**
    1. ✅ Cutting prints transfer → Stock LOCKED
    2. Sewing scans transfer (ACCEPT) → Stock ACCEPTED
    3. Stock released to Sewing → Transfer COMPLETED
    
    Response includes:
    - Transfer slip number (barcode scannable)
    - QT-09 handshake protocol reference
    - Lock status and lock reason
    
    **Next Step:** Operator in receiving department scans transfer slip to ACCEPT
    
    Requires: SPV Cutting
    """
    return CuttingService.create_transfer_to_next_dept(
        db=db,
        work_order_id=request.work_order_id,
        destination_dept=request.destination_dept,
        transfer_qty=request.transfer_qty,
        user_id=current_user.id
    )


@router.get("/status/{work_order_id}", response_model=CuttingWorkOrderResponse)
async def get_cutting_work_order_status(
    work_order_id: int,
    current_user: User = Depends(require_permission("cutting.view_status")),
    db: Session = Depends(get_db)
) -> CuttingWorkOrderResponse:
    """
    **GET** - Retrieve Current Cutting Work Order Status
    
    Real-time status of cutting operation:
    - Current processing stage
    - Input/Output/Reject quantities
    - Start/completion times
    - Material allocation status
    
    Accessible to: Operators, SPV, QC, Admin
    """
    from app.core.models.manufacturing import WorkOrder
    
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    return CuttingWorkOrderResponse(
        id=wo.id,
        mo_id=wo.mo_id,
        product_id=wo.product_id,
        status=wo.status.value,
        input_qty=wo.input_qty,
        output_qty=wo.output_qty,
        reject_qty=wo.reject_qty,
        started_at=wo.start_time,
        completed_at=wo.end_time
    )


@router.get("/pending", response_model=List[CuttingWorkOrderResponse])
async def get_pending_cutting_orders(
    current_user: User = Depends(require_permission("cutting.view_status")),
    db: Session = Depends(get_db)
) -> List[CuttingWorkOrderResponse]:
    """
    **GET** - List All Pending Cutting Work Orders
    
    Returns work orders awaiting execution:
    - Status = Pending (not started)
    - Status = Running (in progress)
    
    For Cutting Line Management & Operator Assignment
    """
    from app.core.models.manufacturing import WorkOrder, Department, WorkOrderStatus
    
    orders = db.query(WorkOrder).filter(
        WorkOrder.department == Department.CUTTING,
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.RUNNING])
    ).all()
    
    return [
        CuttingWorkOrderResponse(
            id=o.id,
            mo_id=o.mo_id,
            product_id=o.product_id,
            status=o.status.value,
            input_qty=o.input_qty,
            output_qty=o.output_qty,
            reject_qty=o.reject_qty,
            started_at=o.start_time,
            completed_at=o.end_time
        )
        for o in orders
    ]
