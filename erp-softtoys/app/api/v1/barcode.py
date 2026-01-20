"""
Barcode Scanner Module for Warehouse and Finishgoods
Handles barcode scanning for receiving and picking operations
Future: RFID integration planned
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.permissions import require_module_access, ModuleName
from app.core.models.users import User
from app.core.models.warehouse import StockMove, StockQuant, StockLot
from app.core.models.products import Product
from app.shared.audit import log_action

router = APIRouter(prefix="/barcode", tags=["Barcode Scanner"])


# ==================== SCHEMAS ====================

class BarcodeValidationRequest(BaseModel):
    barcode: str = Field(..., description="Barcode to validate")
    operation: str = Field(..., description="receive or pick")
    location: str = Field(..., description="warehouse or finishgoods")


class BarcodeValidationResponse(BaseModel):
    valid: bool
    product_id: Optional[int] = None
    product_code: Optional[str] = None
    product_name: Optional[str] = None
    current_qty: Optional[float] = None
    location: Optional[str] = None
    lot_number: Optional[str] = None
    message: str


class ReceiveGoodsRequest(BaseModel):
    barcode: str
    qty: float = Field(..., gt=0)
    location: str = Field(..., description="warehouse or finishgoods")
    lot_number: Optional[str] = None
    po_reference: Optional[str] = None
    notes: Optional[str] = None


class PickGoodsRequest(BaseModel):
    barcode: str
    qty: float = Field(..., gt=0)
    location: str = Field(..., description="warehouse or finishgoods")
    work_order_id: Optional[int] = None
    destination: Optional[str] = None
    notes: Optional[str] = None


class BarcodeHistoryResponse(BaseModel):
    id: int
    barcode: str
    product_name: str
    operation: str
    qty: float
    location: str
    timestamp: datetime
    user: str


# ==================== ENDPOINTS ====================

@router.post("/validate", response_model=BarcodeValidationResponse)
async def validate_barcode(
    request: BarcodeValidationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_module_access(ModuleName.WAREHOUSE))
):
    """
    Validate a barcode and return product information
    Used before receive/pick operations
    """
    
    # Find product by barcode (assuming barcode = product code)
    result = await db.execute(
        select(Product).where(Product.code == request.barcode)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        return BarcodeValidationResponse(
            valid=False,
            message=f"Product not found for barcode: {request.barcode}"
        )
    
    # Get current stock quantity
    stock_result = await db.execute(
        select(func.sum(StockQuant.quantity))
        .where(
            and_(
                StockQuant.product_id == product.id,
                StockQuant.location == request.location
            )
        )
    )
    current_qty = stock_result.scalar() or 0.0
    
    # Get latest lot number
    lot_result = await db.execute(
        select(StockLot.lot_number)
        .where(StockLot.product_id == product.id)
        .order_by(StockLot.created_at.desc())
        .limit(1)
    )
    lot_number = lot_result.scalar_one_or_none()
    
    # Validation based on operation
    if request.operation == "pick" and current_qty <= 0:
        return BarcodeValidationResponse(
            valid=False,
            product_id=product.id,
            product_code=product.code,
            product_name=product.name,
            current_qty=current_qty,
            message=f"Insufficient stock for picking. Current qty: {current_qty}"
        )
    
    return BarcodeValidationResponse(
        valid=True,
        product_id=product.id,
        product_code=product.code,
        product_name=product.name,
        current_qty=current_qty,
        location=request.location,
        lot_number=lot_number,
        message="Barcode validated successfully"
    )


@router.post("/receive")
async def receive_goods(
    request: ReceiveGoodsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_module_access(ModuleName.WAREHOUSE))
):
    """
    Receive goods using barcode scanner
    Creates stock move and updates inventory
    """
    
    # Validate barcode first
    result = await db.execute(
        select(Product).where(Product.code == request.barcode)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found for barcode: {request.barcode}"
        )
    
    # Generate lot number if not provided
    lot_number = request.lot_number
    if not lot_number:
        # Auto-generate: PROD-CODE-YYYYMMDD-XXX
        today = datetime.now().strftime("%Y%m%d")
        count_result = await db.execute(
            select(func.count(StockLot.id))
            .where(
                and_(
                    StockLot.product_id == product.id,
                    func.date(StockLot.created_at) == datetime.now().date()
                )
            )
        )
        count = count_result.scalar() + 1
        lot_number = f"{product.code}-{today}-{count:03d}"
    
    # Create stock lot
    stock_lot = StockLot(
        product_id=product.id,
        lot_number=lot_number,
        quantity=request.qty,
        location=request.location,
        created_at=datetime.now()
    )
    db.add(stock_lot)
    
    # Create stock move (receiving)
    stock_move = StockMove(
        product_id=product.id,
        move_type="receive",
        quantity=request.qty,
        from_location="supplier",
        to_location=request.location,
        reference=request.po_reference or f"BARCODE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        status="done",
        created_by=current_user.id,
        notes=request.notes or f"Received via barcode scanner by {current_user.username}",
        created_at=datetime.now()
    )
    db.add(stock_move)
    
    # Update or create stock quant
    quant_result = await db.execute(
        select(StockQuant).where(
            and_(
                StockQuant.product_id == product.id,
                StockQuant.location == request.location,
                StockQuant.lot_id == stock_lot.id
            )
        )
    )
    stock_quant = quant_result.scalar_one_or_none()
    
    if stock_quant:
        stock_quant.quantity += request.qty
    else:
        stock_quant = StockQuant(
            product_id=product.id,
            location=request.location,
            lot_id=stock_lot.id,
            quantity=request.qty,
            reserved_quantity=0.0
        )
        db.add(stock_quant)
    
    await db.commit()
    
    # Audit log
    await log_action(
        db, current_user.id, "barcode_receive",
        f"Received {request.qty} {product.uom} of {product.name} via barcode",
        {"barcode": request.barcode, "qty": request.qty, "location": request.location, "lot": lot_number}
    )
    
    return {
        "success": True,
        "message": f"Received {request.qty} {product.uom} of {product.name}",
        "product": {
            "id": product.id,
            "code": product.code,
            "name": product.name
        },
        "lot_number": lot_number,
        "location": request.location,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/pick")
async def pick_goods(
    request: PickGoodsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_module_access(ModuleName.WAREHOUSE))
):
    """
    Pick goods using barcode scanner (FIFO logic)
    Creates stock move and updates inventory
    """
    
    # Validate barcode
    result = await db.execute(
        select(Product).where(Product.code == request.barcode)
    )
    product = result.scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found for barcode: {request.barcode}"
        )
    
    # Check available stock (FIFO - oldest lot first)
    quants_result = await db.execute(
        select(StockQuant)
        .join(StockLot)
        .where(
            and_(
                StockQuant.product_id == product.id,
                StockQuant.location == request.location,
                StockQuant.quantity > StockQuant.reserved_quantity
            )
        )
        .order_by(StockLot.created_at.asc())
    )
    available_quants = quants_result.scalars().all()
    
    if not available_quants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No available stock for {product.name} in {request.location}"
        )
    
    # Calculate total available
    total_available = sum(q.quantity - q.reserved_quantity for q in available_quants)
    
    if total_available < request.qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient stock. Requested: {request.qty}, Available: {total_available}"
        )
    
    # Pick from quants (FIFO)
    remaining_qty = request.qty
    picked_lots = []
    
    for quant in available_quants:
        if remaining_qty <= 0:
            break
        
        available = quant.quantity - quant.reserved_quantity
        pick_qty = min(remaining_qty, available)
        
        # Update quant
        quant.quantity -= pick_qty
        remaining_qty -= pick_qty
        
        # Get lot info
        lot_result = await db.execute(
            select(StockLot).where(StockLot.id == quant.lot_id)
        )
        lot = lot_result.scalar_one()
        picked_lots.append({
            "lot_number": lot.lot_number,
            "qty": pick_qty
        })
    
    # Create stock move (picking)
    stock_move = StockMove(
        product_id=product.id,
        move_type="pick",
        quantity=request.qty,
        from_location=request.location,
        to_location=request.destination or "production",
        reference=f"WO-{request.work_order_id}" if request.work_order_id else f"BARCODE-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        status="done",
        created_by=current_user.id,
        notes=request.notes or f"Picked via barcode scanner by {current_user.username}",
        created_at=datetime.now()
    )
    db.add(stock_move)
    
    await db.commit()
    
    # Audit log
    await log_action(
        db, current_user.id, "barcode_pick",
        f"Picked {request.qty} {product.uom} of {product.name} via barcode",
        {"barcode": request.barcode, "qty": request.qty, "location": request.location, "lots": picked_lots}
    )
    
    return {
        "success": True,
        "message": f"Picked {request.qty} {product.uom} of {product.name}",
        "product": {
            "id": product.id,
            "code": product.code,
            "name": product.name
        },
        "picked_lots": picked_lots,
        "location": request.location,
        "timestamp": datetime.now().isoformat()
    }


@router.get("/history", response_model=List[BarcodeHistoryResponse])
async def get_barcode_history(
    location: Optional[str] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_module_access(ModuleName.WAREHOUSE))
):
    """
    Get barcode scanning history
    """
    
    query = select(StockMove).join(Product)
    
    if location:
        query = query.where(
            (StockMove.from_location == location) | (StockMove.to_location == location)
        )
    
    query = query.order_by(StockMove.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    moves = result.scalars().all()
    
    history = []
    for move in moves:
        product_result = await db.execute(
            select(Product).where(Product.id == move.product_id)
        )
        product = product_result.scalar_one()
        
        user_result = await db.execute(
            select(User).where(User.id == move.created_by)
        )
        user = user_result.scalar_one()
        
        history.append(BarcodeHistoryResponse(
            id=move.id,
            barcode=product.code,
            product_name=product.name,
            operation=move.move_type,
            qty=move.quantity,
            location=move.from_location if move.move_type == "pick" else move.to_location,
            timestamp=move.created_at,
            user=user.username
        ))
    
    return history


@router.get("/stats")
async def get_barcode_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_module_access(ModuleName.WAREHOUSE))
):
    """
    Get barcode scanning statistics
    """
    
    today = datetime.now().date()
    
    # Today's receives
    receive_result = await db.execute(
        select(func.count(StockMove.id), func.sum(StockMove.quantity))
        .where(
            and_(
                StockMove.move_type == "receive",
                func.date(StockMove.created_at) == today
            )
        )
    )
    receive_count, receive_qty = receive_result.first()
    
    # Today's picks
    pick_result = await db.execute(
        select(func.count(StockMove.id), func.sum(StockMove.quantity))
        .where(
            and_(
                StockMove.move_type == "pick",
                func.date(StockMove.created_at) == today
            )
        )
    )
    pick_count, pick_qty = pick_result.first()
    
    # Total products scanned today
    products_result = await db.execute(
        select(func.count(func.distinct(StockMove.product_id)))
        .where(func.date(StockMove.created_at) == today)
    )
    products_count = products_result.scalar()
    
    return {
        "today": {
            "date": today.isoformat(),
            "receives": {
                "count": receive_count or 0,
                "total_qty": float(receive_qty or 0)
            },
            "picks": {
                "count": pick_count or 0,
                "total_qty": float(pick_qty or 0)
            },
            "unique_products": products_count or 0
        }
    }
