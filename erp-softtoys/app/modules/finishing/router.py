"""Finishing Module API Endpoints
Production workflow: WIP receipt → Line clearance → Stuffing → Closing → Metal detector QC → Conversion to FG.
"""

from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.base_production_service import BaseProductionService
from app.core.dependencies import get_db, require_permission
from app.core.models.users import User
from app.modules.finishing.models import (
    AcceptWIPRequest,
    ClosingAndGroomingRequest,
    ConversionRequest,
    FinishingWorkOrderResponse,
    MetalDetectorTestRequest,
    StuffingRequest,
)
from app.modules.finishing.services import FinishingService

router = APIRouter(prefix="/production/finishing", tags=["Finishing Module"])


@router.post("/accept-transfer", response_model=dict)
async def accept_wip_from_sewing(
    request: AcceptWIPRequest,
    current_user: User = Depends(require_permission("finishing.accept_transfer")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 400: Accept WIP SEW Transfer.

    **Handshake Digital (QT-09):**
    1. Operator scans transfer slip from Sewing
    2. System verifies transfer is LOCKED
    3. Records actual received qty
    4. **Unlocks stock** (status: LOCKED → ACCEPTED)
    5. Marks Sewing line as CLEAR

    Response confirms handshake and next step.

    Requires: SPV Finishing or Operator_Finishing
    """
    return FinishingService.accept_wip_transfer(
        db=db,
        transfer_slip_number=request.transfer_slip_number,
        received_qty=request.received_qty,
        user_id=current_user.id,
        notes=request.notes
    )


@router.post("/line-clearance-check/{work_order_id}", response_model=dict)
async def check_packing_line_clearance(
    work_order_id: int,
    current_user: User = Depends(require_permission("finishing.line_clearance")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 405-406: LINE CLEARANCE CHECK.

    Before stuffing can begin:
    - Check if Packing line has finished previous batch
    - If still occupied → BLOCK stuffing
    - If clear → Proceed to Step 410

    **Purpose:** Prevent product mixing downstream in Packing

    Requires: SPV Finishing
    """
    is_clear, blocking_reason = FinishingService.check_line_clearance_packing(
        db=db,
        work_order_id=work_order_id
    )

    if not is_clear:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot proceed - {blocking_reason}"
        )

    return {
        "work_order_id": work_order_id,
        "line_clearance_status": "CLEAR",
        "message": "Packing line is clear - ready to proceed to stuffing",
        "next_step": "Step 410: Stuffing Operation"
    }


@router.post("/stuffing", response_model=dict)
async def perform_stuffing_operation(
    request: StuffingRequest,
    current_user: User = Depends(require_permission("finishing.perform_stuffing")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 410: Perform Stuffing (Isi Dacron).

    Add filling material:
    - Usually Dacron polyester fiber
    - Fill to firmness standard
    - Record qty completed

    Proceeds to Step 420: Closing & Grooming

    Requires: Operator_Finishing
    """
    return FinishingService.perform_stuffing(
        db=db,
        work_order_id=request.work_order_id,
        operator_id=request.operator_id,
        stuffing_material=request.stuffing_material,
        qty_stuffed=request.qty_stuffed,
        notes=request.notes
    )


@router.post("/closing-grooming", response_model=dict)
async def perform_closing_grooming(
    request: ClosingAndGroomingRequest,
    current_user: User = Depends(require_permission("finishing.perform_closing")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 420: Closing & Grooming (Jahit Tutup & Rapih).

    Final assembly steps:
    - Sew closing seams with sturdy stitching
    - Groom product (straighten appendages, smooth seams)
    - Check overall appearance

    Next: Step 430 - CRITICAL Metal Detector Test

    Requires: Operator_Finishing
    """
    return FinishingService.perform_closing_and_grooming(
        db=db,
        work_order_id=request.work_order_id,
        operator_id=request.operator_id,
        qty_closed=request.qty_closed,
        quality_notes=request.quality_notes
    )


@router.post("/metal-detector-test", response_model=dict)
async def perform_metal_detector_test(
    request: MetalDetectorTestRequest,
    current_user: User = Depends(require_permission("finishing.metal_detector_qc")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 430-435: CRITICAL POINT - Metal Detector Test.

    **⚠️ SAFETY CRITICAL - IKEA ISO 8124 Requirement:**

    Run metal detector test on all finished units:

    **✅ PASS** (pass_qty):
    - No metal fragments detected
    - Safe for children
    - Proceed to Step 440: Physical QC

    **❌ FAIL** (fail_qty):
    - Metal detected (e.g., needle fragments, staples)
    - **CRITICAL REJECT** - Cannot proceed to packing
    - Step 435: Segregate units and investigate
    - QC Supervisor must review and determine action:
      - Repair/removal? → Rework
      - Cannot fix? → Scrap
    - Generate incident report

    Response indicates if test passed or if investigation required.

    **This is a compliance checkpoint for IKEA quality standards.**

    Requires: QC Inspector
    """
    return FinishingService.metal_detector_test(
        db=db,
        work_order_id=request.work_order_id,
        inspector_id=request.inspector_id,
        pass_qty=request.pass_qty,
        fail_qty=request.fail_qty,
        notes=request.notes
    )


@router.post("/physical-qc-check", response_model=dict)
async def physical_and_symmetry_check(
    work_order_id: int,
    inspector_id: int,
    pass_qty: Decimal,
    repair_qty: Decimal = 0,
    notes: str = None,
    current_user: User = Depends(require_permission("finishing.final_qc")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 440-445: Physical & Symmetry QC Check.

    Final visual inspection:
    - Check physical appearance (color, texture, seams)
    - Verify symmetry (ears equal, limbs proportional)
    - Inspect for defects

    **Two Outcomes:**
    1. **PASS** → Proceed to Step 450: Conversion to FG
    2. **REPAIR** → Step 445: Cleaning/adjustments, then re-check

    Requires: QC Inspector
    """
    return FinishingService.physical_qc_check(
        db=db,
        work_order_id=work_order_id,
        inspector_id=inspector_id,
        pass_qty=pass_qty,
        repair_qty=repair_qty,
        notes=notes
    )


@router.post("/convert-to-fg", response_model=dict)
async def convert_wip_to_finish_good(
    request: ConversionRequest,
    current_user: User = Depends(require_permission("finishing.convert_to_fg")),
    db: Session = Depends(get_db)
) -> dict:
    """**POST** - Step 450: CONVERSION to Finish Good Code.

    **Critical Step - Product Becomes FG:**

    Transforms internal WIP code → External IKEA article code

    Example:
    - FROM: `WIP-FIN-SHARK-001` (internal tracking code)
    - TO: `BLAHAJ-100` (IKEA customer-facing code)

    **This marks the point where:**
    ✅ Product is complete and ready
    ✅ Conversion to FG inventory
    ✅ Next step: Packing & sorting by destination

    Response includes:
    - Batch number
    - Conversion timestamp
    - Next step reference

    **Next:** Step 460 - Packing instructions & sortation

    Requires: SPV Finishing

    """
    # Get product IDs from codes
    from app.core.models.products import Product

    wip_product = db.query(Product).filter(Product.code == request.wip_code).first()
    fg_product = db.query(Product).filter(Product.code == request.fg_code).first()

    if not wip_product or not fg_product:
        raise HTTPException(status_code=404, detail="Product code not found")

    return FinishingService.convert_wip_to_fg(
        db=db,
        work_order_id=request.work_order_id,
        wip_product_id=wip_product.id,
        fg_product_id=fg_product.id,
        qty_converted=request.qty_converted,
        user_id=current_user.id
    )


@router.get("/status/{work_order_id}", response_model=FinishingWorkOrderResponse)
async def get_finishing_work_order_status(
    work_order_id: int,
    current_user: User = Depends(require_permission("finishing.view_status")),
    db: Session = Depends(get_db)
) -> FinishingWorkOrderResponse:
    """**GET** - Retrieve Current Finishing Work Order Status.

    Real-time status showing:
    - Current stage (stuffing/closing/QC/conversion)
    - Qty through each stage
    - QC results (metal test pass/fail)
    - Conversion status

    Accessible to: Operators, SPV, QC, Admin
    """
    wo = BaseProductionService.get_work_order(db, work_order_id)

    return FinishingWorkOrderResponse(
        id=wo.id,
        mo_id=wo.mo_id,
        wip_product_id=wo.product_id,
        fg_product_id=None,
        status=wo.status.value,
        input_qty=wo.input_qty,
        stuffed_qty=wo.input_qty,
        closed_qty=wo.input_qty,
        metal_test_pass=wo.output_qty,
        metal_test_fail=wo.reject_qty,
        converted_qty=wo.output_qty,
        started_at=wo.start_time,
        completed_at=wo.end_time
    )


@router.get("/pending", response_model=list[FinishingWorkOrderResponse])
async def get_pending_finishing_orders(
    current_user: User = Depends(require_permission("finishing.view_status")),
    db: Session = Depends(get_db)
) -> list[FinishingWorkOrderResponse]:
    """**GET** - List All Pending Finishing Work Orders.

    Returns work orders awaiting:
    - WIP transfer acceptance
    - Stuffing operation
    - Closing & grooming
    - Metal detector QC
    - Physical QC
    - Conversion to FG
    - Transfer to Packing
    """
    from app.core.models.manufacturing import Department, WorkOrder, WorkOrderStatus

    orders = db.query(WorkOrder).filter(
        WorkOrder.department == Department.FINISHING,
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.RUNNING])
    ).all()

    return [
        FinishingWorkOrderResponse(
            id=o.id,
            mo_id=o.mo_id,
            wip_product_id=o.product_id,
            fg_product_id=None,
            status=o.status.value,
            input_qty=o.input_qty,
            stuffed_qty=None,
            closed_qty=None,
            metal_test_pass=None,
            metal_test_fail=None,
            converted_qty=None,
            started_at=o.start_time,
            completed_at=o.end_time
        )
        for o in orders
    ]
