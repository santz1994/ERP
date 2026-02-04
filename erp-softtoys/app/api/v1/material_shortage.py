"""
Material Allocation API Endpoints - Week 3 Implementation
Endpoints for material reservation, deduction, and shortage alerts

Author: IT Developer Expert
Date: 4 Februari 2026
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from decimal import Decimal

from app.core.database import get_db
from app.core.auth import require_permission
from app.core.models.manufacturing import WorkOrder, WorkOrderStatus, ManufacturingOrder
from app.core.models.users import User
from app.services.material_allocation_service import (
    MaterialAllocationService,
    MaterialShortageAlert,
    allocate_materials_for_mo
)


router = APIRouter(
    prefix="/api/v1/material-allocation",
    tags=["Material Allocation"]
)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class MaterialAllocationResponse(BaseModel):
    """Response for material allocation"""
    
    id: int
    wo_id: int
    material_id: int
    material_code: str
    material_name: str
    qty_allocated: Decimal
    qty_consumed: Decimal
    uom: str
    is_reserved: bool
    is_consumed: bool
    allocated_at: Optional[str]
    consumed_at: Optional[str]
    
    class Config:
        from_attributes = True


class ShortageAlertResponse(BaseModel):
    """Response for material shortage alert"""
    
    material_id: int
    material_code: str
    material_name: str
    required_qty: float
    available_qty: float
    shortage_qty: float
    shortage_pct: float
    wo_id: int
    wo_number: Optional[str]
    department: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    
    class Config:
        from_attributes = True


class WOStartRequest(BaseModel):
    """Request to start a Work Order"""
    
    force_start: bool = Field(
        default=False,
        description="Force start even if materials are in shortage (creates debt)"
    )


class WOStartResponse(BaseModel):
    """Response for WO start operation"""
    
    success: bool
    wo_id: int
    wo_number: str
    department: str
    status: str
    message: str
    materials_deducted: int
    errors: List[str] = []


# ============================================================================
# ENDPOINTS - MATERIAL ALLOCATION
# ============================================================================

@router.post(
    "/mo/{mo_id}/allocate",
    response_model=dict,
    summary="Allocate materials for all WOs in MO",
    dependencies=[Depends(require_permission("ppic.create_mo"))]
)
async def allocate_materials_for_manufacturing_order(
    mo_id: int,
    db: Session = Depends(get_db)
):
    """
    **Week 3 Feature**: Auto-allocate materials for all Work Orders in a Manufacturing Order
    
    This endpoint:
    1. Gets all WOs from the MO
    2. For each WO, allocates materials based on BOM
    3. Checks stock availability
    4. Returns shortage alerts if any
    
    **Returns**:
    - `total_allocations`: Number of material allocations created
    - `shortage_alerts`: List of materials in shortage
    - `has_shortages`: Boolean flag
    
    **Permissions**: PPIC only
    """
    
    try:
        result = allocate_materials_for_mo(db, mo_id)
        return result
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to allocate materials: {str(e)}"
        )


@router.get(
    "/wo/{wo_id}/allocations",
    response_model=List[MaterialAllocationResponse],
    summary="Get material allocations for a Work Order"
)
async def get_wo_material_allocations(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all material allocations for a specific Work Order
    
    Shows:
    - Material details
    - Allocated quantity
    - Consumed quantity
    - Reservation status
    """
    
    from app.core.models.manufacturing import SPKMaterialAllocation
    from app.core.models.products import Product
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order {wo_id} not found"
        )
    
    allocations = db.query(SPKMaterialAllocation).filter_by(wo_id=wo_id).all()
    
    response = []
    for alloc in allocations:
        material = db.query(Product).filter_by(id=alloc.material_id).first()
        
        response.append(MaterialAllocationResponse(
            id=alloc.id,
            wo_id=alloc.wo_id,
            material_id=alloc.material_id,
            material_code=material.code if material else "N/A",
            material_name=material.name if material else "Unknown",
            qty_allocated=alloc.qty_allocated,
            qty_consumed=alloc.qty_consumed,
            uom=alloc.uom.name if alloc.uom else "pcs",
            is_reserved=alloc.is_reserved,
            is_consumed=alloc.is_consumed,
            allocated_at=alloc.allocated_at.isoformat() if alloc.allocated_at else None,
            consumed_at=alloc.consumed_at.isoformat() if alloc.consumed_at else None
        ))
    
    return response


# ============================================================================
# ENDPOINTS - WORK ORDER START/STOP
# ============================================================================

@router.post(
    "/wo/{wo_id}/start",
    response_model=WOStartResponse,
    summary="Start Work Order and deduct materials",
    dependencies=[Depends(require_permission("production.input"))]
)
async def start_work_order(
    wo_id: int,
    request: WOStartRequest,
    current_user: User = Depends(require_permission("production.input")),
    db: Session = Depends(get_db)
):
    """
    **Week 3 Feature**: Start a Work Order and perform hard stock deduction
    
    This endpoint:
    1. Validates WO can start (status PENDING → RUNNING)
    2. Checks material availability
    3. Deducts stock from warehouse (FIFO)
    4. Updates WO status to RUNNING
    5. Records actual start date
    
    **force_start**: If `true`, allows starting even with material shortage (creates debt)
    
    **Permissions**: Production department users only
    """
    
    service = MaterialAllocationService(db)
    
    # Get Work Order
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order {wo_id} not found"
        )
    
    # Check WO status
    if wo.status != WorkOrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Work Order is already {wo.status.value}. Can only start PENDING WOs."
        )
    
    # Check if can start (materials available)
    if not request.force_start:
        can_start, blocking_reasons = service.check_wo_can_start(wo)
        
        if not can_start:
            return WOStartResponse(
                success=False,
                wo_id=wo.id,
                wo_number=wo.wo_number or f"WO-{wo.id}",
                department=wo.department.value,
                status=wo.status.value,
                message="Cannot start WO due to material shortages",
                materials_deducted=0,
                errors=blocking_reasons
            )
    
    # Deduct stock
    success, errors = service.deduct_stock_on_wo_start(
        wo=wo,
        force=request.force_start
    )
    
    if not success and not request.force_start:
        return WOStartResponse(
            success=False,
            wo_id=wo.id,
            wo_number=wo.wo_number or f"WO-{wo.id}",
            department=wo.department.value,
            status=wo.status.value,
            message="Failed to deduct materials from warehouse",
            materials_deducted=0,
            errors=errors
        )
    
    # Update WO status
    from datetime import date, datetime
    wo.status = WorkOrderStatus.RUNNING
    wo.actual_start_date = date.today()
    wo.start_time = datetime.utcnow()
    
    db.commit()
    db.refresh(wo)
    
    # Count materials deducted
    from app.core.models.manufacturing import SPKMaterialAllocation
    materials_deducted = db.query(SPKMaterialAllocation).filter_by(
        wo_id=wo.id,
        is_consumed=True
    ).count()
    
    return WOStartResponse(
        success=True,
        wo_id=wo.id,
        wo_number=wo.wo_number or f"WO-{wo.id}",
        department=wo.department.value,
        status=wo.status.value,
        message=f"Work Order started successfully. {materials_deducted} materials deducted.",
        materials_deducted=materials_deducted,
        errors=errors if request.force_start else []
    )


@router.get(
    "/wo/{wo_id}/can-start",
    response_model=dict,
    summary="Check if WO can start"
)
async def check_wo_can_start(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if a Work Order can start (all materials available)
    
    Returns:
    - `can_start`: Boolean
    - `blocking_reasons`: List of reasons why it cannot start
    """
    
    service = MaterialAllocationService(db)
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Work Order {wo_id} not found"
        )
    
    can_start, blocking_reasons = service.check_wo_can_start(wo)
    
    return {
        "wo_id": wo_id,
        "wo_number": wo.wo_number,
        "department": wo.department.value,
        "status": wo.status.value,
        "can_start": can_start,
        "blocking_reasons": blocking_reasons
    }


# ============================================================================
# ENDPOINTS - MATERIAL SHORTAGE ALERTS
# ============================================================================

@router.get(
    "/shortages",
    response_model=List[ShortageAlertResponse],
    summary="Get all material shortage alerts",
    dependencies=[Depends(require_permission("warehouse.view"))]
)
async def get_material_shortage_alerts(
    mo_id: Optional[int] = Query(None, description="Filter by Manufacturing Order ID"),
    department: Optional[str] = Query(None, description="Filter by department (CUTTING, SEWING, etc.)"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, MEDIUM, LOW)"),
    db: Session = Depends(get_db)
):
    """
    **Week 3 Feature**: Get material shortage alerts with filtering
    
    This endpoint returns all materials that are in shortage across Work Orders.
    
    **Severity Levels**:
    - `CRITICAL`: Missing 50%+ of required material
    - `HIGH`: Missing 20-50%
    - `MEDIUM`: Missing 5-20%
    - `LOW`: Missing <5%
    
    **Filters**:
    - `mo_id`: Show only shortages for specific MO
    - `department`: Show only shortages for specific department
    - `severity`: Show only specific severity level
    
    **Use Cases**:
    - PPIC: View all critical shortages to prioritize purchasing
    - Warehouse: View shortages to prepare stock
    - Production: Check if their WO can start
    
    **Permissions**: Warehouse, PPIC, Production can view
    """
    
    service = MaterialAllocationService(db)
    
    alerts = service.get_material_shortage_alerts(
        mo_id=mo_id,
        department=department,
        severity=severity
    )
    
    response = []
    for alert in alerts:
        # Get WO details
        wo = db.query(WorkOrder).filter_by(id=alert.wo_id).first()
        
        response.append(ShortageAlertResponse(
            material_id=alert.material_id,
            material_code=alert.material_code,
            material_name=alert.material_name,
            required_qty=float(alert.required_qty),
            available_qty=float(alert.available_qty),
            shortage_qty=float(alert.shortage_qty),
            shortage_pct=float((alert.shortage_qty / alert.required_qty) * 100),
            wo_id=alert.wo_id,
            wo_number=wo.wo_number if wo else f"WO-{alert.wo_id}",
            department=alert.department,
            severity=alert.severity
        ))
    
    return response


@router.get(
    "/shortages/summary",
    response_model=dict,
    summary="Get shortage alerts summary",
    dependencies=[Depends(require_permission("warehouse.view"))]
)
async def get_shortage_alerts_summary(
    db: Session = Depends(get_db)
):
    """
    Get summary statistics of material shortage alerts
    
    Returns:
    - Total shortages
    - Count by severity
    - Count by department
    - Top 10 most critical materials
    """
    
    service = MaterialAllocationService(db)
    
    all_alerts = service.get_material_shortage_alerts()
    
    # Count by severity
    severity_count = {}
    for alert in all_alerts:
        severity_count[alert.severity] = severity_count.get(alert.severity, 0) + 1
    
    # Count by department
    dept_count = {}
    for alert in all_alerts:
        dept_count[alert.department] = dept_count.get(alert.department, 0) + 1
    
    # Top 10 materials by shortage quantity
    material_shortage = {}
    for alert in all_alerts:
        key = alert.material_code
        if key not in material_shortage:
            material_shortage[key] = {
                "material_code": alert.material_code,
                "material_name": alert.material_name,
                "total_shortage": 0,
                "wo_count": 0
            }
        material_shortage[key]["total_shortage"] += float(alert.shortage_qty)
        material_shortage[key]["wo_count"] += 1
    
    top_10_materials = sorted(
        material_shortage.values(),
        key=lambda x: x["total_shortage"],
        reverse=True
    )[:10]
    
    return {
        "total_shortages": len(all_alerts),
        "by_severity": severity_count,
        "by_department": dept_count,
        "top_10_materials": top_10_materials,
        "has_critical": severity_count.get("CRITICAL", 0) > 0
    }


@router.get(
    "/health",
    summary="Health check endpoint"
)
async def material_allocation_health():
    """Health check for material allocation service"""
    return {
        "service": "Material Allocation Service",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "Auto material allocation",
            "Stock deduction (FIFO)",
            "Material shortage alerts",
            "Debt system support"
        ]
    }
