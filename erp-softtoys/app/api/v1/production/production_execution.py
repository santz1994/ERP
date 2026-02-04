"""
Production Execution API Endpoints
Handles daily production input, WO completion, and WIP transfers

Author: IT Developer Expert
Date: 3 Februari 2026
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from decimal import Decimal
from datetime import datetime

from app.core.database import get_db
from app.core.models.manufacturing import WorkOrder, ManufacturingOrder, WorkOrderStatus, Department
from app.core.models.products import Product
from app.core.models.warehouse import StockQuant, Location
from app.services.bom_explosion_service import BOMExplosionService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/production", tags=["production-execution"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class ProductionInputRequest(BaseModel):
    """Daily production input data"""
    wo_id: int = Field(..., description="Work Order ID")
    date: str = Field(..., description="Production date (YYYY-MM-DD)")
    qty_produced: Decimal = Field(..., gt=0, description="Total quantity produced")
    qty_good: Decimal = Field(..., ge=0, description="Good quality quantity")
    qty_defect: Decimal = Field(..., ge=0, description="Defect quantity")
    notes: Optional[str] = Field(None, description="Production notes")


class ProductionInputResponse(BaseModel):
    """Production input confirmation"""
    success: bool
    message: str
    wo_id: int
    wo_number: str
    qty_produced: Decimal
    qty_good: Decimal
    qty_defect: Decimal
    completion_percentage: Decimal
    status: str


class WOCompleteRequest(BaseModel):
    """Request to mark Work Order as complete"""
    wo_id: int = Field(..., description="Work Order ID")
    create_wip_transfer: bool = Field(True, description="Auto-create WIP transfer to warehouse")


class WOCompleteResponse(BaseModel):
    """Work Order completion confirmation"""
    success: bool
    message: str
    wo_id: int
    wo_number: str
    status: str
    wip_transferred: bool
    wip_qty: Optional[Decimal] = None
    next_wo_unlocked: List[str] = []


class WIPTransferRequest(BaseModel):
    """WIP transfer between departments"""
    wo_id: int = Field(..., description="Source Work Order ID")
    from_location_id: int = Field(..., description="Source warehouse location")
    to_location_id: int = Field(..., description="Destination warehouse location")
    wip_product_id: int = Field(..., description="WIP product to transfer")
    qty_transfer: Decimal = Field(..., gt=0, description="Quantity to transfer")
    notes: Optional[str] = Field(None, description="Transfer notes")


class WIPTransferResponse(BaseModel):
    """WIP transfer confirmation"""
    success: bool
    message: str
    transfer_id: int
    wip_product_code: str
    wip_product_name: str
    qty_transferred: Decimal
    from_location: str
    to_location: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/input", response_model=ProductionInputResponse)
async def input_production_daily(
    request: ProductionInputRequest,
    db: Session = Depends(get_db)
):
    """
    Record daily production input for Work Order
    
    Process:
    1. Validate Work Order exists and is RUNNING
    2. Update actual quantities (cumulative)
    3. Calculate completion percentage
    4. If reached target, mark as FINISHED
    5. Trigger auto-unlock next WO if completed
    
    **Quantities**:
    - qty_produced: Total produced today (added to actual_qty)
    - qty_good: Good quality (added to good_qty)
    - qty_defect: Defect/rework (added to defect_qty)
    
    **Validation**: qty_good + qty_defect = qty_produced
    """
    
    # Validate input
    if request.qty_good + request.qty_defect != request.qty_produced:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sum of good qty and defect qty must equal total produced qty"
        )
    
    # Get Work Order
    wo = db.query(WorkOrder).filter_by(id=request.wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {request.wo_id} not found"
        )
    
    # Validate WO can accept input (must be RUNNING or PENDING)
    if wo.status == WorkOrderStatus.FINISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Work Order {wo.wo_number} is already FINISHED. Cannot add more production."
        )
    
    try:
        # Update quantities (cumulative)
        wo.actual_qty = (wo.actual_qty or Decimal('0')) + request.qty_produced
        wo.good_qty = (wo.good_qty or Decimal('0')) + request.qty_good
        wo.defect_qty = (wo.defect_qty or Decimal('0')) + request.qty_defect
        
        # Calculate completion percentage
        completion_pct = (wo.actual_qty / wo.target_qty) * 100 if wo.target_qty > 0 else 0
        
        # Auto-update status based on progress
        old_status = wo.status
        if wo.status == WorkOrderStatus.PENDING:
            wo.status = WorkOrderStatus.RUNNING
        
        # Check if reached target
        if wo.actual_qty >= wo.target_qty:
            wo.status = WorkOrderStatus.FINISHED
        
        # Add notes
        if request.notes:
            existing_notes = wo.notes or ""
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            wo.notes = f"{existing_notes}\n[{timestamp}] {request.notes}".strip()
        
        db.commit()
        db.refresh(wo)
        
        # If completed, trigger auto-unlock next WO
        if wo.status == WorkOrderStatus.FINISHED and old_status != WorkOrderStatus.FINISHED:
            service = BOMExplosionService(db)
            service.update_wo_status_auto(mo_id=wo.mo_id)
        
        return ProductionInputResponse(
            success=True,
            message=f"Production input recorded for {wo.wo_number}. Completion: {completion_pct:.1f}%",
            wo_id=wo.id,
            wo_number=wo.wo_number,
            qty_produced=request.qty_produced,
            qty_good=request.qty_good,
            qty_defect=request.qty_defect,
            completion_percentage=completion_pct,
            status=wo.status.value if hasattr(wo.status, 'value') else str(wo.status)
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error recording production input: {str(e)}"
        )


@router.post("/complete", response_model=WOCompleteResponse)
async def complete_work_order(
    request: WOCompleteRequest,
    db: Session = Depends(get_db)
):
    """
    Mark Work Order as FINISHED and create WIP transfer
    
    Process:
    1. Validate WO is RUNNING
    2. Mark as FINISHED
    3. Create WIP stock in warehouse (if enabled)
    4. Unlock next dependent WO
    
    **WIP Transfer**:
    - Output WIP product moved to warehouse
    - Quantity = good_qty (defects not transferred)
    - Location = Warehouse Main (default)
    """
    
    wo = db.query(WorkOrder).filter_by(id=request.wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {request.wo_id} not found"
        )
    
    if wo.status == WorkOrderStatus.FINISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Work Order {wo.wo_number} is already FINISHED"
        )
    
    try:
        # Mark as completed
        wo.status = WorkOrderStatus.FINISHED
        
        wip_transferred = False
        wip_qty = None
        
        # Create WIP transfer if requested and WO has output WIP
        if request.create_wip_transfer and wo.output_wip_product_id:
            # Get good quantity produced
            good_qty = wo.good_qty or Decimal('0')
            
            if good_qty > 0:
                # Get warehouse location
                warehouse_main = db.query(StockLocation).filter_by(
                    name="Warehouse Main"
                ).first()
                
                if not warehouse_main:
                    # Create default location if not exists
                    warehouse_main = StockLocation(
                        name="Warehouse Main",
                        location_type="warehouse"
                    )
                    db.add(warehouse_main)
                    db.flush()
                
                # Check if stock quant exists
                stock_quant = db.query(StockQuant).filter(
                    and_(
                        StockQuant.product_id == wo.output_wip_product_id,
                        StockQuant.location_id == warehouse_main.id
                    )
                ).first()
                
                if stock_quant:
                    # Update existing stock
                    stock_quant.quantity += good_qty
                else:
                    # Create new stock quant
                    stock_quant = StockQuant(
                        product_id=wo.output_wip_product_id,
                        location_id=warehouse_main.id,
                        quantity=good_qty
                    )
                    db.add(stock_quant)
                
                wip_transferred = True
                wip_qty = good_qty
        
        db.commit()
        
        # Unlock next WO
        service = BOMExplosionService(db)
        service.update_wo_status_auto(mo_id=wo.mo_id)
        
        # Check which WOs were unlocked
        next_wos = db.query(WorkOrder).filter(
            and_(
                WorkOrder.mo_id == wo.mo_id,
                WorkOrder.sequence == wo.sequence + 1,
                WorkOrder.status == WorkOrderStatus.RUNNING
            )
        ).all()
        
        unlocked_wo_numbers = [next_wo.wo_number for next_wo in next_wos]
        
        return WOCompleteResponse(
            success=True,
            message=f"Work Order {wo.wo_number} marked as FINISHED",
            wo_id=wo.id,
            wo_number=wo.wo_number,
            status=wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
            wip_transferred=wip_transferred,
            wip_qty=wip_qty,
            next_wo_unlocked=unlocked_wo_numbers
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing Work Order: {str(e)}"
        )


@router.post("/wip-transfer", response_model=WIPTransferResponse)
async def transfer_wip(
    request: WIPTransferRequest,
    db: Session = Depends(get_db)
):
    """
    Transfer WIP between warehouse locations
    
    Process:
    1. Validate source stock availability
    2. Deduct from source location
    3. Add to destination location
    4. Create transfer log
    
    **Use Cases**:
    - SEWING → FINISHING warehouse
    - FINISHING → PACKING warehouse
    - Department buffer → Production line
    """
    
    # Validate Work Order
    wo = db.query(WorkOrder).filter_by(id=request.wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {request.wo_id} not found"
        )
    
    # Validate WIP product
    wip_product = db.query(Product).filter_by(id=request.wip_product_id).first()
    if not wip_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"WIP Product with ID {request.wip_product_id} not found"
        )
    
    # Validate locations
    from_location = db.query(StockLocation).filter_by(id=request.from_location_id).first()
    to_location = db.query(StockLocation).filter_by(id=request.to_location_id).first()
    
    if not from_location or not to_location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source or destination location not found"
        )
    
    try:
        # Check source stock availability
        source_stock = db.query(StockQuant).filter(
            and_(
                StockQuant.product_id == request.wip_product_id,
                StockQuant.location_id == request.from_location_id
            )
        ).first()
        
        if not source_stock or source_stock.quantity < request.qty_transfer:
            available_qty = source_stock.quantity if source_stock else Decimal('0')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {available_qty}, Requested: {request.qty_transfer}"
            )
        
        # Deduct from source
        source_stock.quantity -= request.qty_transfer
        
        # Add to destination
        dest_stock = db.query(StockQuant).filter(
            and_(
                StockQuant.product_id == request.wip_product_id,
                StockQuant.location_id == request.to_location_id
            )
        ).first()
        
        if dest_stock:
            dest_stock.quantity += request.qty_transfer
        else:
            dest_stock = StockQuant(
                product_id=request.wip_product_id,
                location_id=request.to_location_id,
                quantity=request.qty_transfer
            )
            db.add(dest_stock)
        
        db.commit()
        
        # TODO: Create transfer log entry for audit trail
        
        return WIPTransferResponse(
            success=True,
            message=f"Transferred {request.qty_transfer} pcs from {from_location.name} to {to_location.name}",
            transfer_id=0,  # TODO: Return actual transfer log ID
            wip_product_code=wip_product.code,
            wip_product_name=wip_product.name,
            qty_transferred=request.qty_transfer,
            from_location=from_location.name,
            to_location=to_location.name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error transferring WIP: {str(e)}"
        )


@router.get("/work-order/{wo_id}/progress")
async def get_work_order_progress(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed progress for Work Order
    
    Returns:
    - Target vs Actual quantities
    - Good vs Defect breakdown
    - Completion percentage
    - Status history
    - Material consumption (if tracked)
    """
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {wo_id} not found"
        )
    
    # Calculate metrics
    target_qty = wo.target_qty or Decimal('0')
    actual_qty = wo.actual_qty or Decimal('0')
    good_qty = wo.good_qty or Decimal('0')
    defect_qty = wo.defect_qty or Decimal('0')
    
    completion_pct = (actual_qty / target_qty * 100) if target_qty > 0 else 0
    good_rate = (good_qty / actual_qty * 100) if actual_qty > 0 else 0
    defect_rate = (defect_qty / actual_qty * 100) if actual_qty > 0 else 0
    
    return {
        "wo_id": wo.id,
        "wo_number": wo.wo_number,
        "department": wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
        "status": wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
        "quantities": {
            "target": float(target_qty),
            "actual": float(actual_qty),
            "good": float(good_qty),
            "defect": float(defect_qty),
            "remaining": float(target_qty - actual_qty)
        },
        "metrics": {
            "completion_percentage": round(completion_pct, 2),
            "good_rate_percentage": round(good_rate, 2),
            "defect_rate_percentage": round(defect_rate, 2)
        },
        "notes": wo.notes
    }
