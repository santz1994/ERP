"""Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved.

Embroidery API Endpoints
Handles embroidery operations between cutting and sewing
"""


from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models.users import User
from app.core.permissions import ModuleName, Permission, require_permission
from app.modules.embroidery import EmbroideryService

router = APIRouter(prefix="/embroidery", tags=["Embroidery"])


# Pydantic Schemas
class EmbroideryOutputRequest(BaseModel):
    embroidered_qty: int = Field(..., gt=0, description="Quantity embroidered")
    reject_qty: int = Field(0, ge=0, description="Rejected quantity")
    design_type: str | None = Field(None, description="Embroidery design type")
    thread_colors: list[str] | None = Field(None, description="Thread colors used")


class WorkOrderResponse(BaseModel):
    id: int
    mo_id: int
    department: str
    status: str
    input_qty: int
    output_qty: int
    reject_qty: int
    start_time: str | None
    end_time: str | None
    metadata: dict | None

    class Config:
        from_attributes = True


class LineStatusResponse(BaseModel):
    line_id: str
    current_article: str | None
    is_occupied: bool
    department: str
    destination: str | None

    class Config:
        from_attributes = True


# Endpoints
@router.get("/work-orders", response_model=list[WorkOrderResponse])
def get_embroidery_work_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.EMBROIDERY, Permission.VIEW))
):
    """Get all work orders for Embroidery department.

    - **status**: Filter by status (Pending, Running, Finished)
    """
    service = EmbroideryService(db)
    work_orders = service.get_work_orders(status=status)
    return work_orders


@router.post("/work-order/{work_order_id}/start", response_model=WorkOrderResponse)
def start_embroidery_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.EMBROIDERY, Permission.EXECUTE))
):
    """Start embroidery work order.

    - Validates line clearance
    - Creates line occupancy record
    - Changes status to Running
    """
    try:
        service = EmbroideryService(db)
        work_order = service.start_work_order(work_order_id, current_user.id)
        return work_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/work-order/{work_order_id}/record-output", response_model=WorkOrderResponse)
def record_embroidery_output(
    work_order_id: int,
    request: EmbroideryOutputRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.EMBROIDERY, Permission.EXECUTE))
):
    """Record embroidery output with design details.

    - **embroidered_qty**: Number of pieces embroidered successfully
    - **reject_qty**: Number of pieces rejected
    - **design_type**: Type of embroidery design (e.g., "Logo", "Name Tag")
    - **thread_colors**: List of thread colors used
    """
    try:
        service = EmbroideryService(db)
        work_order = service.record_embroidery_output(
            work_order_id=work_order_id,
            embroidered_qty=request.embroidered_qty,
            reject_qty=request.reject_qty,
            design_type=request.design_type,
            thread_colors=request.thread_colors,
            user_id=current_user.id
        )
        return work_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/work-order/{work_order_id}/complete", response_model=WorkOrderResponse)
def complete_embroidery_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.EMBROIDERY, Permission.EXECUTE))
):
    """Complete embroidery work order.

    - Releases line occupancy
    - Changes status to Finished
    - Ready for transfer to Sewing
    """
    try:
        service = EmbroideryService(db)
        work_order = service.complete_embroidery(work_order_id, current_user.id)
        return work_order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/work-order/{work_order_id}/transfer")
def transfer_to_sewing(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.EMBROIDERY, Permission.EXECUTE))
):
    """Transfer embroidered items to Sewing (QT-09 Protocol).

    - Validates line clearance at Sewing
    - Creates transfer log
    - Creates new work order for Sewing department
    """
    try:
        service = EmbroideryService(db)
        transfer = service.transfer_to_sewing(work_order_id, current_user.id)
        return {
            "message": "Transfer to Sewing completed successfully",
            "transfer_id": transfer.id,
            "transfer_qty": transfer.transfer_qty
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/line-status", response_model=list[LineStatusResponse])
def get_line_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.EMBROIDERY, Permission.VIEW))
):
    """Get real-time status of all embroidery lines.

    Shows which lines are occupied and with which article
    """
    service = EmbroideryService(db)
    line_statuses = service.get_line_status()
    return line_statuses
