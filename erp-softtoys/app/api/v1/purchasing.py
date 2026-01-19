"""
Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved

Purchasing API Endpoints
Handles purchase orders, supplier management, material receiving
"""

from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.models.users import User
from app.modules.purchasing import PurchasingService

router = APIRouter(prefix="/purchasing", tags=["Purchasing"])


# Pydantic Schemas
class POItemRequest(BaseModel):
    product_id: int = Field(..., description="Raw material product ID")
    quantity: int = Field(..., gt=0, description="Order quantity")
    unit_price: float = Field(..., gt=0, description="Unit price in IDR")


class CreatePORequest(BaseModel):
    po_number: str = Field(..., description="PO number")
    supplier_id: int = Field(..., description="Supplier ID")
    order_date: date = Field(..., description="Order date")
    expected_date: date = Field(..., description="Expected delivery date")
    items: List[POItemRequest] = Field(..., description="PO items")


class ReceiveItemRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Received quantity")
    lot_number: Optional[str] = Field(None, description="Lot/Batch number")


class ReceivePORequest(BaseModel):
    received_items: List[ReceiveItemRequest] = Field(..., description="Received items")
    location_id: int = Field(1, description="Warehouse location ID")


class CancelPORequest(BaseModel):
    reason: str = Field(..., description="Cancellation reason")


class PurchaseOrderResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    order_date: date
    expected_date: date
    status: str
    total_amount: float
    currency: str
    approved_by: Optional[int]
    approved_at: Optional[str]
    received_by: Optional[int]
    received_at: Optional[str]
    metadata: Optional[dict]

    class Config:
        from_attributes = True


class SupplierPerformanceResponse(BaseModel):
    supplier_id: int
    total_purchase_orders: int
    completed_orders: int
    on_time_delivery: int
    on_time_rate: float
    completion_rate: float


# Endpoints
@router.get("/purchase-orders", response_model=List[PurchaseOrderResponse])
def get_purchase_orders(
    status: Optional[str] = None,
    supplier_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all purchase orders with optional filters
    
    - **status**: Filter by status (Draft, Sent, Received, Done, Cancelled)
    - **supplier_id**: Filter by supplier
    """
    service = PurchasingService(db)
    pos = service.get_purchase_orders(status=status, supplier_id=supplier_id)
    return pos


@router.post("/purchase-order", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(
    request: CreatePORequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new purchase order for raw materials
    
    - **po_number**: Unique PO number
    - **supplier_id**: Supplier/vendor ID
    - **order_date**: Date when PO is created
    - **expected_date**: Expected delivery date
    - **items**: List of materials to purchase with quantities and prices
    """
    try:
        service = PurchasingService(db)
        po = service.create_purchase_order(
            po_number=request.po_number,
            supplier_id=request.supplier_id,
            order_date=request.order_date,
            expected_date=request.expected_date,
            items=[item.dict() for item in request.items],
            user_id=current_user.id
        )
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/purchase-order/{po_id}/approve", response_model=PurchaseOrderResponse)
def approve_purchase_order(
    po_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Approve purchase order (Manager only)
    
    Changes status from Draft to Sent
    """
    try:
        service = PurchasingService(db)
        po = service.approve_purchase_order(po_id, current_user.id)
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/purchase-order/{po_id}/receive", response_model=PurchaseOrderResponse)
def receive_purchase_order(
    po_id: int,
    request: ReceivePORequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Receive materials from purchase order
    
    - Creates stock lots for traceability
    - Updates inventory quantities (FIFO)
    - Records stock movements
    - Changes PO status to Received
    """
    try:
        service = PurchasingService(db)
        po = service.receive_purchase_order(
            po_id=po_id,
            received_items=[item.dict() for item in request.received_items],
            user_id=current_user.id,
            location_id=request.location_id
        )
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/purchase-order/{po_id}/cancel", response_model=PurchaseOrderResponse)
def cancel_purchase_order(
    po_id: int,
    request: CancelPORequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel purchase order
    
    Can only cancel Draft or Sent POs, not Received/Done
    """
    try:
        service = PurchasingService(db)
        po = service.cancel_purchase_order(po_id, request.reason, current_user.id)
        return po
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/supplier/{supplier_id}/performance", response_model=SupplierPerformanceResponse)
def get_supplier_performance(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get supplier performance metrics
    
    - Total purchase orders
    - Completion rate
    - On-time delivery rate
    """
    service = PurchasingService(db)
    performance = service.get_supplier_performance(supplier_id)
    return performance
