"""
Material Allocation API Endpoints - Week 3 Implementation

Features:
1. Allocate materials for MO/WO
2. Start WO with stock deduction
3. Get material shortage alerts
4. Check if WO can start

Author: IT Developer Expert
Date: 4 Februari 2026
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder
from app.services.material_allocation_service import (
    MaterialAllocationService,
    allocate_materials_for_mo
)


router = APIRouter(prefix="/api/v1/material-allocation", tags=["Material Allocation"])


# ============================================================================
# Request/Response Schemas
# ============================================================================

class MaterialShortageAlertResponse(BaseModel):
    """Material shortage alert response schema"""
    material_id: int
    material_code: str
    material_name: str
    required_qty: float
    available_qty: float
    shortage_qty: float
    shortage_pct: float
    wo_id: int
    department: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    
    class Config:
        from_attributes = True


class AllocateMaterialsRequest(BaseModel):
    """Request to allocate materials for MO"""
    mo_id: int
    check_availability: bool = True


class AllocateMaterialsResponse(BaseModel):
    """Response after material allocation"""
    success: bool
    mo_id: int
    total_work_orders: int
    total_allocations: int
    shortage_alerts: List[MaterialShortageAlertResponse]
    has_shortages: bool
    message: str


class StartWORequest(BaseModel):
    """Request to start Work Order with stock deduction"""
    wo_id: int
    force: bool = False  # Force start even with shortages (debt system)


class StartWOResponse(BaseModel):
    """Response after starting WO"""
    success: bool
    wo_id: int
    message: str
    errors: List[str] = []


class CheckWOCanStartResponse(BaseModel):
    """Response for can-start check"""
    can_start: bool
    wo_id: int
    blocking_reasons: List[str]


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/allocate", response_model=AllocateMaterialsResponse)
def allocate_materials(
    request: AllocateMaterialsRequest,
    db: Session = Depends(get_db)
):
    """
    Allocate materials for all Work Orders in a Manufacturing Order
    
    This creates soft reservations for materials.
    """
    
    try:
        result = allocate_materials_for_mo(db, request.mo_id)
        
        return AllocateMaterialsResponse(
            success=result["success"],
            mo_id=result["mo_id"],
            total_work_orders=result["total_work_orders"],
            total_allocations=result["total_allocations"],
            shortage_alerts=[
                MaterialShortageAlertResponse(**alert)
                for alert in result["shortage_alerts"]
            ],
            has_shortages=result["has_shortages"],
            message=f"Allocated materials for {result['total_work_orders']} Work Orders. "
                   f"{'⚠️ Found shortages!' if result['has_shortages'] else '✅ All materials available.'}"
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error allocating materials: {str(e)}")


@router.post("/start-wo", response_model=StartWOResponse)
def start_work_order(
    request: StartWORequest,
    db: Session = Depends(get_db)
):
    """
    Start Work Order with automatic stock deduction
    
    This performs hard deduction from warehouse.
    If force=True, allows negative inventory (debt system).
    """
    
    service = MaterialAllocationService(db)
    
    # Get WO
    wo = db.query(WorkOrder).filter_by(id=request.wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work Order {request.wo_id} not found")
    
    # Check if already started
    if wo.status.value == "IN_PROGRESS":
        return StartWOResponse(
            success=False,
            wo_id=wo.id,
            message="Work Order already started",
            errors=["WO is already in IN_PROGRESS status"]
        )
    
    # Deduct stock
    success, errors = service.deduct_stock_on_wo_start(wo, force=request.force)
    
    if success:
        # Update WO status
        from app.core.models.manufacturing import WorkOrderStatus
        wo.status = WorkOrderStatus.IN_PROGRESS
        wo.materials_consumed = True
        
        from datetime import date
        wo.actual_start_date = date.today()
        
        db.commit()
        
        return StartWOResponse(
            success=True,
            wo_id=wo.id,
            message=f"✅ Work Order {wo.wo_number} started successfully! Materials deducted.",
            errors=[]
        )
    else:
        if request.force:
            # Even with force, failed - critical error
            return StartWOResponse(
                success=False,
                wo_id=wo.id,
                message="❌ Failed to start Work Order even with force mode",
                errors=errors
            )
        else:
            return StartWOResponse(
                success=False,
                wo_id=wo.id,
                message="⚠️ Cannot start WO: Material shortages detected. Use force=true to override.",
                errors=errors
            )


@router.get("/shortage-alerts", response_model=List[MaterialShortageAlertResponse])
def get_shortage_alerts(
    mo_id: Optional[int] = Query(None, description="Filter by Manufacturing Order ID"),
    department: Optional[str] = Query(None, description="Filter by department"),
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL/HIGH/MEDIUM/LOW)"),
    db: Session = Depends(get_db)
):
    """
    Get material shortage alerts
    
    Filters:
    - mo_id: Get alerts for specific MO
    - department: Get alerts for specific department
    - severity: Get alerts by severity level
    """
    
    service = MaterialAllocationService(db)
    
    alerts = service.get_material_shortage_alerts(
        mo_id=mo_id,
        department=department,
        severity=severity
    )
    
    return [
        MaterialShortageAlertResponse(**alert.to_dict())
        for alert in alerts
    ]


@router.get("/check-wo-can-start/{wo_id}", response_model=CheckWOCanStartResponse)
def check_wo_can_start(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if Work Order can start (all materials available)
    
    Returns:
    - can_start: True if WO can start, False otherwise
    - blocking_reasons: List of reasons preventing WO from starting
    """
    
    service = MaterialAllocationService(db)
    
    # Get WO
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work Order {wo_id} not found")
    
    can_start, blocking_reasons = service.check_wo_can_start(wo)
    
    return CheckWOCanStartResponse(
        can_start=can_start,
        wo_id=wo_id,
        blocking_reasons=blocking_reasons
    )


@router.get("/wo/{wo_id}/allocations")
def get_wo_material_allocations(
    wo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all material allocations for a Work Order
    
    Shows:
    - Material details
    - Allocated quantity
    - Consumed quantity
    - Reservation status
    """
    
    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work Order {wo_id} not found")
    
    allocations = []
    
    for alloc in wo.allocated_materials:
        material = alloc.material
        
        allocations.append({
            "id": alloc.id,
            "material_id": alloc.material_id,
            "material_code": material.code if material else "N/A",
            "material_name": material.name if material else "Unknown",
            "qty_allocated": float(alloc.qty_allocated),
            "qty_consumed": float(alloc.qty_consumed),
            "uom": alloc.uom.name if alloc.uom else "pcs",
            "is_reserved": alloc.is_reserved,
            "is_consumed": alloc.is_consumed,
            "allocated_at": alloc.allocated_at.isoformat() if alloc.allocated_at else None,
            "consumed_at": alloc.consumed_at.isoformat() if alloc.consumed_at else None
        })
    
    return {
        "wo_id": wo_id,
        "wo_number": wo.wo_number,
        "department": wo.department.value,
        "allocations": allocations,
        "total_allocations": len(allocations),
        "all_consumed": all(a["is_consumed"] for a in allocations)
    }


@router.post("/mo/{mo_id}/check-all-wos")
def check_all_wos_can_start(
    mo_id: int,
    db: Session = Depends(get_db)
):
    """
    Check if all Work Orders in an MO can start
    
    Returns status for each WO.
    """
    
    mo = db.query(ManufacturingOrder).filter_by(id=mo_id).first()
    if not mo:
        raise HTTPException(status_code=404, detail=f"Manufacturing Order {mo_id} not found")
    
    service = MaterialAllocationService(db)
    
    wo_statuses = []
    
    for wo in mo.work_orders:
        can_start, blocking_reasons = service.check_wo_can_start(wo)
        
        wo_statuses.append({
            "wo_id": wo.id,
            "wo_number": wo.wo_number,
            "department": wo.department.value,
            "can_start": can_start,
            "blocking_reasons": blocking_reasons,
            "status": "✅ Ready" if can_start else "❌ Blocked"
        })
    
    return {
        "mo_id": mo_id,
        "mo_batch_number": mo.batch_number,
        "total_wos": len(wo_statuses),
        "ready_wos": len([w for w in wo_statuses if w["can_start"]]),
        "blocked_wos": len([w for w in wo_statuses if not w["can_start"]]),
        "work_orders": wo_statuses
    }
