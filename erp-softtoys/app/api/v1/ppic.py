"""
PPIC (Production Planning & Inventory Control) API Endpoints
ADMIN-ONLY module for Manufacturing Order management

NOTE: PPIC at Quty Karunia is ADMINISTRATIVE ONLY.
- Does NOT perform detailed production planning
- Does NOT assign personnel to tasks
- Planning is done by each DEPARTMENT based on their machine capacity and operator availability
- PPIC only approves MOs and tracks compliance with manager directives
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.core.schemas import (
    ManufacturingOrderCreate, ManufacturingOrderResponse,
    RoutingType, MOStatus
)
from app.core.dependencies import get_db, require_permission
from app.core.models.users import User
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, Department, WorkOrderStatus
from app.core.models.products import Product


router = APIRouter(
    prefix="/ppic",
    tags=["PPIC - Production Planning"],
)


@router.post(
    "/manufacturing-order",
    response_model=ManufacturingOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("ppic.create_mo"))]
)
async def create_manufacturing_order(
    mo_data: ManufacturingOrderCreate,
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """
    Create new Manufacturing Order (SPK Induk)
    
    **Roles Required**: ppic_manager
    
    **Request Body**:
    - `so_line_id`: Sales order line ID
    - `product_id`: WIP/FG product to manufacture
    - `qty_planned`: Planned quantity to produce
    - `routing_type`: Route 1 (Full), Route 2 (Direct), Route 3 (Subcon)
    - `batch_number`: Batch identifier for traceability
    
    **Responses**:
    - `201`: Manufacturing order created
    - `400`: Invalid product or sales order
    - `403`: Insufficient permissions
    - `422`: Validation error
    
    **Business Logic**:
    1. Validate product exists and is WIP or Finish Good type
    2. Validate routing type matches product requirements
    3. Create MO in DRAFT state
    4. Return created MO with system-generated ID
    """
    # Validate product exists
    product = db.query(Product).filter(Product.id == mo_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found"
        )
    
    # Validate product type for manufacturing
    from app.core.models.products import ProductType
    if product.type not in [ProductType.WIP, ProductType.FINISH_GOOD]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot manufacture {product.type}. Only WIP or Finish Good allowed."
        )
    
    # Check if batch_number already exists
    existing_batch = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.batch_number == mo_data.batch_number
    ).first()
    if existing_batch:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch number already exists"
        )
    
    # Create manufacturing order
    from app.core.models.manufacturing import MOState
    new_mo = ManufacturingOrder(
        so_line_id=mo_data.so_line_id,
        product_id=mo_data.product_id,
        qty_planned=mo_data.qty_planned,
        qty_produced=0,
        routing_type=mo_data.routing_type.value,
        batch_number=mo_data.batch_number,
        state=MOState.DRAFT,
        created_by_id=current_user.id
    )
    
    db.add(new_mo)
    db.commit()
    db.refresh(new_mo)
    
    return ManufacturingOrderResponse(
        id=new_mo.id,
        so_line_id=new_mo.so_line_id,
        product_id=new_mo.product_id,
        qty_planned=new_mo.qty_planned,
        qty_produced=new_mo.qty_produced,
        routing_type=RoutingType(new_mo.routing_type),
        batch_number=new_mo.batch_number,
        state=MOStatus(new_mo.state),
        created_at=new_mo.created_at
    )


@router.get(
    "/manufacturing-order/{mo_id}",
    response_model=ManufacturingOrderResponse,
    dependencies=[Depends(require_permission("ppic.view_mo"))]
)
async def get_manufacturing_order(
    mo_id: int,
    current_user: User = Depends(require_permission("ppic.view_mo")),
    db: Session = Depends(get_db)
):
    """
    Get Manufacturing Order details
    
    **Roles Required**: ppic_manager
    
    **Path Parameters**:
    - `mo_id`: Manufacturing Order ID
    
    **Responses**:
    - `200`: Manufacturing order details
    - `403`: Insufficient permissions
    - `404`: Manufacturing order not found
    """
    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    return ManufacturingOrderResponse(
        id=mo.id,
        so_line_id=mo.so_line_id,
        product_id=mo.product_id,
        qty_planned=mo.qty_planned,
        qty_produced=mo.qty_produced,
        routing_type=RoutingType(mo.routing_type),
        batch_number=mo.batch_number,
        state=MOStatus(mo.state),
        created_at=mo.created_at
    )


@router.get(
    "/manufacturing-orders",
    response_model=List[ManufacturingOrderResponse],
    dependencies=[Depends(require_permission("ppic.schedule_production"))]
)
async def list_manufacturing_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    current_user: User = Depends(require_permission("ppic.schedule_production")),
    db: Session = Depends(get_db)
):
    """
    List Manufacturing Orders with pagination
    
    **Roles Required**: ppic_manager
    
    **Query Parameters**:
    - `skip`: Number of records to skip (default: 0)
    - `limit`: Number of records to return (default: 100, max: 1000)
    - `status`: Filter by status (DRAFT, IN_PROGRESS, DONE, CANCELLED)
    
    **Responses**:
    - `200`: List of manufacturing orders
    - `403`: Insufficient permissions
    """
    query = db.query(ManufacturingOrder)
    
    # Apply status filter
    if status:
        query = query.filter(ManufacturingOrder.state == status)
    
    mos = query.offset(skip).limit(limit).all()
    
    return [
        ManufacturingOrderResponse(
            id=mo.id,
            so_line_id=mo.so_line_id,
            product_id=mo.product_id,
            qty_planned=mo.qty_planned,
            qty_produced=mo.qty_produced,
            routing_type=RoutingType(mo.routing_type),
            batch_number=mo.batch_number,
            state=MOStatus(mo.state),
            created_at=mo.created_at
        )
        for mo in mos
    ]


@router.post(
    "/manufacturing-order/{mo_id}/approve",
    response_model=ManufacturingOrderResponse,
    dependencies=[Depends(require_permission("ppic.approve_mo"))]
)
async def approve_manufacturing_order(
    mo_id: int,
    current_user: User = Depends(require_permission("ppic.approve_mo")),
    db: Session = Depends(get_db)
):
    """
    Approve Manufacturing Order to move to IN_PROGRESS
    
    **Roles Required**: ppic_manager
    
    **Path Parameters**:
    - `mo_id`: Manufacturing Order ID
    
    **Responses**:
    - `200`: MO approved and state updated to IN_PROGRESS
    - `400`: MO not in DRAFT state
    - `403`: Insufficient permissions
    - `404`: MO not found
    
    **Business Logic**:
    1. Validate MO is in DRAFT state
    2. Change state to IN_PROGRESS
    3. Create work orders for each department in routing
    4. Return updated MO
    """
    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Manufacturing order not found"
        )
    
    from app.core.models.manufacturing import MOState
    if mo.state != MOState.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve MO in {mo.state} state. Only DRAFT MO can be approved."
        )
    
    # Approve MO
    mo.state = MOState.IN_PROGRESS
    mo.approved_by_id = current_user.id
    
    # Create initial work order for Cutting (first step in all routes)
    from app.core.models.manufacturing import Department, WorkOrderStatus
    initial_wo = WorkOrder(
        mo_id=mo.id,
        department=Department.CUTTING,
        status=WorkOrderStatus.PENDING,
        input_qty=mo.qty_planned
    )
    
    db.add(initial_wo)
    db.commit()
    db.refresh(mo)
    
    return ManufacturingOrderResponse(
        id=mo.id,
        so_line_id=mo.so_line_id,
        product_id=mo.product_id,
        qty_planned=mo.qty_planned,
        qty_produced=mo.qty_produced,
        routing_type=RoutingType(mo.routing_type),
        batch_number=mo.batch_number,
        state=MOStatus(mo.state),
        created_at=mo.created_at
    )
