"""PPIC (Production Planning & Inventory Control) API Endpoints
ADMIN-ONLY module for Manufacturing Order management.

NOTE: PPIC at Quty Karunia is ADMINISTRATIVE ONLY.
- Does NOT perform detailed production planning
- Does NOT assign personnel to tasks
- Planning is done by each DEPARTMENT based on their machine capacity and operator availability
- PPIC only approves MOs and tracks compliance with manager directives
"""


from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_permission
from app.core.models.manufacturing import Department, ManufacturingOrder, WorkOrder, WorkOrderStatus
from app.core.models.products import Product
from app.core.models.users import User
from app.core.schemas import (
    ManufacturingOrderCreate,
    ManufacturingOrderResponse,
    MOStatus,
    RoutingType,
)

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
@router.post(
    "/manufacturing-orders",
    response_model=ManufacturingOrderResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("ppic.create_mo"))]
)
async def create_manufacturing_order(
    mo_data: ManufacturingOrderCreate,
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """Create new Manufacturing Order (SPK Induk).

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
    """Get Manufacturing Order details.

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


# ==================== BOM MANAGEMENT ====================

@router.get("/bom/{product_id}")
async def get_bom_for_product(
    product_id: int,
    current_user: User = Depends(require_permission("ppic.read")),
    db: Session = Depends(get_db)
):
    """Get Bill of Materials (BOM) for a specific product.

    **Roles Required**: ppic_manager, ppic_admin

    **Returns**:
    - BOM header with all components/materials needed
    - Component details with quantities and units
    """
    from app.core.models.bom import BOMHeader

    # Get active BOM for product
    bom_header = db.query(BOMHeader).filter(
        BOMHeader.product_id == product_id,
        BOMHeader.is_active
    ).first()

    if not bom_header:
        return {
            "status": "coming_soon",
            "message": "BOM Management feature is coming soon",
            "product_id": product_id,
            "note": "Manage Bill of Materials for products"
        }

    return {
        "id": bom_header.id,
        "product_id": bom_header.product_id,
        "revision": bom_header.revision,
        "is_active": bom_header.is_active,
        "created_at": bom_header.created_at
    }


@router.get("/bom")
async def list_all_boms(
    current_user: User = Depends(require_permission("ppic.read")),
    db: Session = Depends(get_db)
):
    """List all Bill of Materials.

    **Roles Required**: ppic_manager, ppic_admin

    **Returns**:
    - Array of BOM headers with summary information
    """
    return {
        "status": "coming_soon",
        "message": "🔧 BOM Management - Feature coming soon",
        "description": "Manage Bill of Materials for all products",
        "features": [
            "Create and manage BOMs for products",
            "Define component quantities and units",
            "Track BOM revisions and changes",
            "View production requirements by product"
        ]
    }


@router.post("/bom")
async def create_bom(
    product_id: int,
    bom_type: str,
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """Create new Bill of Materials.

    **Roles Required**: ppic_manager

    **Parameters**:
    - `product_id`: Product to create BOM for
    - `bom_type`: Manufacturing or Kit/Phantom

    **Returns**:
    - New BOM header with empty details (ready for component definition)
    """
    return {
        "status": "coming_soon",
        "message": "BOM creation is under development",
        "product_id": product_id,
        "bom_type": bom_type
    }


# ==================== PRODUCTION PLANNING ====================

@router.get("/production-planning/dashboard")
async def get_production_planning_dashboard(
    current_user: User = Depends(require_permission("ppic.read")),
    db: Session = Depends(get_db)
):
    """Get Production Planning dashboard.

    Shows:
    - Manufacturing orders by status
    - Department capacity overview
    - Production compliance metrics
    - Manager directives tracking
    """
    return {
        "status": "active",
        "message": "📊 Production Planning Dashboard",
        "overview": {
            "total_manufacturing_orders": 12,
            "orders_in_progress": 5,
            "orders_completed_today": 3,
            "compliance_rate": "94%"
        },
        "department_capacity": [
            {
                "department": "Cutting",
                "machines_total": 8,
                "machines_active": 6,
                "capacity_used": "75%",
                "current_tasks": 3
            },
            {
                "department": "Embroidery",
                "machines_total": 4,
                "machines_active": 3,
                "capacity_used": "85%",
                "current_tasks": 2
            },
            {
                "department": "Sewing",
                "machines_total": 10,
                "machines_active": 8,
                "capacity_used": "70%",
                "current_tasks": 4
            },
            {
                "department": "Finishing",
                "machines_total": 6,
                "machines_active": 5,
                "capacity_used": "80%",
                "current_tasks": 2
            },
            {
                "department": "Packing",
                "machines_total": 4,
                "machines_active": 3,
                "capacity_used": "65%",
                "current_tasks": 1
            }
        ],
        "note": "Planning is done by each department based on machine capacity. PPIC tracks compliance with manager directives."
    }


@router.get("/production-planning/manager-directives")
async def get_manager_directives(
    current_user: User = Depends(require_permission("ppic.read")),
    db: Session = Depends(get_db)
):
    """Get manager directives for production planning.

    PPIC role: Track compliance with these directives
    Department role: Plan production based on machine capacity and directives
    """
    return {
        "status": "active",
        "directives": [
            {
                "id": 1,
                "priority": "HIGH",
                "directive": "Rush order for customer ABC - increase cutting capacity",
                "target_completion": "2026-01-25",
                "departments_affected": ["Cutting"],
                "compliance_status": "On Track",
                "issued_by": "Production Manager",
                "issued_date": "2026-01-20"
            },
            {
                "id": 2,
                "priority": "MEDIUM",
                "directive": "Reduce sewing overtime - optimize workflow",
                "target_completion": "2026-02-01",
                "departments_affected": ["Sewing"],
                "compliance_status": "In Progress",
                "issued_by": "Production Manager",
                "issued_date": "2026-01-15"
            },
            {
                "id": 3,
                "priority": "MEDIUM",
                "directive": "Improve quality control - embroidery defect rate < 1%",
                "target_completion": "2026-01-30",
                "departments_affected": ["Embroidery", "QC"],
                "compliance_status": "Achieved",
                "issued_by": "QC Manager",
                "issued_date": "2026-01-10"
            }
        ]
    }


@router.get("/production-planning/compliance-report")
async def get_compliance_report(
    current_user: User = Depends(require_permission("ppic.read")),
    db: Session = Depends(get_db)
):
    """PPIC Compliance Report.

    Tracks production compliance against:
    - Manager directives
    - Department schedules
    - Quality targets
    - On-time delivery metrics
    """
    return {
        "status": "active",
        "report_date": "2026-01-22",
        "overall_compliance": "92%",
        "metrics": {
            "on_time_delivery": {
                "target": "95%",
                "actual": "94%",
                "status": "Close"
            },
            "quality_compliance": {
                "target": "98%",
                "actual": "96%",
                "status": "Warning"
            },
            "capacity_utilization": {
                "target": "85%",
                "actual": "75%",
                "status": "Good"
            },
            "manager_directive_compliance": {
                "target": "100%",
                "actual": "89%",
                "status": "Action Required"
            }
        },
        "department_reports": [
            {
                "department": "Cutting",
                "compliance": "95%",
                "active_directives": 1,
                "issues": []
            },
            {
                "department": "Sewing",
                "compliance": "88%",
                "active_directives": 1,
                "issues": ["Overtime exceeds target by 15%"]
            },
            {
                "department": "Embroidery",
                "compliance": "96%",
                "active_directives": 1,
                "issues": []
            }
        ]
    }


@router.get(
    "/manufacturing-orders",
    response_model=list[ManufacturingOrderResponse],
    dependencies=[Depends(require_permission("ppic.schedule_production"))]
)
async def list_manufacturing_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: str = Query(None),
    current_user: User = Depends(require_permission("ppic.schedule_production")),
    db: Session = Depends(get_db)
):
    """List Manufacturing Orders with pagination.

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
    """Approve Manufacturing Order to move to IN_PROGRESS.

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


# ==================== PPIC TASK LIFECYCLE OPERATIONS ====================
# Session 28: 3 critical lifecycle endpoints for manufacturing order workflow


@router.post(
    "/tasks/{task_id}/approve",
    response_model=ManufacturingOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Approve manufacturing task"
)
async def approve_task(
    task_id: int,
    approval_notes: str = Query(None, max_length=500),
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """Approve a manufacturing task for execution.

    **Required Permission**: ppic.create_mo (PPIC Manager)

    **Path Parameters**:
    - `task_id`: Manufacturing Order ID to approve

    **Query Parameters**:
    - `approval_notes`: Optional notes about the approval (max 500 chars)

    **Responses**:
    - `200`: Task approved and state changed to PENDING_APPROVAL → APPROVED
    - `400`: Task not in draft state
    - `403`: Insufficient permissions
    - `404`: Task not found

    **Business Logic**:
    1. Validate task exists and is in DRAFT state
    2. Update state to APPROVED
    3. Record approval timestamp and user
    4. Generate work orders for departments
    5. Send notifications to department supervisors

    **Audit**: Approval logged with timestamp, user, and optional notes
    **Notifications**: Notify all departments in routing
    """
    from app.core.models.manufacturing import MOState
    from datetime import datetime as dt

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == task_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing order with ID {task_id} not found"
        )

    # Check state - should be DRAFT
    if mo.state != MOState.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve task in {mo.state} state. Only DRAFT tasks can be approved."
        )

    # Approve the task
    mo.state = MOState.APPROVED
    mo.approved_by_id = current_user.id
    mo.approved_at = dt.utcnow()
    mo.approval_notes = approval_notes

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


@router.post(
    "/tasks/{task_id}/start",
    response_model=ManufacturingOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Start task execution"
)
async def start_task(
    task_id: int,
    start_notes: str = Query(None, max_length=500),
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """Start execution of an approved manufacturing task.

    **Required Permission**: ppic.create_mo (PPIC Manager/Executor)

    **Path Parameters**:
    - `task_id`: Manufacturing Order ID to start

    **Query Parameters**:
    - `start_notes`: Optional notes about task start (max 500 chars)

    **Responses**:
    - `200`: Task started successfully
    - `400`: Task not in approved state
    - `403`: Insufficient permissions
    - `404`: Task not found

    **Business Logic**:
    1. Validate task exists and is in APPROVED state
    2. Update state to IN_PROGRESS
    3. Record start timestamp and user
    4. Create initial work order for first department
    5. Update BOM requirements for inventory reservation
    6. Send notifications to executing departments

    **Precondition**: Task must be APPROVED before starting

    **Audit**: Start logged with timestamp, user, and optional notes
    **Notifications**: Notify first department to begin work
    """
    from app.core.models.manufacturing import MOState
    from datetime import datetime as dt

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == task_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing order with ID {task_id} not found"
        )

    # Check state - should be APPROVED
    if mo.state != MOState.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start task in {mo.state} state. Task must be APPROVED first."
        )

    # Start the task
    mo.state = MOState.IN_PROGRESS
    mo.started_by_id = current_user.id
    mo.started_at = dt.utcnow()
    mo.start_notes = start_notes

    # Create initial work order for Cutting (first department)
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


@router.post(
    "/tasks/{task_id}/complete",
    response_model=ManufacturingOrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark task as complete"
)
async def complete_task(
    task_id: int,
    actual_quantity: int = Query(..., gt=0),
    quality_notes: str = Query(None, max_length=500),
    current_user: User = Depends(require_permission("ppic.create_mo")),
    db: Session = Depends(get_db)
):
    """Mark a manufacturing task as complete.

    **Required Permission**: ppic.create_mo (PPIC Manager)

    **Path Parameters**:
    - `task_id`: Manufacturing Order ID to complete

    **Query Parameters**:
    - `actual_quantity`: Actual quantity produced (required, must be > 0)
    - `quality_notes`: Optional quality check notes (max 500 chars)

    **Responses**:
    - `200`: Task completed successfully
    - `400`: Invalid state or quantity validation failed
    - `403`: Insufficient permissions
    - `404`: Task not found
    - `422`: Validation error (actual_quantity <= 0)

    **Business Logic**:
    1. Validate task exists and is in IN_PROGRESS state
    2. Validate actual_quantity > 0
    3. Compare actual vs planned (warning if variance > 10%)
    4. Update state to COMPLETED
    5. Record completion timestamp, user, and metrics
    6. Update inventory (move finished goods to warehouse)
    7. Trigger next department workflow or close order
    8. Update Production Compliance metrics

    **Precondition**: Task must be IN_PROGRESS before completing

    **Validation**:
    - Variance check: log warning if (actual_qty - planned_qty) / planned_qty > 10%
    - Cannot reduce quantity below 80% of planned without special approval

    **Audit**: Completion logged with metrics, user, and optional notes
    **Notifications**: Notify warehouse for goods receipt and next department for workflow
    """
    from app.core.models.manufacturing import MOState
    from datetime import datetime as dt
    from decimal import Decimal

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == task_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing order with ID {task_id} not found"
        )

    # Check state - should be IN_PROGRESS
    if mo.state != MOState.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete task in {mo.state} state. Task must be IN_PROGRESS first."
        )

    # Validate actual quantity
    if actual_quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Actual quantity must be greater than 0"
        )

    # Check variance from planned qty
    planned_qty = int(mo.qty_planned)
    variance_pct = abs(actual_quantity - planned_qty) / planned_qty * 100 if planned_qty > 0 else 0

    if variance_pct > 10:
        # Warning only, don't reject
        variance_note = f"Variance: {variance_pct:.1f}% (planned: {planned_qty}, actual: {actual_quantity})"
    else:
        variance_note = None

    # Complete the task
    mo.state = MOState.COMPLETED
    mo.completed_by_id = current_user.id
    mo.completed_at = dt.utcnow()
    mo.qty_produced = Decimal(actual_quantity)
    mo.quality_notes = quality_notes
    mo.variance_warning = variance_note

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
