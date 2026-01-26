"""
Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved.

FinishGood Mobile API Endpoints
Handles barcode scanning for warehouse receipt and shipment preparation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional

from app.core.database import get_db
from app.core.models.users import User
from app.core.dependencies import require_permission
from app.core.permissions import ModuleName, Permission
from app.modules.finishgoods import FinishgoodsService

router = APIRouter(prefix="/finishgoods", tags=["FinishGoods-Mobile"])

# ==================== PYDANTIC SCHEMAS ====================

class BarcodeValidationResponse(BaseModel):
    id: str
    barcode: str
    product_code: str
    product_name: str
    article_ikea: str
    mo_id: int
    quantity: int
    unit_per_box: int
    box_count: int
    location: str
    received_date: str
    packing_date: str
    status: str

    class Config:
        from_attributes = True


class ScanBoxRequest(BaseModel):
    barcode: str = Field(..., description="Box barcode")
    mo_id: int = Field(..., description="Manufacturing Order ID")
    box_number: int = Field(..., gt=0, description="Box sequence number")
    quantity: int = Field(..., gt=0, description="Units in box")
    scanned_at: str = Field(..., description="ISO format timestamp")


class ScanBoxResponse(BaseModel):
    scan_id: str
    barcode: str
    mo_id: int
    box_number: int
    quantity: int
    timestamp: str
    action: str = "scan"
    user_id: int
    status: str = "recorded"


class PendingTransferResponse(BaseModel):
    transfer_id: int
    mo_id: int
    product_code: str
    product_name: str
    total_quantity: int
    boxes_count: int
    unit_per_box: int
    status: str
    packing_date: Optional[str] = None

    class Config:
        from_attributes = True


class ShipmentBoxData(BaseModel):
    box_number: int
    barcode: str
    product_code: str
    quantity: int
    scanned_count: int
    expected_count: int
    is_complete: bool


class ConfirmReceiptRequest(BaseModel):
    transfer_id: int = Field(..., description="Transfer ID from Packing")
    scanned_boxes: List[ShipmentBoxData] = Field(..., description="List of scanned boxes")
    received_at: str = Field(..., description="ISO format timestamp")
    received_by_user_id: int = Field(..., description="User ID who received")


class ConfirmReceiptResponse(BaseModel):
    message: str
    transfer_id: int
    quantity: int
    status: str
    scanned_boxes_count: int
    complete_boxes: int
    incomplete_boxes: int


class PrepareShipmentRequest(BaseModel):
    mo_id: int = Field(..., description="Manufacturing Order ID")
    destination: str = Field(..., description="Shipping destination")
    prepared_at: str = Field(..., description="ISO format timestamp")
    prepared_by_user_id: int = Field(..., description="User ID who prepared")


class PrepareShipmentResponse(BaseModel):
    message: str
    mo_id: int
    destination: str
    total_units: int
    status: str = "prepared_for_shipment"


# ==================== ENDPOINTS ====================

@router.get("/pending-transfers", response_model=List[PendingTransferResponse])
def get_pending_transfers(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.VIEW))
):
    """Get all pending transfers from Packing department.
    
    Returns transfers that are ready to be received in FinishGood warehouse.
    Mobile app uses this to display available MOsin scan mode.
    """
    try:
        service = FinishgoodsService(db)
        # Get transfers from packing that haven't been received yet
        transfers = service.get_pending_transfers()
        return transfers
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/barcode/{barcode}", response_model=BarcodeValidationResponse)
def validate_barcode(
    barcode: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.VIEW))
):
    """Validate barcode and retrieve product information.
    
    Called when mobile user scans a box barcode. Returns product details,
    expected quantity, and IKEA article information.
    
    - **barcode**: Box barcode to validate
    
    Returns:
    - Product code and name
    - IKEA article number
    - Expected quantity per box
    - MO ID and location
    - Stock information
    """
    try:
        service = FinishgoodsService(db)
        
        # Decode barcode and get product info
        # Barcode format: [MO_ID]-[PRODUCT_CODE]-[BOX_NUMBER]
        barcode_parts = barcode.split('-')
        if len(barcode_parts) < 3:
            raise ValueError(f"Invalid barcode format: {barcode}")
        
        mo_id = int(barcode_parts[0])
        product_code = barcode_parts[1]
        box_number = int(barcode_parts[2])
        
        # Get product info
        product_info = service.get_barcode_product_info(barcode)
        
        if not product_info:
            raise ValueError(f"Product not found for barcode: {barcode}")
        
        return product_info
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/scan-box", response_model=ScanBoxResponse)
def scan_box(
    request: ScanBoxRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.EXECUTE))
):
    """Record a box scan during FinishGood receipt.
    
    Called when mobile user scans a box. Records the scan with:
    - Box barcode
    - Quantity verified
    - Timestamp
    - User ID
    
    This creates a scan record for audit trail and receipt verification.
    """
    try:
        service = FinishgoodsService(db)
        
        # Create scan record
        scan_record = service.record_box_scan(
            barcode=request.barcode,
            mo_id=request.mo_id,
            box_number=request.box_number,
            quantity=request.quantity,
            user_id=current_user.id,
            scanned_at=request.scanned_at
        )
        
        return ScanBoxResponse(
            scan_id=str(scan_record.id),
            barcode=request.barcode,
            mo_id=request.mo_id,
            box_number=request.box_number,
            quantity=request.quantity,
            timestamp=request.scanned_at,
            user_id=current_user.id,
            status="recorded"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/receive-from-packing", response_model=ConfirmReceiptResponse)
def confirm_receipt_from_packing(
    request: ConfirmReceiptRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.EXECUTE))
):
    """Confirm receipt of finished goods from Packing department.
    
    After scanning all boxes in a shipment, warehouse staff confirms receipt.
    This:
    - Validates all scanned boxes
    - Checks against expected quantity
    - Updates inventory in FG warehouse
    - Marks transfer as completed
    - Creates audit trail
    
    Mobile app calls this after all boxes in a transfer are scanned.
    """
    try:
        service = FinishgoodsService(db)
        
        # Validate scanned boxes
        total_units = sum(box.quantity for box in request.scanned_boxes)
        complete_count = sum(1 for box in request.scanned_boxes if box.is_complete)
        incomplete_count = len(request.scanned_boxes) - complete_count
        
        # Confirm receipt
        result = service.confirm_receipt_from_packing(
            transfer_id=request.transfer_id,
            scanned_boxes=[
                {
                    'box_number': box.box_number,
                    'barcode': box.barcode,
                    'quantity': box.quantity,
                    'is_complete': box.is_complete
                }
                for box in request.scanned_boxes
            ],
            received_at=request.received_at,
            received_by_user_id=request.received_by_user_id
        )
        
        return ConfirmReceiptResponse(
            message="Goods received successfully",
            transfer_id=request.transfer_id,
            quantity=total_units,
            status="received",
            scanned_boxes_count=len(request.scanned_boxes),
            complete_boxes=complete_count,
            incomplete_boxes=incomplete_count
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/prepare-shipment", response_model=PrepareShipmentResponse)
def prepare_shipment(
    request: PrepareShipmentRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.EXECUTE))
):
    """Prepare received goods for shipment.
    
    After goods are received and verified, prepare for shipment by:
    - Marking goods as "prepared for shipment"
    - Recording destination
    - Generating shipping documents
    - Creating shipment records
    - Updating status for export/delivery
    
    Mobile app calls this after confirming receipt and entering destination.
    """
    try:
        service = FinishgoodsService(db)
        
        # Prepare shipment
        shipment = service.prepare_for_shipment(
            mo_id=request.mo_id,
            destination=request.destination,
            prepared_at=request.prepared_at,
            prepared_by_user_id=request.prepared_by_user_id
        )
        
        return PrepareShipmentResponse(
            message="Shipment prepared successfully",
            mo_id=request.mo_id,
            destination=request.destination,
            total_units=shipment['total_units'],
            status="prepared_for_shipment"
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/inventory", response_model=List[dict])
def get_finishgood_inventory(
    product_code: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.VIEW))
):
    """Get FinishGood warehouse inventory.
    
    Returns current stock levels for finished goods. Used by mobile app
    to display available inventory after receipt.
    
    - **product_code**: Filter by specific product code (optional)
    """
    try:
        service = FinishgoodsService(db)
        inventory = service.get_finished_goods_inventory(product_code=product_code)
        return inventory
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/scan-history/{mo_id}", response_model=List[dict])
def get_scan_history(
    mo_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.VIEW))
):
    """Get scan history for a specific Manufacturing Order.
    
    Returns all box scans recorded for an MO. Useful for auditing and
    verifying receipt accuracy.
    
    - **mo_id**: Manufacturing Order ID
    """
    try:
        service = FinishgoodsService(db)
        history = service.get_scan_history(mo_id)
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status/{transfer_id}", response_model=dict)
def get_transfer_status(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.VIEW))
):
    """Get current status of a transfer.
    
    Returns status, scanned boxes count, missing items, etc.
    Mobile app uses this to display progress during receipt.
    
    - **transfer_id**: Transfer ID to check
    """
    try:
        service = FinishgoodsService(db)
        status = service.get_transfer_status(transfer_id)
        return status
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ==================== HELPER ENDPOINTS ====================

@router.get("/statistics")
def get_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHGOODS, Permission.VIEW))
):
    """Get FinishGood warehouse statistics.
    
    Returns:
    - Total inventory value
    - Number of SKUs in stock
    - Aging analysis
    - Ready for shipment count
    """
    try:
        service = FinishgoodsService(db)
        stats = service.get_warehouse_statistics()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
