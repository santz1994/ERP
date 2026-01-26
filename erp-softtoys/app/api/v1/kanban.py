"""E-Kanban API Router
Digital kanban system for accessory/material requests.
"""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.base_production_service import BaseProductionService
from app.core.database import get_db
from app.core.models.kanban import KanbanCard, KanbanPriority, KanbanStatus
from app.core.models.products import Product
from app.core.models.users import User
from app.core.dependencies import require_permission
from app.core.permissions import ModuleName, Permission
from app.core.websocket import ws_manager

router = APIRouter(prefix="/kanban", tags=["E-Kanban"])


# ========== SCHEMAS ==========

class KanbanCardCreate(BaseModel):
    """Request schema for creating kanban card."""

    product_id: int
    qty_requested: int = Field(gt=0, description="Quantity must be positive")
    priority: KanbanPriority = KanbanPriority.NORMAL
    needed_by: datetime | None = None
    request_reason: str | None = None
    work_order_id: int | None = None


class KanbanCardResponse(BaseModel):
    """Response schema for kanban card."""

    id: int
    card_number: str
    requested_by_dept: str
    requested_at: datetime
    product_code: str
    product_name: str
    qty_requested: int
    qty_fulfilled: int
    priority: KanbanPriority
    status: KanbanStatus
    needed_by: datetime | None
    approved_at: datetime | None
    fulfilled_at: datetime | None

    class Config:
        from_attributes = True


class KanbanApprovalRequest(BaseModel):
    """Request schema for approving kanban."""

    approval_notes: str | None = None


class KanbanFulfillmentRequest(BaseModel):
    """Request schema for fulfilling kanban."""

    qty_fulfilled: int = Field(gt=0)
    fulfillment_notes: str | None = None


# ========== ENDPOINTS ==========

@router.post("/card", response_model=KanbanCardResponse)
async def create_kanban_card(
    request: KanbanCardCreate,
    current_user: User = Depends(require_permission(ModuleName.KANBAN, Permission.CREATE)),
    db: Session = Depends(get_db)
):
    """Create new E-Kanban card for material request.

    **Use Case**: Department needs materials/accessories

    **Example**: Packing department needs carton boxes
    ```json
    {
      "product_id": 123,
      "qty_requested": 500,
      "priority": "High",
      "needed_by": "2026-01-20T14:00:00",
      "request_reason": "Running low on carton boxes for Week 22 shipment"
    }
    ```

    **Process**:
    1. Create kanban card
    2. Notify warehouse team
    3. Wait for approval
    4. Warehouse fulfills request
    """
    # Verify product exists
    product = db.query(Product).filter(Product.id == request.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Generate card number
    card_count = db.query(KanbanCard).count()
    card_number = f"KAN-{datetime.now().strftime('%Y%m%d')}-{card_count + 1:04d}"

    # Create kanban card
    kanban = KanbanCard(
        card_number=card_number,
        requested_by_dept=current_user.department,
        requested_by_user_id=current_user.id,
        product_id=request.product_id,
        qty_requested=request.qty_requested,
        priority=request.priority,
        needed_by=request.needed_by,
        request_reason=request.request_reason,
        work_order_id=request.work_order_id,
        status=KanbanStatus.PENDING
    )

    db.add(kanban)
    db.commit()
    db.refresh(kanban)

    # Send real-time notification to warehouse
    await ws_manager.send_to_department(
        department="Warehouse",
        message={
            "type": "notification",
            "notification_type": "KANBAN_NEW_REQUEST",
            "severity": "INFO" if request.priority != KanbanPriority.URGENT else "WARNING",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "card_number": card_number,
                "product": product.name,
                "qty": request.qty_requested,
                "from_dept": current_user.department,
                "priority": request.priority.value
            }
        }
    )

    return KanbanCardResponse(
        id=kanban.id,
        card_number=kanban.card_number,
        requested_by_dept=kanban.requested_by_dept,
        requested_at=kanban.requested_at,
        product_code=product.code,
        product_name=product.name,
        qty_requested=kanban.qty_requested,
        qty_fulfilled=kanban.qty_fulfilled,
        priority=kanban.priority,
        status=kanban.status,
        needed_by=kanban.needed_by,
        approved_at=kanban.approved_at,
        fulfilled_at=kanban.fulfilled_at
    )


@router.get("/cards", response_model=list[KanbanCardResponse])
async def list_kanban_cards(
    status: KanbanStatus | None = None,
    department: str | None = None,
    priority: KanbanPriority | None = None,
    current_user: User = Depends(require_permission(ModuleName.KANBAN, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """List kanban cards with filters.

    **Filters**:
    - `status`: Filter by status (Pending, Approved, In Progress, Completed, Cancelled)
    - `department`: Filter by requesting department
    - `priority`: Filter by priority (Low, Normal, High, Urgent)

    **Role Access**:
    - Operators: See own department cards
    - Warehouse: See all cards
    - Admin/Supervisors: See all cards
    """
    query = db.query(KanbanCard)

    # Access control
    if current_user.role.value not in ['Admin', 'Warehouse Admin', 'PPIC Manager']:
        # Operators see only their department
        query = query.filter(KanbanCard.requested_by_dept == current_user.department)
    elif department:
        query = query.filter(KanbanCard.requested_by_dept == department)

    # Apply filters
    if status:
        query = query.filter(KanbanCard.status == status)
    if priority:
        query = query.filter(KanbanCard.priority == priority)

    cards = query.order_by(KanbanCard.requested_at.desc()).limit(100).all()

    result = []
    for card in cards:
        product = db.query(Product).filter(Product.id == card.product_id).first()
        result.append(KanbanCardResponse(
            id=card.id,
            card_number=card.card_number,
            requested_by_dept=card.requested_by_dept,
            requested_at=card.requested_at,
            product_code=product.code,
            product_name=product.name,
            qty_requested=card.qty_requested,
            qty_fulfilled=card.qty_fulfilled,
            priority=card.priority,
            status=card.status,
            needed_by=card.needed_by,
            approved_at=card.approved_at,
            fulfilled_at=card.fulfilled_at
        ))

    return result


@router.post("/card/{card_id}/approve")
async def approve_kanban_card(
    card_id: int,
    request: KanbanApprovalRequest,
    current_user: User = Depends(require_permission(ModuleName.KANBAN, Permission.APPROVE)),
    db: Session = Depends(get_db)
):
    """Approve kanban card (Warehouse Admin/Supervisor only).

    **Authorization**: Warehouse Admin, Supervisor, Admin
    """
    # Check role
    if current_user.role.value not in ['Admin', 'Warehouse Admin', 'SPV Warehouse']:
        raise HTTPException(
            status_code=403,
            detail="Only warehouse supervisors can approve kanban cards"
        )

    # Get kanban card
    kanban = BaseProductionService.get_kanban_card(db, card_id)

    if kanban.status != KanbanStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve card in status: {kanban.status.value}"
        )

    # Approve
    kanban.status = KanbanStatus.APPROVED
    kanban.approved_by_user_id = current_user.id
    kanban.approved_at = datetime.now()
    if request.approval_notes:
        kanban.fulfillment_notes = request.approval_notes

    db.commit()

    # Notify requester
    await ws_manager.send_to_department(
        department=kanban.requested_by_dept,
        message={
            "type": "notification",
            "notification_type": "KANBAN_APPROVED",
            "severity": "INFO",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "card_number": kanban.card_number,
                "approved_by": current_user.full_name
            }
        }
    )

    return {"message": "Kanban card approved", "card_number": kanban.card_number}


@router.post("/card/{card_id}/fulfill")
async def fulfill_kanban_card(
    card_id: int,
    request: KanbanFulfillmentRequest,
    current_user: User = Depends(require_permission(ModuleName.KANBAN, Permission.EXECUTE)),
    db: Session = Depends(get_db)
):
    """Fulfill kanban card (Warehouse team).

    **Process**: Mark materials as delivered to requesting department
    """
    # Check role
    if current_user.department != 'Warehouse' and current_user.role.value != 'Admin':
        raise HTTPException(
            status_code=403,
            detail="Only warehouse team can fulfill kanban cards"
        )

    kanban = BaseProductionService.get_kanban_card(db, card_id)

    if kanban.status not in [KanbanStatus.APPROVED, KanbanStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot fulfill card in status: {kanban.status.value}"
        )

    # Fulfill
    kanban.qty_fulfilled = request.qty_fulfilled
    kanban.status = KanbanStatus.COMPLETED
    kanban.fulfilled_by_user_id = current_user.id
    kanban.fulfilled_at = datetime.now()
    if request.fulfillment_notes:
        kanban.fulfillment_notes = request.fulfillment_notes

    db.commit()

    # Notify requester
    await ws_manager.send_to_department(
        department=kanban.requested_by_dept,
        message={
            "type": "notification",
            "notification_type": "KANBAN_FULFILLED",
            "severity": "INFO",
            "timestamp": datetime.now().isoformat(),
            "details": {
                "card_number": kanban.card_number,
                "qty_fulfilled": request.qty_fulfilled,
                "fulfilled_by": current_user.full_name
            }
        }
    )

    return {"message": "Kanban card fulfilled", "card_number": kanban.card_number}


@router.get("/dashboard/{department}")
async def kanban_dashboard(
    department: str,
    current_user: User = Depends(require_permission(ModuleName.KANBAN, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """Kanban board dashboard for department.

    **Returns**: Count of cards by status for visual kanban board
    """
    # Access control
    if current_user.department != department and current_user.role.value not in ['Admin', 'Warehouse Admin']:
        raise HTTPException(status_code=403, detail="Access denied to this department")

    # Count cards by status
    pending = db.query(KanbanCard).filter(
        and_(
            KanbanCard.requested_by_dept == department,
            KanbanCard.status == KanbanStatus.PENDING
        )
    ).count()

    approved = db.query(KanbanCard).filter(
        and_(
            KanbanCard.requested_by_dept == department,
            KanbanCard.status == KanbanStatus.APPROVED
        )
    ).count()

    in_progress = db.query(KanbanCard).filter(
        and_(
            KanbanCard.requested_by_dept == department,
            KanbanCard.status == KanbanStatus.IN_PROGRESS
        )
    ).count()

    # Recent completed (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    completed = db.query(KanbanCard).filter(
        and_(
            KanbanCard.requested_by_dept == department,
            KanbanCard.status == KanbanStatus.COMPLETED,
            KanbanCard.fulfilled_at >= week_ago
        )
    ).count()

    return {
        "department": department,
        "pending": pending,
        "approved": approved,
        "in_progress": in_progress,
        "completed_last_7_days": completed,
        "timestamp": datetime.now().isoformat()
    }
