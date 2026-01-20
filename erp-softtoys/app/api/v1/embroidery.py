"""
Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved

Embroidery API Endpoints
Handles embroidery operations between cutting and sewing
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models.users import User
from app.modules.embroidery import EmbroideryService

router = APIRouter(prefix="/embroidery", tags=["Embroidery"])


# Pydantic Schemas
class EmbroideryOutputRequest(BaseModel):
    embroidered_qty: int = Field(..., gt=0, description="Quantity embroidered")
    reject_qty: int = Field(0, ge=0, description="Rejected quantity")
    design_type: Optional[str] = Field(None, description="Embroidery design type")
    thread_colors: Optional[List[str]] = Field(None, description="Thread colors used")


class WorkOrderResponse(BaseModel):
    id: int
    mo_id: int
    department: str
    status: str
    input_qty: int
    output_qty: int
    reject_qty: int
    start_time: Optional[str]
    end_time: Optional[str]
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class LineStatusResponse(BaseModel):
    line_id: str
    current_article: Optional[str]
    is_occupied: bool
    department: str
    destination: Optional[str]

    class Config:
        from_attributes = True


# Endpoints
@router.get("/work-orders", response_model=List[WorkOrderResponse])
def get_embroidery_work_orders(
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all work orders for Embroidery department
    
    - **status**: Filter by status (Pending, Running, Finished)
    """
    service = EmbroideryService(db)
    work_orders = service.get_work_orders(status=status)
    return work_orders


@router.post("/work-order/{work_order_id}/start", response_model=WorkOrderResponse)
def start_embroidery_work_order(
    work_order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start embroidery work order
    
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
    current_user: User = Depends(get_current_user)
):
    """
    Record embroidery output with design details
    
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
    current_user: User = Depends(get_current_user)
):
    """
    Complete embroidery work order
    
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
    current_user: User = Depends(get_current_user)
):
    """
    Transfer embroidered items to Sewing (QT-09 Protocol)
    
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


@router.get("/line-status", response_model=List[LineStatusResponse])
def get_line_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get real-time status of all embroidery lines
    
    Shows which lines are occupied and with which article
    """
    service = EmbroideryService(db)
    line_statuses = service.get_line_status()
    return line_statuses
