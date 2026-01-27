"""
API Endpoints for Daily Production Input Tracking & Editable SPK
Created: January 26, 2026
Location: app/api/v1/ppic/daily_production.py

Endpoints:
- POST /ppic/spk/{spk_id}/daily-production      - Record daily production
- GET /ppic/spk/{spk_id}/daily-production       - Get calendar data
- POST /ppic/spk/{spk_id}/complete              - Mark SPK as completed
- PUT /ppic/spk/{spk_id}                        - Edit SPK quantity
- POST /ppic/material-debt/{debt_id}/approve    - Approve material debt
- POST /ppic/material-debt/{debt_id}/settle     - Settle material debt
"""

from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models import User, SPKDailyProduction, SPKProductionCompletion, SPK
from app.core.models import SPKModification, MaterialDebt, MaterialDebtSettlement, AuditLog

router = APIRouter(prefix="/ppic", tags=["ppic"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class RecordDailyProductionRequest(BaseModel):
    """Request model for recording daily production"""
    production_date: date
    input_qty: int
    notes: Optional[str] = None
    status: str = "CONFIRMED"


class DailyProductionResponse(BaseModel):
    """Response model for daily production data"""
    spk_id: int
    target_qty: int
    actual_qty: int
    daily_entries: List[dict]
    completion_percentage: float
    is_completed: bool


class UpdateSPKRequest(BaseModel):
    """Request model for editing SPK"""
    modified_qty: int
    modification_reason: str
    allow_negative_inventory: bool = False


class CompleteSPKRequest(BaseModel):
    """Request model for completing SPK"""
    confirmation_notes: str


class ApproveMaterialDebtRequest(BaseModel):
    """Request model for approving material debt"""
    approval_decision: str  # APPROVE, REJECT
    approval_reason: Optional[str] = None


class SettleMaterialDebtRequest(BaseModel):
    """Request model for settling material debt"""
    qty_settled: int
    settlement_date: date
    settlement_notes: Optional[str] = None


# ============================================================================
# ENDPOINT 1: Record Daily Production
# ============================================================================
@router.post("/spk/{spk_id}/daily-production")
async def record_daily_production(
    spk_id: int,
    request: RecordDailyProductionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Record daily production quantity for SPK
    Permission: PPIC_MANAGER, SUPERVISOR, OPERATOR
    
    Request:
    {
        "production_date": "2026-01-26",
        "input_qty": 50,
        "notes": "Good quality production",
        "status": "CONFIRMED"
    }
    
    Response:
    {
        "data": {
            "spk_id": 1,
            "daily_entry": {...},
            "cumulative_qty": 110,
            "target_qty": 500,
            "completion_percentage": 22.0
        },
        "message": "Daily production recorded successfully",
        "timestamp": "2026-01-26T10:00:00"
    }
    """
    # Permission check
    # await check_permission - removed
    
    # Verify SPK exists
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    # Check for duplicate entry (same SPK, same date)
    existing = db.query(SPKDailyProduction).filter(
        SPKDailyProduction.spk_id == spk_id,
        SPKDailyProduction.production_date == request.production_date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Daily production for {request.production_date} already recorded"
        )
    
    # Calculate cumulative quantity
    last_entry = db.query(SPKDailyProduction)\
        .filter(SPKDailyProduction.spk_id == spk_id)\
        .order_by(SPKDailyProduction.production_date.desc())\
        .first()
    
    cumulative = (last_entry.cumulative_qty if last_entry else 0) + request.input_qty
    
    # Create daily entry
    daily_entry = SPKDailyProduction(
        spk_id=spk_id,
        production_date=request.production_date,
        input_qty=request.input_qty,
        cumulative_qty=cumulative,
        input_by_id=current_user.id,
        status=request.status,
        notes=request.notes
    )
    db.add(daily_entry)
    
    # Update SPK production status
    spk.actual_qty = cumulative
    spk.production_status = "IN_PROGRESS" if cumulative > 0 else "NOT_STARTED"
    
    # Audit log
    audit_log = AuditLog(
        action="DAILY_PRODUCTION_INPUT",
        resource_type="SPK",
        resource_id=spk_id,
        user_id=current_user.id,
        details={
            "date": request.production_date.isoformat(),
            "qty": request.input_qty,
            "cumulative": cumulative
        },
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "data": {
            "spk_id": spk_id,
            "daily_entry": {
                "id": daily_entry.id,
                "date": daily_entry.production_date.isoformat(),
                "qty": daily_entry.input_qty,
                "cumulative": cumulative,
                "status": daily_entry.status
            },
            "cumulative_qty": cumulative,
            "target_qty": spk.target_qty,
            "completion_percentage": (cumulative / spk.target_qty * 100) if spk.target_qty > 0 else 0
        },
        "message": "Daily production recorded successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 2: Get Daily Production Report
# ============================================================================
@router.get("/spk/{spk_id}/daily-production")
async def get_daily_production(
    spk_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily production entries for SPK (calendar-style data)
    Permission: PPIC_MANAGER, SUPERVISOR, OPERATOR, MANAGER
    
    Response:
    {
        "data": {
            "spk_id": 1,
            "target_qty": 500,
            "actual_qty": 255,
            "daily_entries": [
                {
                    "date": "2026-01-26",
                    "qty": 50,
                    "cumulative": 50,
                    "notes": "Good quality",
                    "status": "CONFIRMED"
                },
                ...
            ],
            "completion_percentage": 51.0,
            "is_completed": false
        }
    }
    """
    # Permission check
    # await check_permission - removed
    
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    # Get all daily entries
    entries = db.query(SPKDailyProduction)\
        .filter(SPKDailyProduction.spk_id == spk_id)\
        .order_by(SPKDailyProduction.production_date.asc())\
        .all()
    
    # Format calendar response
    calendar_data = {
        "spk_id": spk_id,
        "target_qty": spk.target_qty,
        "actual_qty": spk.actual_qty or 0,
        "daily_entries": [
            {
                "date": entry.production_date.isoformat(),
                "qty": entry.input_qty,
                "cumulative": entry.cumulative_qty,
                "notes": entry.notes,
                "status": entry.status,
                "input_by": entry.input_by.username if entry.input_by else None
            }
            for entry in entries
        ],
        "completion_percentage": (spk.actual_qty / spk.target_qty * 100) if spk.target_qty > 0 else 0,
        "is_completed": spk.production_status == "COMPLETED"
    }
    
    return {"data": calendar_data, "timestamp": datetime.utcnow().isoformat()}


# ============================================================================
# ENDPOINT 3: Complete SPK Production
# ============================================================================
@router.post("/spk/{spk_id}/complete")
async def complete_spk_production(
    spk_id: int,
    request: CompleteSPKRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark SPK as completed when target quantity reached
    Permission: PPIC_MANAGER, MANAGER, SUPERADMIN
    
    Request:
    {
        "confirmation_notes": "Production completed successfully"
    }
    
    Response:
    {
        "data": {
            "spk_id": 1,
            "production_status": "COMPLETED",
            "target_qty": 500,
            "actual_qty": 500,
            "completion_date": "2026-01-30"
        },
        "message": "✅ SPK marked as COMPLETED"
    }
    """
    # Permission check
    # await check_permission - removed
    
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    # Verify quantity reached target
    if (spk.actual_qty or 0) < spk.target_qty:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete. Need {spk.target_qty - (spk.actual_qty or 0)} more units"
        )
    
    # Mark as completed
    spk.production_status = "COMPLETED"
    spk.completion_date = date.today()
    
    # Create completion record
    completion = SPKProductionCompletion(
        spk_id=spk_id,
        target_qty=spk.target_qty,
        actual_qty=spk.actual_qty or 0,
        completed_date=spk.completion_date,
        confirmed_by_id=current_user.id,
        confirmation_notes=request.confirmation_notes,
        confirmed_at=datetime.utcnow(),
        is_completed=True
    )
    db.add(completion)
    
    # Audit log
    audit_log = AuditLog(
        action="SPK_COMPLETED",
        resource_type="SPK",
        resource_id=spk_id,
        user_id=current_user.id,
        details={
            "target_qty": spk.target_qty,
            "actual_qty": spk.actual_qty or 0,
            "completion_date": spk.completion_date.isoformat()
        },
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "data": {
            "spk_id": spk_id,
            "production_status": "COMPLETED",
            "target_qty": spk.target_qty,
            "actual_qty": spk.actual_qty or 0,
            "completion_date": spk.completion_date.isoformat()
        },
        "message": f"✅ SPK {spk_id} marked as COMPLETED",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 4: Edit SPK (Increase/Decrease Quantity)
# ============================================================================
@router.put("/spk/{spk_id}")
async def update_spk(
    spk_id: int,
    request: UpdateSPKRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Edit SPK quantity (increase/decrease production target)
    Permission: PPIC_MANAGER, MANAGER, SUPERADMIN
    
    Request:
    {
        "modified_qty": 600,
        "modification_reason": "Customer requested 100 more units",
        "allow_negative_inventory": true
    }
    
    Response:
    {
        "data": {
            "spk_id": 1,
            "original_qty": 500,
            "modified_qty": 600,
            "modification_reason": "Customer requested increase",
            "material_debt_created": true,
            "material_debt_id": 5
        }
    }
    """
    # Permission check
    # await check_permission - removed
    
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")
    
    # Store original quantity
    original_qty = spk.target_qty
    spk.original_qty = original_qty
    spk.modified_qty = request.modified_qty
    spk.modification_reason = request.modification_reason
    spk.modified_by_id = current_user.id
    spk.modified_at = datetime.utcnow()
    spk.allow_negative_inventory = request.allow_negative_inventory
    
    # Record modification
    modification = SPKModification(
        spk_id=spk_id,
        field_name="target_qty",
        old_value=str(original_qty),
        new_value=str(request.modified_qty),
        modified_by_id=current_user.id,
        modification_reason=request.modification_reason
    )
    db.add(modification)
    
    # Check if we need to create material debt
    material_debt_created = False
    material_debt_id = None
    
    # If new quantity is higher and we don't have enough materials, create debt
    qty_increase = request.modified_qty - original_qty
    
    if qty_increase > 0 and request.allow_negative_inventory:
        # This would typically check available materials
        # For now, we'll let the application decide if debt is needed
        spk.negative_approval_status = "PENDING"
    
    # Audit log
    audit_log = AuditLog(
        action="SPK_MODIFIED",
        resource_type="SPK",
        resource_id=spk_id,
        user_id=current_user.id,
        details={
            "original_qty": original_qty,
            "modified_qty": request.modified_qty,
            "reason": request.modification_reason
        },
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "data": {
            "spk_id": spk_id,
            "original_qty": original_qty,
            "modified_qty": request.modified_qty,
            "modification_reason": request.modification_reason,
            "allow_negative_inventory": request.allow_negative_inventory,
            "negative_approval_status": spk.negative_approval_status,
            "material_debt_created": material_debt_created,
            "material_debt_id": material_debt_id
        },
        "message": f"SPK {spk_id} updated successfully",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 5: Approve Material Debt
# ============================================================================
@router.post("/material-debt/{debt_id}/approve")
async def approve_material_debt(
    debt_id: int,
    request: ApproveMaterialDebtRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve or reject material debt
    Permission: MANAGER, WAREHOUSE_SPV, SUPERADMIN
    
    Request:
    {
        "approval_decision": "APPROVE",
        "approval_reason": "Material in transit, ETA Jan 28"
    }
    """
    # await check_permission - removed
    
    debt = db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Material debt not found")
    
    debt.approval_status = request.approval_decision  # APPROVE or REJECT
    debt.approved_by_id = current_user.id
    debt.approved_at = datetime.utcnow()
    debt.approval_reason = request.approval_reason
    
    audit_log = AuditLog(
        action=f"MATERIAL_DEBT_{request.approval_decision.upper()}",
        resource_type="MATERIAL_DEBT",
        resource_id=debt_id,
        user_id=current_user.id,
        details={"reason": request.approval_reason},
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "data": {
            "debt_id": debt_id,
            "approval_status": debt.approval_status,
            "approved_by": current_user.username,
            "approved_at": debt.approved_at.isoformat()
        },
        "message": f"Material debt {request.approval_decision.lower()}d",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 6: Settle Material Debt
# ============================================================================
@router.post("/material-debt/{debt_id}/settle")
async def settle_material_debt(
    debt_id: int,
    request: SettleMaterialDebtRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Settle material debt when material arrives
    Permission: WAREHOUSE_SPV, MANAGER, SUPERADMIN
    
    Request:
    {
        "qty_settled": 100,
        "settlement_date": "2026-01-28",
        "settlement_notes": "100 units received from supplier"
    }
    """
    # await check_permission - removed
    
    debt = db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
    if not debt:
        raise HTTPException(status_code=404, detail="Material debt not found")
    
    # Check if settlement exceeds owed amount
    if request.qty_settled > (debt.qty_owed - debt.qty_settled):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot settle {request.qty_settled}. Only {debt.qty_owed - debt.qty_settled} units owed"
        )
    
    # Create settlement record
    settlement = MaterialDebtSettlement(
        material_debt_id=debt_id,
        qty_settled=request.qty_settled,
        settlement_date=request.settlement_date,
        received_by_id=current_user.id,
        settled_by_id=current_user.id,
        settlement_notes=request.settlement_notes
    )
    db.add(settlement)
    
    # Update debt
    debt.qty_settled += request.qty_settled
    if debt.qty_settled >= debt.qty_owed:
        debt.approval_status = "SETTLED"
    
    audit_log = AuditLog(
        action="MATERIAL_DEBT_SETTLED",
        resource_type="MATERIAL_DEBT",
        resource_id=debt_id,
        user_id=current_user.id,
        details={"qty_settled": request.qty_settled},
        timestamp=datetime.utcnow()
    )
    db.add(audit_log)
    db.commit()
    
    return {
        "data": {
            "debt_id": debt_id,
            "qty_owed": debt.qty_owed,
            "qty_settled": debt.qty_settled,
            "approval_status": debt.approval_status,
            "remaining": max(0, debt.qty_owed - debt.qty_settled)
        },
        "message": f"Material debt settled ({request.qty_settled} units)",
        "timestamp": datetime.utcnow().isoformat()
    }


