"""
Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved

Finishgoods API Endpoints
Handles finished goods warehouse management and shipping
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models.users import User
from app.modules.finishgoods import FinishgoodsService

router = APIRouter(prefix="/finishgoods", tags=["Finishgoods"])


# Pydantic Schemas
class ReceiveFromPackingRequest(BaseModel):
    transfer_id: int = Field(..., description="Transfer ID from Packing")
    fg_location_id: int = Field(2, description="FG warehouse location ID")


class PrepareShipmentRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity to ship")
    destination: str = Field(..., description="Destination country/location")
    shipping_marks: List[str] = Field(..., description="Shipping marks/labels")


class ShipFinishgoodsRequest(BaseModel):
    product_id: int = Field(..., description="Product ID")
    quantity: int = Field(..., gt=0, description="Quantity to ship")


class InventoryItemResponse(BaseModel):
    product_id: int
    product_code: str
    product_name: str
    quantity_on_hand: int
    min_stock: int
    stock_status: str
    uom: str


class ShipmentReadyResponse(BaseModel):
    mo_id: int
    product_code: str
    product_name: str
    quantity_available: int
    quantity_reserved: int
    destination: str


class StockAgingResponse(BaseModel):
    product_code: str
    product_name: str
    received_date: str
    days_in_stock: int
    aging_category: str


# Endpoints
@router.get("/inventory", response_model=List[InventoryItemResponse])
def get_finishgoods_inventory(
    product_code: Optional[str] = None,
    low_stock_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get finished goods inventory with stock levels
    
    - **product_code**: Filter by product code (partial match)
    - **low_stock_only**: Show only products below minimum stock
    """
    service = FinishgoodsService(db)
    inventory = service.get_finished_goods_inventory(
        product_code=product_code,
        low_stock_only=low_stock_only
    )
    return inventory


@router.post("/receive-from-packing")
def receive_from_packing(
    request: ReceiveFromPackingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Receive finished goods from Packing department
    
    - Validates transfer from Packing
    - Creates stock movement
    - Updates FG inventory
    - Marks transfer as completed
    """
    try:
        service = FinishgoodsService(db)
        transfer = service.receive_from_packing(
            transfer_id=request.transfer_id,
            user_id=current_user.id,
            fg_location_id=request.fg_location_id
        )
        return {
            "message": "Finished goods received successfully",
            "transfer_id": transfer.id,
            "quantity": transfer.transfer_qty,
            "status": transfer.status
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/prepare-shipment")
def prepare_shipment(
    request: PrepareShipmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Prepare finished goods for shipment
    
    - Validates stock availability
    - Reserves stock for shipment
    - Creates shipping preparation record
    """
    try:
        service = FinishgoodsService(db)
        shipment = service.prepare_shipment(
            product_id=request.product_id,
            quantity=request.quantity,
            destination=request.destination,
            shipping_marks=request.shipping_marks,
            user_id=current_user.id
        )
        return shipment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/ship")
def ship_finishgoods(
    request: ShipFinishgoodsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Ship finished goods (reduce FG inventory)
    
    - Creates outbound stock movement
    - Updates FG inventory
    - Releases reserved stock
    """
    try:
        service = FinishgoodsService(db)
        result = service.ship_finishgoods(
            product_id=request.product_id,
            quantity=request.quantity,
            user_id=current_user.id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/ready-for-shipment", response_model=List[ShipmentReadyResponse])
def get_shipment_ready_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get list of products ready for shipment
    
    Shows completed manufacturing orders with available stock
    """
    service = FinishgoodsService(db)
    ready_products = service.get_shipment_ready_products()
    return ready_products


@router.get("/stock-aging", response_model=List[StockAgingResponse])
def get_stock_aging(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get finished goods stock aging analysis
    
    Categories:
    - Fresh: < 7 days
    - Normal: 7-14 days
    - Aging: 14-30 days
    - Old Stock: > 30 days
    """
    service = FinishgoodsService(db)
    aging_data = service.get_stock_aging()
    return aging_data
