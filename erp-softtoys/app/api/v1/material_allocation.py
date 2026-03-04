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
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, SPKMaterialAllocation
from app.core.models.products import Product
from app.services.material_allocation_service import (
    MaterialAllocationService,
    allocate_materials_for_mo
)


router = APIRouter(prefix="/ppic/material-allocation", tags=["Material Allocation"])


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
        orm_mode = True


class MaterialAllocationListItem(BaseModel):
    """Material allocation list item for frontend"""
    id: int
    wo_id: int
    spk_number: str
    material_id: int
    material_code: str
    material_name: str
    department: str
    qty_allocated: float
    qty_consumed: float
    status: str  # ALLOCATED, RELEASED, PARTIAL, INSUFFICIENT
    uom: Optional[str] = None

    class Config:
        orm_mode = True


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

@router.get("", response_model=List[MaterialAllocationListItem])
def list_material_allocations(
    db: Session = Depends(get_db),
    status: Optional[str] = Query(None, description="Filter by status: ALLOCATED, RELEASED, PARTIAL, INSUFFICIENT"),
    department: Optional[str] = Query(None, description="Filter by department")
):
    """List all material allocations with optional filters."""
    query = (
        db.query(SPKMaterialAllocation)
        .join(WorkOrder, SPKMaterialAllocation.wo_id == WorkOrder.id)
        .join(Product, SPKMaterialAllocation.material_id == Product.id)
    )

    if department:
        query = query.filter(WorkOrder.department == department)

    allocations = query.all()

    result = []
    for alloc in allocations:
        wo = db.query(WorkOrder).get(alloc.wo_id)
        product = db.query(Product).get(alloc.material_id)
        if not wo or not product:
            continue

        # Derive status string
        if alloc.is_consumed:
            derived_status = "RELEASED"
        elif alloc.is_reserved:
            consumed_ratio = float(alloc.qty_consumed or 0) / float(alloc.qty_allocated or 1)
            if consumed_ratio >= 0.95:
                derived_status = "ALLOCATED"
            elif consumed_ratio > 0:
                derived_status = "PARTIAL"
            else:
                derived_status = "ALLOCATED"
        else:
            derived_status = "INSUFFICIENT"

        if status and derived_status != status:
            continue

        result.append(MaterialAllocationListItem(
            id=alloc.id,
            wo_id=alloc.wo_id,
            spk_number=wo.wo_number or f"WO-{wo.id}",
            material_id=alloc.material_id,
            material_code=product.code,
            material_name=product.name,
            department=wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
            qty_allocated=float(alloc.qty_allocated or 0),
            qty_consumed=float(alloc.qty_consumed or 0),
            status=derived_status,
            uom=alloc.uom
        ))

    return result


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
@router.get("/shortages", response_model=List[MaterialShortageAlertResponse])  # Alias for frontend
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


# ============================================================================
# Reservation Endpoints (used by MaterialReservation widget)
# ============================================================================

@router.get("/reservations")
def list_reservations(
    wo_id: Optional[int] = Query(None, description="Filter by Work Order ID"),
    material_id: Optional[int] = Query(None, description="Filter by Material (Product) ID"),
    db: Session = Depends(get_db)
):
    """List material allocations / reservations, optionally filtered by WO or material."""
    query = db.query(SPKMaterialAllocation)
    if wo_id:
        query = query.filter(SPKMaterialAllocation.wo_id == wo_id)
    if material_id:
        query = query.filter(SPKMaterialAllocation.material_id == material_id)

    allocations = query.all()
    result = []
    for alloc in allocations:
        wo = db.query(WorkOrder).get(alloc.wo_id)
        product = db.query(Product).get(alloc.material_id)
        if not wo or not product:
            continue
        state = "CONSUMED" if alloc.is_consumed else ("RESERVED" if alloc.is_reserved else "RELEASED")
        result.append({
            "id": alloc.id,
            "wo_id": alloc.wo_id,
            "wo_number": wo.wo_number or f"WO-{wo.id}",
            "material_id": alloc.material_id,
            "material_code": product.code,
            "material_name": product.name,
            "qty_allocated": float(alloc.qty_allocated or 0),
            "qty_consumed": float(alloc.qty_consumed or 0),
            "uom": alloc.uom,
            "state": state,
            "is_reserved": alloc.is_reserved,
            "is_consumed": alloc.is_consumed,
            "allocated_at": alloc.allocated_at.isoformat() if alloc.allocated_at else None,
        })
    return result


@router.post("/reserve")
def reserve_materials_for_wo(
    request: dict,
    db: Session = Depends(get_db)
):
    """Reserve (allocate) materials for a Work Order. Alias that auto-runs allocation."""
    wo_id = request.get("wo_id")
    if not wo_id:
        raise HTTPException(status_code=422, detail="wo_id is required")

    wo = db.query(WorkOrder).filter_by(id=wo_id).first()
    if not wo:
        raise HTTPException(status_code=404, detail=f"Work Order {wo_id} not found")

    service = MaterialAllocationService(db)
    try:
        allocated_count = service.allocate_materials_for_wo(wo)
        db.commit()
        return {
            "success": True,
            "wo_id": wo_id,
            "allocated_count": allocated_count,
            "message": f"✅ Reserved {allocated_count} materials for WO-{wo_id}"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reservations/{reservation_id}/release")
def release_reservation(
    reservation_id: int,
    db: Session = Depends(get_db)
):
    """Release a material reservation (mark is_reserved=False)."""
    from datetime import datetime
    alloc = db.query(SPKMaterialAllocation).filter_by(id=reservation_id).first()
    if not alloc:
        raise HTTPException(status_code=404, detail=f"Reservation {reservation_id} not found")
    if alloc.is_consumed:
        raise HTTPException(status_code=400, detail="Cannot release an already-consumed allocation")

    alloc.is_reserved = False
    alloc.qty_allocated = 0
    db.commit()
    return {"success": True, "reservation_id": reservation_id, "message": "Reservation released"}
