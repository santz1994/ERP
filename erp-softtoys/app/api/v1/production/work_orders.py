"""
Work Order API Endpoints
Handles Work Order generation, listing, and status management

Author: IT Developer Expert
Date: 3 Februari 2026
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from decimal import Decimal

from app.core.database import get_db
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, Department, WorkOrderStatus
from app.core.models.products import Product
from app.services.bom_explosion_service import BOMExplosionService
from pydantic import BaseModel, Field

router = APIRouter(prefix="/work-orders", tags=["work-orders"])


# ============================================================================
# Pydantic Schemas
# ============================================================================

class WorkOrderResponse(BaseModel):
    """Work Order response model"""
    id: int
    mo_id: int
    wo_number: str
    department: str
    sequence: int
    status: str
    target_qty: Decimal
    actual_qty: Optional[Decimal] = None
    good_qty: Optional[Decimal] = None
    defect_qty: Optional[Decimal] = None
    notes: Optional[str] = None
    
    # WIP tracking
    input_wip_product_id: Optional[int] = None
    input_wip_product_code: Optional[str] = None
    input_wip_product_name: Optional[str] = None
    output_wip_product_id: Optional[int] = None
    output_wip_product_code: Optional[str] = None
    output_wip_product_name: Optional[str] = None
    
    # Dependency info
    can_start: bool = False
    dependency_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class BOMExplosionNode(BaseModel):
    """BOM Explosion tree node"""
    product_id: int
    product_code: str
    product_name: str
    quantity: Decimal
    level: int
    type: str  # 'wip', 'raw', 'finished_good'
    department: Optional[str] = None
    children: List['BOMExplosionNode'] = []
    materials: List[dict] = []


class GenerateWORequest(BaseModel):
    """Request to generate Work Orders from MO"""
    mo_id: int = Field(..., description="Manufacturing Order ID")


class GenerateWOResponse(BaseModel):
    """Response after generating Work Orders"""
    success: bool
    message: str
    mo_id: int
    work_orders_created: int
    work_orders: List[WorkOrderResponse]


class WODependencyResponse(BaseModel):
    """Work Order dependency check response"""
    wo_id: int
    wo_number: str
    can_start: bool
    reason: str


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/generate", response_model=GenerateWOResponse, status_code=status.HTTP_201_CREATED)
async def generate_work_orders(
    request: GenerateWORequest,
    db: Session = Depends(get_db)
):
    """
    Generate Work Orders from Manufacturing Order
    
    Process:
    1. Explode BOM multi-level
    2. Generate Work Orders per department with buffer
    3. Set dependencies and sequence
    4. Return created Work Orders
    
    **Dual Trigger Support**:
    - PARTIAL mode: Only Cutting & Embroidery WOs created
    - RELEASED mode: All WOs created
    """
    
    # Check if MO exists
    mo = db.query(ManufacturingOrder).filter_by(id=request.mo_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing Order with ID {request.mo_id} not found"
        )
    
    # Check if WOs already exist
    existing_wos = db.query(WorkOrder).filter_by(mo_id=request.mo_id).count()
    if existing_wos > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Work Orders already exist for MO {mo.batch_number}. Found {existing_wos} WOs."
        )
    
    try:
        # Initialize BOM explosion service
        service = BOMExplosionService(db)
        
        # Generate Work Orders
        work_orders = service.explode_mo_and_generate_work_orders(
            mo_id=request.mo_id,
            target_qty=mo.qty_target
        )
        
        if not work_orders:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate Work Orders. No WOs created."
            )
        
        # Commit transaction
        db.commit()
        
        # Prepare response
        wo_responses = []
        for wo in work_orders:
            # Get input/output WIP product details
            input_wip = None
            output_wip = None
            
            if wo.input_wip_product_id:
                input_wip = db.query(Product).filter_by(id=wo.input_wip_product_id).first()
            
            if wo.output_wip_product_id:
                output_wip = db.query(Product).filter_by(id=wo.output_wip_product_id).first()
            
            # Check dependencies
            can_start, reason = service.check_wo_dependencies(wo.id)
            
            wo_responses.append(WorkOrderResponse(
                id=wo.id,
                mo_id=wo.mo_id,
                wo_number=wo.wo_number,
                department=wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
                sequence=wo.sequence,
                status=wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
                target_qty=wo.target_qty,
                actual_qty=wo.actual_qty,
                good_qty=wo.good_qty,
                defect_qty=wo.defect_qty,
                notes=wo.notes,
                input_wip_product_id=wo.input_wip_product_id,
                input_wip_product_code=input_wip.code if input_wip else None,
                input_wip_product_name=input_wip.name if input_wip else None,
                output_wip_product_id=wo.output_wip_product_id,
                output_wip_product_code=output_wip.code if output_wip else None,
                output_wip_product_name=output_wip.name if output_wip else None,
                can_start=can_start,
                dependency_reason=reason
            ))
        
        return GenerateWOResponse(
            success=True,
            message=f"Successfully generated {len(work_orders)} Work Orders for MO {mo.batch_number}",
            mo_id=request.mo_id,
            work_orders_created=len(work_orders),
            work_orders=wo_responses
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating Work Orders: {str(e)}"
        )


@router.get("/", response_model=List[WorkOrderResponse])
async def list_work_orders(
    mo_id: Optional[int] = None,
    department: Optional[str] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List Work Orders with filters
    
    Query Parameters:
    - mo_id: Filter by Manufacturing Order
    - department: Filter by department (CUTTING, SEWING, etc.)
    - status_filter: Filter by status (PENDING, RUNNING, FINISHED)
    """
    
    query = db.query(WorkOrder).options(
        joinedload(WorkOrder.manufacturing_order),
        joinedload(WorkOrder.product)
    )
    
    # Apply filters
    if mo_id:
        query = query.filter(WorkOrder.mo_id == mo_id)
    
    # Skip filter if 'ALL' is sent from frontend
    if department and department.upper() != 'ALL':
        try:
            dept_enum = Department[department.upper()]
            query = query.filter(WorkOrder.department == dept_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid department: {department}"
            )
    
    # Skip filter if 'ALL' is sent from frontend  
    if status_filter and status_filter.upper() != 'ALL':
        try:
            status_enum = WorkOrderStatus[status_filter.upper()]
            query = query.filter(WorkOrder.status == status_enum)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status_filter}"
            )
    
    # Order by MO, then sequence
    query = query.order_by(WorkOrder.mo_id, WorkOrder.sequence)
    
    work_orders = query.all()
    
    # Prepare response with dependency info
    service = BOMExplosionService(db)
    wo_responses = []
    
    for wo in work_orders:
        # Check dependencies
        can_start, reason = service.check_wo_dependencies(wo.id)
        
        wo_responses.append(WorkOrderResponse(
            id=wo.id,
            mo_id=wo.mo_id,
            wo_number=wo.wo_number or f"WO-{wo.id}",
            department=wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
            sequence=wo.sequence or 0,
            status=wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
            target_qty=wo.target_qty or wo.input_qty,
            actual_qty=wo.output_qty,
            good_qty=wo.output_qty,
            defect_qty=wo.reject_qty,
            notes=wo.notes,
            input_wip_product_id=wo.input_wip_product_id,
            input_wip_product_code=wo.product.code if wo.product else None,
            input_wip_product_name=wo.product.name if wo.product else None,
            output_wip_product_id=wo.output_wip_product_id,
            output_wip_product_code=None,
            output_wip_product_name=None,
            can_start=can_start,
            dependency_reason=reason
        ))
    
    return wo_responses


@router.get("/{wo_id}", response_model=WorkOrderResponse)
async def get_work_order(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """Get single Work Order by ID with full details"""
    
    wo = db.query(WorkOrder).options(
        joinedload(WorkOrder.mo),
        joinedload(WorkOrder.input_wip_product),
        joinedload(WorkOrder.output_wip_product)
    ).filter_by(id=wo_id).first()
    
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {wo_id} not found"
        )
    
    # Check dependencies
    service = BOMExplosionService(db)
    can_start, reason = service.check_wo_dependencies(wo.id)
    
    return WorkOrderResponse(
        id=wo.id,
        mo_id=wo.mo_id,
        wo_number=wo.wo_number,
        department=wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
        sequence=wo.sequence,
        status=wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
        target_qty=wo.target_qty,
        actual_qty=wo.actual_qty,
        good_qty=wo.good_qty,
        defect_qty=wo.defect_qty,
        notes=wo.notes,
        input_wip_product_id=wo.input_wip_product_id,
        input_wip_product_code=wo.input_wip_product.code if wo.input_wip_product else None,
        input_wip_product_name=wo.input_wip_product.name if wo.input_wip_product else None,
        output_wip_product_id=wo.output_wip_product_id,
        output_wip_product_code=wo.output_wip_product.code if wo.output_wip_product else None,
        output_wip_product_name=wo.output_wip_product.name if wo.output_wip_product else None,
        can_start=can_start,
        dependency_reason=reason
    )


@router.get("/{wo_id}/dependencies", response_model=WODependencyResponse)
async def check_wo_dependencies(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if Work Order can start (dependencies satisfied)
    
    Returns:
    - can_start: boolean
    - reason: explanation
    """
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {wo_id} not found"
        )
    
    service = BOMExplosionService(db)
    can_start, reason = service.check_wo_dependencies(wo_id)
    
    return WODependencyResponse(
        wo_id=wo_id,
        wo_number=wo.wo_number,
        can_start=can_start,
        reason=reason
    )


@router.get("/mo/{mo_id}/bom-explosion", response_model=BOMExplosionNode)
async def get_bom_explosion_tree(
    mo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get BOM explosion tree for Manufacturing Order
    
    Returns hierarchical BOM structure:
    - Multi-level WIP stages
    - Materials per stage
    - Quantities with buffer
    """
    
    mo = db.query(ManufacturingOrder).filter_by(id=mo_id).first()
    if not mo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Manufacturing Order with ID {mo_id} not found"
        )
    
    try:
        service = BOMExplosionService(db)
        
        # Explode BOM
        explosion_result = service.explode_bom_multi_level(
            product_id=mo.product_id,
            quantity=mo.qty_target,
            level=0
        )
        
        if not explosion_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No BOM found for product ID {mo.product_id}"
            )
        
        # Convert to response format
        def convert_to_node(data: dict) -> BOMExplosionNode:
            """Recursively convert explosion data to response model"""
            product = db.query(Product).filter_by(id=data['product_id']).first()
            
            node = BOMExplosionNode(
                product_id=data['product_id'],
                product_code=data.get('product_code', product.code if product else 'UNKNOWN'),
                product_name=data.get('product_name', product.name if product else 'UNKNOWN'),
                quantity=Decimal(str(data['quantity'])),
                level=data['level'],
                type=data.get('type', 'unknown'),
                department=data.get('department'),
                children=[],
                materials=[]
            )
            
            # Add materials
            if 'materials' in data:
                node.materials = data['materials']
            
            # Recursively add children
            if 'children' in data:
                for child in data['children']:
                    node.children.append(convert_to_node(child))
            
            return node
        
        return convert_to_node(explosion_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exploding BOM: {str(e)}"
        )


@router.put("/{wo_id}/status")
async def update_work_order_status(
    wo_id: int,
    new_status: str,
    db: Session = Depends(get_db)
):
    """
    Update Work Order status and trigger auto-update for dependent WOs
    
    Status transitions:
    - PENDING → RUNNING (when dependencies satisfied)
    - RUNNING → FINISHED (when production complete)
    - FINISHED → cannot change
    """
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order with ID {wo_id} not found"
        )
    
    try:
        # Validate new status
        new_status_enum = WorkOrderStatus[new_status.upper()]
        
        # Update status
        old_status = wo.status
        wo.status = new_status_enum
        db.commit()
        
        # If changed to FINISHED, trigger auto-update for dependent WOs
        if new_status_enum == WorkOrderStatus.FINISHED:
            service = BOMExplosionService(db)
            service.update_wo_status_auto(mo_id=wo.mo_id)
        
        return {
            "success": True,
            "message": f"Work Order {wo.wo_number} status updated from {old_status} to {new_status_enum}",
            "wo_id": wo_id,
            "old_status": old_status.value if hasattr(old_status, 'value') else str(old_status),
            "new_status": new_status_enum.value
        }
        
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}. Valid options: PENDING, RUNNING, FINISHED"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating Work Order status: {str(e)}"
        )


@router.post("/{wo_id}/start", status_code=status.HTTP_200_OK)
async def start_work_order(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Start a Work Order (change status from PENDING to RUNNING)
    
    **Universal endpoint for all departments**
    
    Path Parameters:
    - wo_id: Work Order ID to start
    
    Response:
    - 200: WO started successfully
    - 404: WO not found
    - 400: Invalid state transition
    """
    from datetime import datetime
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order #{wo_id} not found"
        )
    
    # Validate state transition
    if wo.status != WorkOrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot start WO in {wo.status} state. Must be PENDING."
        )
    
    # Update status
    wo.status = WorkOrderStatus.RUNNING
    wo.start_time = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": f"Work Order #{wo_id} started",
        "wo_id": wo_id,
        "department": wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
        "status": "RUNNING",
        "start_time": wo.start_time.isoformat()
    }


@router.post("/{wo_id}/complete", status_code=status.HTTP_200_OK)
async def complete_work_order(
    wo_id: int,
    actual_qty: Optional[Decimal] = None,
    good_qty: Optional[Decimal] = None,
    defect_qty: Optional[Decimal] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Complete a Work Order (change status from RUNNING to FINISHED)
    
    **Universal endpoint for all departments**
    
    Path Parameters:
    - wo_id: Work Order ID to complete
    
    Query Parameters:
    - actual_qty: Actual quantity produced
    - good_qty: Good quality quantity
    - defect_qty: Defect quantity
    - notes: Optional completion notes
    
    Response:
    - 200: WO completed successfully
    - 404: WO not found
    - 400: Invalid state transition
    """
    from datetime import datetime
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order #{wo_id} not found"
        )
    
    # Validate state transition
    if wo.status != WorkOrderStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot complete WO in {wo.status} state. Must be RUNNING."
        )
    
    # Update status and quantities
    wo.status = WorkOrderStatus.FINISHED
    wo.end_time = datetime.utcnow()
    
    if actual_qty is not None:
        wo.actual_qty = actual_qty
    if good_qty is not None:
        wo.good_qty = good_qty
    if defect_qty is not None:
        wo.defect_qty = defect_qty
    if notes:
        wo.notes = notes
    
    db.commit()
    
    # Trigger auto-update for dependent WOs
    service = BOMExplosionService(db)
    service.update_wo_status_auto(mo_id=wo.mo_id)
    
    return {
        "success": True,
        "message": f"Work Order #{wo_id} completed",
        "wo_id": wo_id,
        "department": wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
        "status": "FINISHED",
        "end_time": wo.end_time.isoformat(),
        "actual_qty": float(wo.actual_qty) if wo.actual_qty else 0,
        "good_qty": float(wo.good_qty) if wo.good_qty else 0,
        "defect_qty": float(wo.defect_qty) if wo.defect_qty else 0
    }

