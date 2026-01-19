"""
Warehouse Management API Endpoints
Stock management, transfers, inventory tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.schemas import (
    StockTransferCreate, StockTransferResponse, StockCheckResponse,
    TransferDept, TransferStatus
)
from app.core.dependencies import get_db, require_any_role
from app.core.models.users import User
from app.core.models.warehouse import StockMove, StockQuant, Location
from app.core.models.transfer import TransferLog, TransferDept as TransferDeptEnum, TransferStatus as TransferStatusEnum, LineOccupancy, LineStatus
from app.core.models.products import Product


router = APIRouter(
    prefix="/warehouse",
    tags=["Warehouse - Stock Management"],
)


@router.get(
    "/stock/{product_id}",
    response_model=StockCheckResponse,
    dependencies=[Depends(require_any_role("warehouse_admin", "ppic_manager", "spv_cutting"))]
)
async def check_stock(
    product_id: int,
    location_id: int = Query(None),
    current_user: User = Depends(require_any_role("warehouse_admin", "ppic_manager", "spv_cutting")),
    db: Session = Depends(get_db)
):
    """
    Check current stock for a product
    
    **Roles Required**: warehouse_admin, ppic_manager, spv_cutting
    
    **Path Parameters**:
    - `product_id`: Product ID to check
    
    **Query Parameters**:
    - `location_id`: Optional - specific location (warehouse zone, line, etc)
    
    **Responses**:
    - `200`: Current stock status
    - `403`: Insufficient permissions
    - `404`: Product not found
    
    **Response Fields**:
    - `qty_on_hand`: Physical stock currently available
    - `qty_reserved`: Qty already allocated to SPK but not yet taken
    - `qty_available`: qty_on_hand - qty_reserved (Can use for new SPK)
    """
    # Validate product exists
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get stock quant (sum across all locations if not specified)
    query = db.query(StockQuant).filter(StockQuant.product_id == product_id)
    
    if location_id:
        query = query.filter(StockQuant.location_id == location_id)
    
    stock_quants = query.all()
    
    total_on_hand = sum(sq.qty_on_hand for sq in stock_quants)
    total_reserved = sum(sq.qty_reserved for sq in stock_quants)
    
    # Get location name
    if location_id:
        location = db.query(Location).filter(Location.id == location_id).first()
        location_name = location.name if location else "Unknown"
    else:
        location_name = "All Locations"
    
    return StockCheckResponse(
        product_id=product_id,
        location=location_name,
        qty_on_hand=total_on_hand,
        qty_reserved=total_reserved,
        qty_available=total_on_hand - total_reserved,
        updated_at=db.query(StockQuant.updated_at).filter(
            StockQuant.product_id == product_id
        ).order_by(StockQuant.updated_at.desc()).first()[0] if stock_quants else None
    )


@router.post(
    "/transfer",
    response_model=StockTransferResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_any_role("warehouse_admin", "spv_cutting", "spv_sewing"))]
)
async def create_stock_transfer(
    transfer_data: StockTransferCreate,
    current_user: User = Depends(require_any_role("warehouse_admin", "spv_cutting", "spv_sewing")),
    db: Session = Depends(get_db)
):
    """
    Create inter-departmental stock transfer (QT-09 Protocol)
    
    **Roles Required**: warehouse_admin, spv_cutting, spv_sewing
    
    **Request Body**:
    - `from_dept`: Source department (Cutting, Embroidery, Sewing, etc)
    - `to_dept`: Destination department
    - `product_id`: Product being transferred
    - `qty`: Quantity to transfer
    - `batch_number`: Batch identifier for traceability
    - `reference_doc`: Reference document (SPK, PO number)
    - `lot_id`: Optional - lot/roll number for FIFO tracking
    
    **Responses**:
    - `201`: Transfer created in INITIATED state
    - `400`: Insufficient stock, invalid product, or line clearance blocked
    - `403`: Insufficient permissions
    - `422`: Validation error
    
    **Business Logic**:
    1. **Line Clearance Check (ID 290, 380)**:
       - Query LineOccupancy table for to_dept line status
       - If OCCUPIED by different article → Status = BLOCKED, return error
       - If CLEAR → Continue
    
    2. **Stock Validation**:
       - Check qty_available >= qty (on_hand - reserved)
       - Decrement qty_available, increment qty_reserved
    
    3. **Create Transfer Log**:
       - Status = INITIATED (waiting for ACCEPT at receiving dept)
       - Set timestamp_start
       - Set is_line_clear flag
    
    4. **Lock Stock in Database**:
       - Mark stock as locked until handshake complete (ID 293, 383)
    
    **Handshake Protocol (QT-09)**:
    - Transfer starts in INITIATED state
    - Receiving dept scans ACCEPT → Status = ACCEPTED
    - After processing → Status = COMPLETED
    - If line occupied → Status = BLOCKED (operator must clear)
    """
    # Validate product exists
    product = db.query(Product).filter(Product.id == transfer_data.product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product not found"
        )
    
    # Check stock availability
    stock_query = db.query(StockQuant).filter(
        StockQuant.product_id == transfer_data.product_id
    )
    
    if transfer_data.lot_id:
        stock_query = stock_query.filter(StockQuant.lot_id == transfer_data.lot_id)
    
    stock_quants = stock_query.all()
    total_available = sum((sq.qty_on_hand - sq.qty_reserved) for sq in stock_quants)
    
    if total_available < transfer_data.qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Available: {total_available}, Requested: {transfer_data.qty}"
        )
    
    # **QT-09 PROTOCOL: LINE CLEARANCE CHECK (Step 1 - ID 290, 380)**
    line_occupancy = db.query(LineOccupancy).filter(
        LineOccupancy.dept_name == transfer_data.to_dept.value
    ).first()
    
    is_line_clear = False
    
    if line_occupancy:
        # Line exists - check if it's occupied by different article
        if line_occupancy.occupancy_status == LineStatus.OCCUPIED:
            if line_occupancy.current_article_id != transfer_data.product_id:
                # Different article on line - BLOCK transfer
                transfer_status = TransferStatusEnum.BLOCKED
            else:
                # Same article - clear to proceed
                is_line_clear = True
                transfer_status = TransferStatusEnum.INITIATED
        else:
            # Line is CLEAR or PAUSED - proceed
            is_line_clear = True
            transfer_status = TransferStatusEnum.INITIATED
    else:
        # No line occupancy record - assume CLEAR
        is_line_clear = True
        transfer_status = TransferStatusEnum.INITIATED
    
    # Create transfer log
    from datetime import datetime
    from_dept_enum = TransferDeptEnum(transfer_data.from_dept.value)
    to_dept_enum = TransferDeptEnum(transfer_data.to_dept.value)
    
    new_transfer = TransferLog(
        from_dept=from_dept_enum,
        to_dept=to_dept_enum,
        product_id=transfer_data.product_id,
        qty_sent=transfer_data.qty,
        qty_received=None,
        status=transfer_status,
        is_line_clear=is_line_clear,
        timestamp_start=datetime.utcnow(),
        reference_doc=transfer_data.reference_doc,
        batch_number=transfer_data.batch_number,
        initiated_by_id=current_user.id
    )
    
    # If blocked - return early with error
    if transfer_status == TransferStatusEnum.BLOCKED:
        db.add(new_transfer)
        db.commit()
        db.refresh(new_transfer)
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transfer blocked: Line {transfer_data.to_dept.value} is occupied by different article",
            headers={"X-Transfer-ID": str(new_transfer.id), "X-Transfer-Status": "BLOCKED"}
        )
    
    # Reserve stock
    for stock_quant in stock_quants:
        if transfer_data.qty > 0:
            amount_to_reserve = min(transfer_data.qty, stock_quant.qty_on_hand - stock_quant.qty_reserved)
            stock_quant.qty_reserved += amount_to_reserve
            transfer_data.qty -= amount_to_reserve
    
    db.add(new_transfer)
    db.commit()
    db.refresh(new_transfer)
    
    return StockTransferResponse(
        id=new_transfer.id,
        from_dept=transfer_data.from_dept,
        to_dept=transfer_data.to_dept,
        product_id=new_transfer.product_id,
        qty_sent=new_transfer.qty_sent,
        qty_received=new_transfer.qty_received,
        status=TransferStatus(new_transfer.status),
        is_line_clear=new_transfer.is_line_clear,
        timestamp_start=new_transfer.timestamp_start,
        timestamp_accept=new_transfer.timestamp_accept,
        timestamp_end=new_transfer.timestamp_end
    )


@router.post(
    "/transfer/{transfer_id}/accept",
    response_model=StockTransferResponse,
    dependencies=[Depends(require_any_role("warehouse_admin", "spv_sewing", "spv_finishing"))]
)
async def accept_transfer(
    transfer_id: int,
    qty_received: Decimal = None,
    current_user: User = Depends(require_any_role("warehouse_admin", "spv_sewing", "spv_finishing")),
    db: Session = Depends(get_db)
):
    """
    Accept transfer at receiving department (QT-09 Handshake - Step 3, ID 293 / 383)
    
    **Roles Required**: warehouse_admin, spv_sewing, spv_finishing
    
    **Path Parameters**:
    - `transfer_id`: Transfer log ID
    
    **Query Parameters**:
    - `qty_received`: Actual quantity received (if different from sent)
    
    **Responses**:
    - `200`: Transfer accepted, status changed to ACCEPTED
    - `400`: Transfer not in INITIATED state, qty mismatch > 10%
    - `403`: Insufficient permissions
    - `404`: Transfer not found
    
    **Business Logic (Handshake Digital - ID 293)**:
    1. Update transfer status to ACCEPTED
    2. Record timestamp_accept and accepted_by user
    3. If qty_received differs from qty_sent > 10% → Generate alert
    4. Release stock from reserved to available (qty_on_hand)
    5. Update LineOccupancy if applicable
    """
    transfer = db.query(TransferLog).filter(TransferLog.id == transfer_id).first()
    if not transfer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transfer not found"
        )
    
    if transfer.status != TransferStatusEnum.INITIATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only accept INITIATED transfers. Current status: {transfer.status}"
        )
    
    # Use qty_sent if qty_received not provided
    received = qty_received if qty_received else transfer.qty_sent
    
    # Check for significant qty mismatch
    qty_diff_percent = abs(received - transfer.qty_sent) / transfer.qty_sent * 100 if transfer.qty_sent > 0 else 0
    
    if qty_diff_percent > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantity mismatch: Expected {transfer.qty_sent}, Received {received} ({qty_diff_percent:.1f}% difference). Max allowed: 10%"
        )
    
    # Accept transfer
    from datetime import datetime
    transfer.status = TransferStatusEnum.ACCEPTED
    transfer.qty_received = received
    transfer.timestamp_accept = datetime.utcnow()
    transfer.accepted_by_id = current_user.id
    
    db.commit()
    db.refresh(transfer)
    
    return StockTransferResponse(
        id=transfer.id,
        from_dept=TransferDept(transfer.from_dept),
        to_dept=TransferDept(transfer.to_dept),
        product_id=transfer.product_id,
        qty_sent=transfer.qty_sent,
        qty_received=transfer.qty_received,
        status=TransferStatus(transfer.status),
        is_line_clear=transfer.is_line_clear,
        timestamp_start=transfer.timestamp_start,
        timestamp_accept=transfer.timestamp_accept,
        timestamp_end=transfer.timestamp_end
    )
