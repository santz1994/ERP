"""
Sewing Module API Endpoints
Production workflow: Material receipt → Qty validation → 3-stage sewing → Inline QC → Transfer to Finishing
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from app.core.dependencies import get_db, require_role
from app.core.models.users import User
from app.modules.sewing.models import (
    AcceptTransferRequest, ValidateInputRequest, ProcessSewingStepRequest,
    InlineQCRequest, SegregationCheckRequest, TransferToFinishingRequest,
    SewingWorkOrderResponse, SegregationValidationResponse
)
from app.modules.sewing.services import SewingService


router = APIRouter(prefix="/production/sewing", tags=["Sewing Module"])


@router.post("/accept-transfer", response_model=dict)
async def accept_transfer_from_cutting(
    request: AcceptTransferRequest,
    current_user: User = Depends(require_role(["SPV Sewing", "Operator_Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 300: Accept Transfer & Material Receipt
    
    **Handshake Digital (QT-09):**
    1. Operator scans transfer slip barcode
    2. System verifies transfer is in LOCKED state (from Cutting)
    3. Records actual received quantity
    4. **Unlocks stock** (status: LOCKED → ACCEPTED)
    5. Updates line occupancy (Cutting line → Clear)
    
    **Critical:** Must match qty from Cutting transfer ±2%
    
    Response confirms:
    - Handshake status (ACCEPTED)
    - Next step (Material validation vs BOM)
    
    Requires: SPV Sewing or Operator_Sewing
    """
    return SewingService.accept_transfer_and_validate(
        db=db,
        transfer_slip_number=request.transfer_slip_number,
        received_qty=request.received_qty,
        user_id=current_user.id,
        notes=request.notes
    )


@router.post("/validate-input", response_model=dict)
async def validate_material_input(
    request: ValidateInputRequest,
    current_user: User = Depends(require_role(["SPV Sewing", "QC Inspector", "Admin"])),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 310: Validate Input Qty vs BOM
    
    **Three Possible Outcomes:**
    
    1. **OK** - Qty matches BOM target → Proceed to Assembly
    2. **SHORTAGE** - Qty < target → Auto-request supplementary materials (benang, label)
       - Step 320: System auto-generates material requisition
       - Warehouse approves and issues materials
       - Sewing resumes with full complement
    3. **SURPLUS** - Qty > target → Process with full qty
    
    Response includes:
    - Variance analysis
    - Auto-actions triggered (if any)
    - Approval status for shortages
    
    Requires: SPV Sewing or QC Inspector
    """
    return SewingService.validate_input_vs_bom(
        db=db,
        work_order_id=request.work_order_id,
        received_qty=request.received_qty
    )


@router.post("/process-stage/{step_number}", response_model=dict)
async def process_sewing_stage(
    work_order_id: int,
    step_number: int,
    request: ProcessSewingStepRequest,
    current_user: User = Depends(require_role(["Operator_Sewing", "SPV Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 330-350: 3-Stage Sewing Process
    
    **Three Sequential Stages:**
    
    **Stage 1 (Step 330): Proses Jahit 1 - Assembly (Rakit Body)**
    - Assemble body pieces
    - Attach main components
    
    **Stage 2 (Step 340): Proses Jahit 2 - Labeling (Attach Label)**
    - Verify label matches destination country
    - Attach IKEA label with care instructions
    - Verify week code
    
    **Stage 3 (Step 350): Proses Jahit 3 - Stik Balik (Loop Stitching)**
    - Add special stitches (fingers, tails, etc.)
    - Final reinforcement stitches
    - → Then proceed to QC inspection
    
    Response includes next stage or QC entry point.
    
    Requires: Operator_Sewing
    """
    return SewingService.process_sewing_step(
        db=db,
        work_order_id=work_order_id,
        step_number=step_number,
        qty_processed=request.qty_processed,
        notes=request.notes
    )


@router.post("/qc-inspect", response_model=dict)
async def perform_inline_qc_inspection(
    request: InlineQCRequest,
    current_user: User = Depends(require_role(["QC Inspector", "SPV Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 360-375: INLINE QC INSPECTION & REWORK
    
    **QC Decision Tree:**
    
    **✅ PASS** (pass_qty):
    - Jahitan bagus, tension OK, tidak ada cacat
    - → Proceed to Segregation Check (Step 380)
    
    **🔄 REWORK** (rework_qty):
    - Jahitan perlu diperbaiki (benang longgar, lubang, dll)
    - Step 370: Return units to Stik Balik stage
    - Operator dapat memperbaiki dengan operator yang sama atau lain
    - After rework: Return to QC for re-inspection
    
    **❌ SCRAP** (scrap_qty):
    - Jahitan tidak bisa diperbaiki
    - Step 375: Reject - create defect report
    - Document scrap reason and quantity
    - Remove from batch, adjust MO qty_produced
    
    Response includes:
    - Pass rate percentage
    - Rework routing (if any)
    - Scrap documentation (if any)
    
    Requires: QC Inspector
    """
    return SewingService.perform_inline_qc(
        db=db,
        work_order_id=request.work_order_id,
        inspector_id=request.inspector_id,
        pass_qty=request.pass_qty or 0,
        rework_qty=request.rework_qty or 0,
        scrap_qty=request.scrap_qty or 0,
        defect_reason=request.defect_reason
    )


@router.get("/segregation-check/{work_order_id}", response_model=SegregationValidationResponse)
async def check_segregation(
    work_order_id: int,
    current_user: User = Depends(require_role(["SPV Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> SegregationValidationResponse:
    """
    **GET** - Step 380: SEGREGASI CHECK (Destination Consistency)
    
    **QT-09 Gold Standard - Prevent Mixed Destinations:**
    
    **The Problem:**
    - Sewing line processes batches for different countries
    - If destination differs from current line → product mixing risk
    - Example: Line finishing USA batch, Sewing sends EUROPE batch
    
    **The Solution (QT-09):**
    - Check: Does batch destination = current Finishing line destination?
    - If YES ✅: Can transfer directly (no delay)
    - If NO ❌: **ALARM** - Must implement 5-meter product segregation
      - Either: Wait for line to clear (manual line clearance)
      - Or: Hold batch in segregation zone for 5 minutes
    
    Response indicates:
    - `destinations_match`: True if same destination
    - `segregation_status`: "CLEAR" or "BLOCKED - Destination Mismatch"
    - `requires_jeda`: Whether 5-meter segregation zone required
    
    **Purpose:** Maintain 100% destination accuracy for IKEA shipments
    
    Requires: SPV Sewing
    """
    destinations_match, blocking_reason, info = SewingService.check_segregation(
        db=db,
        work_order_id=work_order_id
    )
    
    return SegregationValidationResponse(
        work_order_id=info["work_order_id"],
        current_destination=info["current_line_destination"],
        pending_destination=info["batch_destination"],
        destinations_match=info["destinations_match"],
        segregation_status=info.get("segregation_status", "UNKNOWN"),
        requires_jeda=info.get("requires_jeda", False),
        jeda_duration_minutes=info.get("jeda_duration_minutes")
    )


@router.post("/transfer-to-finishing", response_model=dict)
async def transfer_to_finishing_dept(
    request: TransferToFinishingRequest,
    current_user: User = Depends(require_role(["SPV Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 381-383: TRANSFER & HANDSHAKE DIGITAL
    
    **QT-09 Gold Standard Implementation:**
    
    **Step 381:** Print Surat Jalan Transfer to Finishing
    - Verified segregation (destination match)
    - Generate transfer slip with QT-09 reference
    - Record all batch details
    
    **Step 383:** HANDSHAKE DIGITAL - Lock Stock
    - Stock WIP SEW is LOCKED in database (status = LOCKED)
    - Qty held in reserve pending Finishing dept ACCEPT
    - **Prevents stock loss between departments**
    
    **Handshake Flow:**
    1. ✅ Sewing prints transfer → Stock LOCKED
    2. Finishing scans transfer (ACCEPT) → Stock ACCEPTED
    3. Stock released to Finishing → Transfer COMPLETED
    
    Response includes:
    - Transfer slip barcode number
    - QT-09 handshake protocol reference
    - Lock status and lock reason
    
    **Next Step:** Operator in Finishing scans transfer slip to ACCEPT
    
    Requires: SPV Sewing
    """
    return SewingService.transfer_to_finishing(
        db=db,
        work_order_id=request.work_order_id,
        transfer_qty=request.transfer_qty,
        user_id=current_user.id
    )


@router.get("/status/{work_order_id}", response_model=SewingWorkOrderResponse)
async def get_sewing_work_order_status(
    work_order_id: int,
    current_user: User = Depends(require_role(["Operator_Sewing", "SPV Sewing", "QC Inspector", "Admin"])),
    db: Session = Depends(get_db)
) -> SewingWorkOrderResponse:
    """
    **GET** - Retrieve Current Sewing Work Order Status
    
    Real-time status including:
    - Current processing stage
    - Qty through each stage (Assembly → Labeling → Stik)
    - QC results (pass/rework/scrap)
    - Start/completion times
    
    Accessible to: Operators, SPV, QC, Admin
    """
    from app.core.models.manufacturing import WorkOrder
    
    wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail="Work order not found")
    
    return SewingWorkOrderResponse(
        id=wo.id,
        mo_id=wo.mo_id,
        product_id=wo.product_id,
        status=wo.status.value,
        input_qty=wo.input_qty,
        assembly_qty=wo.input_qty,  # Placeholder - would track stages separately in production
        label_qty=wo.input_qty,
        stik_qty=wo.input_qty,
        pass_qty=wo.output_qty,
        rework_qty=0,
        scrap_qty=wo.reject_qty,
        started_at=wo.start_time,
        completed_at=wo.end_time
    )


@router.get("/pending", response_model=List[SewingWorkOrderResponse])
async def get_pending_sewing_orders(
    current_user: User = Depends(require_role(["SPV Sewing", "Operator_Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> List[SewingWorkOrderResponse]:
    """
    **GET** - List All Pending Sewing Work Orders
    
    Returns work orders awaiting:
    - Material transfer acceptance
    - Processing through 3 stages
    - QC inspection
    - Transfer to Finishing
    
    Useful for line management and operator assignment.
    """
    from app.core.models.manufacturing import WorkOrder, Department, WorkOrderStatus
    
    orders = db.query(WorkOrder).filter(
        WorkOrder.department == Department.SEWING,
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.RUNNING])
    ).all()
    
    return [
        SewingWorkOrderResponse(
            id=o.id,
            mo_id=o.mo_id,
            product_id=o.product_id,
            status=o.status.value,
            input_qty=o.input_qty,
            assembly_qty=None,
            label_qty=None,
            stik_qty=None,
            pass_qty=None,
            rework_qty=None,
            scrap_qty=o.reject_qty,
            started_at=o.start_time,
            completed_at=o.end_time
        )
        for o in orders
    ]


@router.post("/internal-loop", response_model=dict)
async def create_internal_loop(
    work_order_id: int,
    from_stage: int,
    to_stage: int,
    qty_to_return: float,
    reason: str,
    notes: str = None,
    current_user: User = Depends(require_role(["SPV Sewing", "Admin"])),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Internal Loop/Return to Previous Stage
    
    **Note 1: Sewing Loop (Balik lagi) - Internal Line Balancing**
    
    For products requiring multiple passes through sewing stages WITHOUT
    leaving the Sewing department. This is NOT a rework due to defects,
    but part of normal production flow for certain product types.
    
    **Common Use Cases:**
    - After Stik (Stage 3) → Return to Assembly (Stage 1) for final components
    - Finger stitching on soft toys requiring additional stik work
    - Complex patterns needing multiple assembly passes
    - Special embellishments added after main body completion
    
    **Internal Control:**
    - No external transfer slip (Surat Jalan) required
    - Uses internal work card (Kartu Kendali Meja)
    - Stays within Sewing department
    - Tracked via Work Order metadata
    
    **Stages:**
    - 1: Assembly (Pos 1: Rakit)
    - 2: Labeling (Pos 2: Label)
    - 3: Stik (Pos 3: Stik Balik)
    
    **Validation:**
    - from_stage > to_stage (must return to PREVIOUS stage)
    - Only SPV Sewing can authorize internal loops
    
    **Example:**
    ```json
    {
        "work_order_id": 123,
        "from_stage": 3,
        "to_stage": 1,
        "qty_to_return": 100.0,
        "reason": "Final Assembly after Stik",
        "notes": "Add final components (eyes, nose) after body stitching"
    }
    ```
    
    Reference: Flow Production.md - Note 1
    Requires: SPV Sewing
    """
    return SewingService.internal_loop_return(
        db=db,
        work_order_id=work_order_id,
        from_stage=from_stage,
        to_stage=to_stage,
        qty_to_return=Decimal(str(qty_to_return)),
        reason=reason,
        user_id=current_user.id,
        notes=notes
    )
