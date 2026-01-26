"""
API Endpoints for SPK Approval Workflow
Created: January 26, 2026
Location: app/api/v1/production/approval.py

✅ Approval workflow untuk SPK modifications & material debt
✅ Request → Pending → Approved → Applied

Endpoints:
- POST /production/spk/{spk_id}/request-modification  - Production SPV request edit
- GET /production/approvals/pending                   - Manager view pending approvals
- POST /production/approvals/{mod_id}/approve         - Manager approve/reject
- POST /production/material-debt/request              - Request material debt (negative inv)
- GET /production/material-debt/pending               - View pending debt approvals
- POST /production/material-debt/{debt_id}/approve    - Approve material debt
"""

from datetime import datetime, date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.core.models import User, SPK, SPKModification, MaterialDebt, MaterialDebtSettlement, AuditLog, Material
from app.shared.permission_service import check_permission
from app.core.logger import logger

router = APIRouter(prefix="/production", tags=["approval"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class RequestModificationRequest(BaseModel):
    """Request untuk modify SPK quantity"""
    new_qty: int
    reason: str
    notes: Optional[str] = None


class ApprovalDecisionRequest(BaseModel):
    """Approve atau reject modification"""
    approved: bool
    approval_notes: Optional[str] = None


class MaterialDebtRequest(BaseModel):
    """Request untuk material debt (negative inventory)"""
    material_id: int
    debt_qty: int
    reason: str
    notes: Optional[str] = None


class MaterialDebtSettlementRequest(BaseModel):
    """Settle material debt (ketika material arrive)"""
    received_qty: int
    notes: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _create_audit_log(db: Session, action: str, entity_type: str, entity_id: int, 
                     user_id: int, details: dict = None):
    """Create audit log entry"""
    try:
        audit = AuditLog(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            user_id=user_id,
            old_values=details.get("old") if details else None,
            new_values=details.get("new") if details else None,
            timestamp=datetime.utcnow()
        )
        db.add(audit)
        db.commit()
    except Exception as e:
        logger.error(f"Failed to create audit log: {str(e)}")


# ============================================================================
# ENDPOINT 1: Request SPK Modification
# ============================================================================
@router.post("/spk/{spk_id}/request-modification")
async def request_spk_modification(
    spk_id: int,
    request: RequestModificationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Production SPV request to modify SPK quantity
    ✅ Triggers manager approval workflow
    
    Permission: PRODUCTION_SPV, PRODUCTION_MANAGER
    
    Request:
    {
        "new_qty": 450,
        "reason": "Customer reduced order",
        "notes": "Will affect packing"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "modification_id": "MOD-001",
            "spk_id": 1,
            "old_qty": 500,
            "new_qty": 450,
            "change": "-50 units",
            "status": "PENDING",
            "requested_by": "SPV001",
            "requested_at": "2026-01-26T10:30:00",
            "message": "✅ Modification request submitted for approval"
        }
    }
    """
    # Permission check
    await check_permission(current_user, "PRODUCTION", "MODIFY", db)
    
    # Verify SPK exists
    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"SPK {spk_id} not found"
        )
    
    # Validation
    if request.new_qty <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New quantity must be positive"
        )
    
    if request.new_qty == spk.original_qty:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New quantity same as original, no change needed"
        )
    
    try:
        # Create modification record
        modification = SPKModification(
            spk_id=spk_id,
            old_qty=spk.original_qty,
            new_qty=request.new_qty,
            field_name="original_qty",
            modification_reason=request.reason,
            modified_by=current_user.id,
            modified_at=datetime.utcnow(),
            approval_status="PENDING"
        )
        db.add(modification)
        db.commit()
        
        # Create audit log
        _create_audit_log(
            db, "REQUEST_MODIFICATION", "SPK", spk_id, current_user.id,
            {"old": spk.original_qty, "new": request.new_qty}
        )
        
        logger.info(f"SPK modification requested: SPK{spk_id}, {spk.original_qty}→{request.new_qty}")
        
        return {
            "success": True,
            "data": {
                "modification_id": f"MOD-{modification.id}",
                "spk_id": spk_id,
                "old_qty": spk.original_qty,
                "new_qty": request.new_qty,
                "change": f"{'-' if request.new_qty < spk.original_qty else '+'}{abs(request.new_qty - spk.original_qty)} units",
                "status": "PENDING",
                "requested_by": current_user.username,
                "requested_at": datetime.utcnow().isoformat(),
                "reason": request.reason,
                "message": "✅ Modification request submitted for approval"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error requesting modification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create modification request"
        )


# ============================================================================
# ENDPOINT 2: Get Pending Approvals (Manager View)
# ============================================================================
@router.get("/approvals/pending")
async def get_pending_approvals(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Manager/Supervisor view pending approvals
    ✅ Show modifications waiting for approval
    
    Permission: PRODUCTION_MANAGER, MANAGER
    
    Response:
    {
        "success": true,
        "data": {
            "approvals": [
                {
                    "modification_id": "MOD-001",
                    "spk_id": 1,
                    "old_qty": 500,
                    "new_qty": 450,
                    "requested_by": "SPV001",
                    "requested_at": "2026-01-26T10:30:00",
                    "reason": "Customer reduced order"
                }
            ],
            "count": 5,
            "page": 1,
            "limit": 20
        }
    }
    """
    # Permission check
    await check_permission(current_user, "PRODUCTION", "APPROVE", db)
    
    try:
        # Get pending modifications
        offset = (page - 1) * limit
        modifications = db.query(SPKModification).filter(
            SPKModification.approval_status == "PENDING"
        ).offset(offset).limit(limit).all()
        
        total = db.query(SPKModification).filter(
            SPKModification.approval_status == "PENDING"
        ).count()
        
        approvals = []
        for mod in modifications:
            spk = db.query(SPK).filter(SPK.id == mod.spk_id).first()
            requester = db.query(User).filter(User.id == mod.modified_by).first()
            
            approvals.append({
                "modification_id": f"MOD-{mod.id}",
                "spk_id": mod.spk_id,
                "spk_number": spk.spk_number if hasattr(spk, 'spk_number') else f"SPK-{spk.id}",
                "old_qty": mod.old_qty,
                "new_qty": mod.new_qty,
                "change": f"{'-' if mod.new_qty < mod.old_qty else '+'}{abs(mod.new_qty - mod.old_qty)} units",
                "requested_by": requester.username if requester else "Unknown",
                "requested_at": mod.modified_at.isoformat() if mod.modified_at else None,
                "reason": mod.modification_reason,
                "notes": mod.notes if hasattr(mod, 'notes') else None
            })
        
        logger.info(f"Manager viewed {len(approvals)} pending approvals")
        
        return {
            "success": True,
            "data": {
                "approvals": approvals,
                "count": total,
                "page": page,
                "limit": limit
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching pending approvals: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending approvals"
        )


# ============================================================================
# ENDPOINT 3: Approve/Reject Modification
# ============================================================================
@router.post("/approvals/{mod_id}/approve")
async def approve_modification(
    mod_id: int,
    request: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Manager approve atau reject modification
    ✅ If approved: SPK quantity updated
    
    Permission: PRODUCTION_MANAGER, MANAGER
    
    Request:
    {
        "approved": true,
        "approval_notes": "Approved by manager"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "modification_id": "MOD-001",
            "approval_status": "APPROVED",
            "spk_id": 1,
            "qty_updated": true,
            "message": "✅ SPK quantity updated to 450"
        }
    }
    """
    # Permission check
    await check_permission(current_user, "PRODUCTION", "APPROVE", db)
    
    try:
        # Get modification
        modification = db.query(SPKModification).filter(
            SPKModification.id == mod_id
        ).first()
        
        if not modification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Modification {mod_id} not found"
            )
        
        if modification.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Modification already {modification.approval_status.lower()}"
            )
        
        # Get SPK
        spk = db.query(SPK).filter(SPK.id == modification.spk_id).first()
        if not spk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SPK {modification.spk_id} not found"
            )
        
        if request.approved:
            # Approve & apply modification
            modification.approval_status = "APPROVED"
            modification.approved_by = current_user.id
            modification.approved_at = datetime.utcnow()
            
            # Update SPK
            spk.original_qty = modification.new_qty
            if hasattr(spk, 'modified_qty'):
                spk.modified_qty = modification.new_qty
            
            message = f"✅ SPK quantity updated to {modification.new_qty}"
            
            # Create audit log
            _create_audit_log(
                db, "APPROVE_MODIFICATION", "SPK", spk.id, current_user.id,
                {"old": modification.old_qty, "new": modification.new_qty}
            )
            
            logger.info(f"Modification {mod_id} APPROVED, SPK{spk.id} updated")
            
        else:
            # Reject modification
            modification.approval_status = "REJECTED"
            modification.approved_by = current_user.id
            modification.approved_at = datetime.utcnow()
            
            message = "❌ Modification rejected"
            
            logger.info(f"Modification {mod_id} REJECTED")
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "modification_id": f"MOD-{modification.id}",
                "approval_status": modification.approval_status,
                "spk_id": modification.spk_id,
                "qty_updated": request.approved,
                "approved_by": current_user.username,
                "message": message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving modification: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process approval"
        )


# ============================================================================
# ENDPOINT 4: Request Material Debt
# ============================================================================
@router.post("/material-debt/request")
async def request_material_debt(
    spk_id: int,
    request: MaterialDebtRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Production staff request material debt (negative inventory)
    ✅ When materials not available, production continues anyway
    ✅ Requires manager approval
    
    Permission: PRODUCTION_STAFF, PRODUCTION_SPV
    
    Request:
    {
        "material_id": 5,
        "debt_qty": 100,
        "reason": "Material not available yet, supplier delayed"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "debt_id": "DEBT-001",
            "spk_id": 1,
            "material_id": 5,
            "debt_qty": 100,
            "status": "PENDING",
            "message": "✅ Material debt request submitted"
        }
    }
    """
    # Permission check
    await check_permission(current_user, "PRODUCTION", "INPUT", db)
    
    try:
        # Verify SPK exists
        spk = db.query(SPK).filter(SPK.id == spk_id).first()
        if not spk:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"SPK {spk_id} not found"
            )
        
        # Verify material exists
        material = db.query(Material).filter(Material.id == request.material_id).first()
        if not material:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Material {request.material_id} not found"
            )
        
        # Validation
        if request.debt_qty <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Debt quantity must be positive"
            )
        
        # Create material debt record
        debt = MaterialDebt(
            spk_id=spk_id,
            material_id=request.material_id,
            debt_qty=request.debt_qty,
            reason=request.reason,
            requested_by=current_user.id,
            requested_at=datetime.utcnow(),
            approval_status="PENDING"
        )
        db.add(debt)
        db.commit()
        
        # Create audit log
        _create_audit_log(
            db, "REQUEST_MATERIAL_DEBT", "SPK", spk_id, current_user.id,
            {"material_id": request.material_id, "qty": request.debt_qty}
        )
        
        logger.info(f"Material debt requested: SPK{spk_id}, Material{request.material_id}, Qty:{request.debt_qty}")
        
        return {
            "success": True,
            "data": {
                "debt_id": f"DEBT-{debt.id}",
                "spk_id": spk_id,
                "material_id": request.material_id,
                "material_name": material.name if hasattr(material, 'name') else "Unknown",
                "debt_qty": request.debt_qty,
                "status": "PENDING",
                "reason": request.reason,
                "message": "✅ Material debt request submitted for approval"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error requesting material debt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create material debt request"
        )


# ============================================================================
# ENDPOINT 5: Get Pending Material Debt Approvals
# ============================================================================
@router.get("/material-debt/pending")
async def get_pending_material_debts(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Manager view pending material debt approvals
    
    Permission: PRODUCTION_MANAGER, MANAGER
    
    Response:
    {
        "success": true,
        "data": {
            "debts": [
                {
                    "debt_id": "DEBT-001",
                    "spk_id": 1,
                    "material": "Cotton Thread",
                    "debt_qty": 100,
                    "requested_by": "STAFF001",
                    "requested_at": "2026-01-26T10:30:00",
                    "reason": "Supplier delayed"
                }
            ],
            "count": 3,
            "page": 1
        }
    }
    """
    # Permission check
    await check_permission(current_user, "PRODUCTION", "APPROVE", db)
    
    try:
        offset = (page - 1) * limit
        debts = db.query(MaterialDebt).filter(
            MaterialDebt.approval_status == "PENDING"
        ).offset(offset).limit(limit).all()
        
        total = db.query(MaterialDebt).filter(
            MaterialDebt.approval_status == "PENDING"
        ).count()
        
        debt_list = []
        for debt in debts:
            material = db.query(Material).filter(Material.id == debt.material_id).first()
            requester = db.query(User).filter(User.id == debt.requested_by).first()
            
            debt_list.append({
                "debt_id": f"DEBT-{debt.id}",
                "spk_id": debt.spk_id,
                "material_id": debt.material_id,
                "material": material.name if material and hasattr(material, 'name') else "Unknown",
                "debt_qty": debt.debt_qty,
                "requested_by": requester.username if requester else "Unknown",
                "requested_at": debt.requested_at.isoformat() if hasattr(debt, 'requested_at') else None,
                "reason": debt.reason if hasattr(debt, 'reason') else None
            })
        
        logger.info(f"Manager viewed {len(debt_list)} pending material debts")
        
        return {
            "success": True,
            "data": {
                "debts": debt_list,
                "count": total,
                "page": page,
                "limit": limit
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error fetching pending material debts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch pending material debts"
        )


# ============================================================================
# ENDPOINT 6: Approve Material Debt
# ============================================================================
@router.post("/material-debt/{debt_id}/approve")
async def approve_material_debt(
    debt_id: int,
    request: ApprovalDecisionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Manager approve material debt
    ✅ Allows production to continue with negative inventory
    
    Permission: PRODUCTION_MANAGER, MANAGER
    
    Request:
    {
        "approved": true,
        "approval_notes": "Approved, supplier ETA 1/27"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "debt_id": "DEBT-001",
            "approval_status": "APPROVED",
            "approved_by": "MGR001",
            "message": "✅ Material debt approved"
        }
    }
    """
    # Permission check
    await check_permission(current_user, "PRODUCTION", "APPROVE", db)
    
    try:
        # Get material debt
        debt = db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
        if not debt:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Material debt {debt_id} not found"
            )
        
        if debt.approval_status != "PENDING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Debt already {debt.approval_status.lower()}"
            )
        
        if request.approved:
            debt.approval_status = "APPROVED"
            message = "✅ Material debt approved"
            logger.info(f"Material debt {debt_id} APPROVED")
        else:
            debt.approval_status = "REJECTED"
            message = "❌ Material debt rejected"
            logger.info(f"Material debt {debt_id} REJECTED")
        
        debt.approved_by = current_user.id
        debt.approved_at = datetime.utcnow()
        
        # Create audit log
        _create_audit_log(
            db, "APPROVE_MATERIAL_DEBT", "MATERIAL_DEBT", debt.id, current_user.id,
            {"status": debt.approval_status}
        )
        
        db.commit()
        
        return {
            "success": True,
            "data": {
                "debt_id": f"DEBT-{debt.id}",
                "approval_status": debt.approval_status,
                "approved_by": current_user.username,
                "message": message
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving material debt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process material debt approval"
        )
