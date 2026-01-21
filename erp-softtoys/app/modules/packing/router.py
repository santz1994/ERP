"""
Packing Module API Endpoints
Final production stage: Sort → Package → Generate shipping marks
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List

from app.core.dependencies import get_db, require_permission
from app.core.models.users import User
from app.core.base_production_service import BaseProductionService
from app.modules.packing.models import (
    SortByDestinationRequest, PackageIntoCartonRequest,
    GenerateShippingMarkRequest, PackingWorkOrderResponse, ShippingMarkResponse
)
from app.modules.packing.services import PackingService


router = APIRouter(prefix="/production/packing", tags=["Packing Module"])


@router.post("/sort-by-destination", response_model=dict)
async def sort_by_destination_and_week(
    request: SortByDestinationRequest,
    current_user: User = Depends(require_permission("packing.sort_by_destination")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 470: Sort by Week & Destination
    
    Categorize finished goods:
    - By destination country (US, DE, JP, etc.)
    - By delivery week number
    - Prepare for cartonization
    
    **Purpose:**
    - Ensures each shipment contains only single destination
    - Facilitates logistics planning (separate containers per destination)
    - IKEA requirement for order fulfillment accuracy
    
    Response includes destination, week, and next step.
    
    Requires: Operator_Packing or SPV Packing
    """
    return PackingService.sort_by_destination_and_week(
        db=db,
        work_order_id=request.work_order_id,
        qty_sorted=request.qty_sorted,
        destination=request.destination,
        week_number=request.week_number
    )


@router.post("/package-cartons", response_model=dict)
async def package_into_cartons(
    request: PackageIntoCartonRequest,
    current_user: User = Depends(require_permission("packing.pack_product")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Step 480: Package into Cartons
    
    Physical packaging process:
    1. **Wrap each item** in polybag (moisture protection, handling safety)
    2. **Place polybag-wrapped items** into shipping carton
    3. **Fill carton** with packing material if needed (foam, paper)
    4. **Seal carton** and prepare for labeling
    
    **Input:**
    - `pcs_per_carton`: Standard carton configuration (typically 12, 24, or 36)
    - `num_cartons`: Total cartons to be used for this batch
    
    **Validation:**
    - System calculates: Qty ÷ Pcs_per_carton = required cartons
    - Verifies sufficient cartons provided
    
    Response includes fill rate and next step.
    
    **Next:** Step 490 - Generate Shipping Marks
    
    Requires: Operator_Packing
    """
    return PackingService.package_into_cartons(
        db=db,
        work_order_id=request.work_order_id,
        qty_packaged=request.qty_packaged,
        pcs_per_carton=request.pcs_per_carton,
        num_cartons=request.num_cartons,
        notes=request.notes
    )


@router.post("/shipping-mark", response_model=ShippingMarkResponse)
async def generate_shipping_mark(
    request: GenerateShippingMarkRequest,
    current_user: User = Depends(require_permission("packing.label_carton")),
    db: Session = Depends(get_db)
) -> ShippingMarkResponse:
    """
    **POST** - Step 490: Generate Shipping Mark
    
    Create barcode label for carton:
    
    **Shipping Mark Contains:**
    - **Article Code** (IKEA code, e.g., BLAHAJ-100)
    - **Qty in Carton** (e.g., 12 pieces)
    - **Destination** (Country code, e.g., US, DE, JP)
    - **Delivery Week** (e.g., Week 6)
    - **Batch/PO Reference** (Traceability)
    - **Carton Sequence** (1 of 8, 2 of 8, etc.)
    
    **Output:**
    - **Barcode Number** (scannable for logistics)
    - **QR Code** (Optional - links to batch details)
    - **Label Format** (Ready to print on standard thermal printer)
    
    **Process:**
    1. ✅ SPV approves carton contents
    2. ✅ System generates unique mark ID
    3. ✅ Print label on thermal printer
    4. ✅ Apply label to top/front of carton
    5. ✅ Scan label to confirm labeling complete
    
    **Purpose:**
    - Logistics tracking & scanning
    - Receiving verification at IKEA warehouse
    - Traceability from production to customer
    
    Response includes barcode, label data, and print instructions.
    
    Requires: SPV Packing
    """
    mark_data = PackingService.generate_shipping_mark(
        db=db,
        work_order_id=request.work_order_id,
        carton_number=request.carton_number,
        fg_code=request.fg_code,
        qty_in_carton=request.qty_in_carton,
        destination=request.destination,
        week_number=request.week_number,
        user_id=current_user.id
    )
    
    return ShippingMarkResponse(
        shipping_mark_id=mark_data["shipping_mark_id"],
        barcode=mark_data["barcode_number"],
        carton_label=str(mark_data["carton_label"]),
        fg_code=request.fg_code,
        qty=request.qty_in_carton,
        destination=request.destination,
        week=request.week_number,
        batch_number=mark_data.get("batch"),
        generated_at=datetime.utcnow(),
        qr_code_url=None
    )


@router.post("/complete", response_model=dict)
async def complete_packing_operation(
    work_order_id: int,
    total_cartons: int,
    total_pcs: Decimal,
    current_user: User = Depends(require_permission("packing.complete_operation")),
    db: Session = Depends(get_db)
) -> dict:
    """
    **POST** - Complete Packing Operation
    
    Mark work order as complete after all cartons labeled and ready:
    - Final qty confirmation (must match original FG qty)
    - Update inventory to FG warehouse
    - Prepare shipping documentation
    
    **Next Stage:** Logistics & Transfer to Finish Good Warehouse
    
    Response includes batch number and next steps.
    
    Requires: SPV Packing
    """
    from datetime import datetime
    
    return PackingService.complete_packing(
        db=db,
        work_order_id=work_order_id,
        total_cartons=total_cartons,
        total_pcs=total_pcs
    )


@router.get("/status/{work_order_id}", response_model=PackingWorkOrderResponse)
async def get_packing_work_order_status(
    work_order_id: int,
    current_user: User = Depends(require_permission("packing.view_status")),
    db: Session = Depends(get_db)
) -> PackingWorkOrderResponse:
    """
    **GET** - Retrieve Current Packing Work Order Status
    
    Real-time status showing:
    - Current stage (sorting/packaging/shipping marks)
    - Qty through each stage
    - Number of cartons
    - Start/completion times
    
    Accessible to: Operators, SPV, Admin
    """
    from app.core.models.manufacturing import WorkOrder
    
    wo = BaseProductionService.get_work_order(db, work_order_id)
    
    return PackingWorkOrderResponse(
        id=wo.id,
        mo_id=wo.mo_id,
        fg_product_id=wo.product_id,
        status=wo.status.value,
        input_qty=wo.input_qty,
        sorted_qty=wo.input_qty,
        packaged_qty=wo.output_qty,
        num_cartons=None,
        started_at=wo.start_time,
        completed_at=wo.end_time
    )


@router.get("/pending", response_model=List[PackingWorkOrderResponse])
async def get_pending_packing_orders(
    current_user: User = Depends(require_permission("packing.view_status")),
    db: Session = Depends(get_db)
) -> List[PackingWorkOrderResponse]:
    """
    **GET** - List All Pending Packing Work Orders
    
    Returns work orders awaiting:
    - Sorting by destination/week
    - Cartonization
    - Shipping mark generation
    - Final completion
    """
    from app.core.models.manufacturing import WorkOrder, Department, WorkOrderStatus
    
    orders = db.query(WorkOrder).filter(
        WorkOrder.department == Department.PACKING,
        WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.RUNNING])
    ).all()
    
    return [
        PackingWorkOrderResponse(
            id=o.id,
            mo_id=o.mo_id,
            fg_product_id=o.product_id,
            status=o.status.value,
            input_qty=o.input_qty,
            sorted_qty=None,
            packaged_qty=None,
            num_cartons=None,
            started_at=o.start_time,
            completed_at=o.end_time
        )
        for o in orders
    ]
