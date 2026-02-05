"""Rework & QC API v1 - Phase 2B

FastAPI endpoints for rework and quality control operations

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.manufacturing.rework_service import ReworkService

# Create router
router = APIRouter(prefix="/api/v1/rework", tags=["Rework"])


# ============================================================================
# Rework Request Management
# ============================================================================


@router.post("/request", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_rework_request(
    spk_id: int,
    defect_qty: Decimal,
    defect_category_id: int,
    defect_notes: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Create rework request for defective units

    Request body:
    {
        "spk_id": 1,
        "defect_qty": 30,
        "defect_category_id": 1,
        "defect_notes": "Broken stitches on seam",
        "user_id": 5
    }
    """
    try:
        service = ReworkService(db)
        rework = service.create_rework_request(
            spk_id=spk_id,
            defect_qty=defect_qty,
            defect_category_id=defect_category_id,
            defect_notes=defect_notes,
            requested_by_id=user_id,
            user_id=user_id,
        )

        return {
            "id": rework.id,
            "spk_id": rework.spk_id,
            "defect_qty": int(defect_qty),
            "status": rework.status,
            "created_at": rework.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/{rework_id}/approve", response_model=dict)
async def approve_rework(
    rework_id: int,
    approval_notes: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Approve rework request (QC Manager action)

    Request body:
    {
        "rework_id": 1,
        "approval_notes": "Approved for rework",
        "user_id": 2
    }
    """
    try:
        service = ReworkService(db)
        rework = service.approve_rework(
            rework_id=rework_id,
            qc_approval_notes=approval_notes,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "approved_at": rework.qc_reviewed_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/{rework_id}/reject", response_model=dict)
async def reject_rework(
    rework_id: int,
    rejection_reason: str,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Reject rework request (discard instead)

    Request body:
    {
        "rework_id": 1,
        "rejection_reason": "Severe damage, not economical to rework",
        "user_id": 2
    }
    """
    try:
        service = ReworkService(db)
        rework = service.reject_rework(
            rework_id=rework_id,
            rejection_reason=rejection_reason,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "rejected_at": rework.qc_reviewed_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/{rework_id}/start", response_model=dict)
async def start_rework(
    rework_id: int,
    operator_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Start rework process (Operator action)

    Request body:
    {
        "rework_id": 1,
        "operator_id": 3,
        "user_id": 3
    }
    """
    try:
        service = ReworkService(db)
        rework = service.start_rework(
            rework_id=rework_id,
            operator_id=operator_id,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "started_at": rework.rework_started_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/{rework_id}/complete", response_model=dict)
async def complete_rework(
    rework_id: int,
    rework_notes: Optional[str] = None,
    material_cost: Decimal = Decimal("0"),
    labor_cost: Decimal = Decimal("0"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Complete rework process (Operator action)

    Request body:
    {
        "rework_id": 1,
        "rework_notes": "Fixed broken stitches",
        "material_cost": 5000,
        "labor_cost": 10000,
        "user_id": 3
    }
    """
    try:
        service = ReworkService(db)
        rework = service.complete_rework(
            rework_id=rework_id,
            rework_notes=rework_notes,
            material_cost=material_cost,
            labor_cost=labor_cost,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "completed_at": rework.rework_completed_at,
            "total_cost": float(rework.total_cost),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/request/{rework_id}/verify", response_model=dict)
async def verify_rework(
    rework_id: int,
    verified_good_qty: Decimal,
    verified_failed_qty: Decimal,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Final QC verification (QC Manager action)

    Request body:
    {
        "rework_id": 1,
        "verified_good_qty": 28,
        "verified_failed_qty": 2,
        "user_id": 2
    }
    """
    try:
        if (verified_good_qty + verified_failed_qty) == 0:
            raise ValueError("Total verified quantities must be greater than 0")

        service = ReworkService(db)
        rework = service.verify_rework(
            rework_id=rework_id,
            verified_good_qty=verified_good_qty,
            verified_failed_qty=verified_failed_qty,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "verified_at": rework.verified_at,
            "good_qty": int(verified_good_qty),
            "failed_qty": int(verified_failed_qty),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Rework Material Management
# ============================================================================


@router.post("/material", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_rework_material(
    rework_id: int,
    product_id: int,
    qty_used: Decimal,
    uom: str,
    unit_cost: Decimal,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Add material consumed during rework

    Request body:
    {
        "rework_id": 1,
        "product_id": 10,
        "qty_used": 5,
        "uom": "PIECES",
        "unit_cost": 2000,
        "user_id": 3
    }
    """
    try:
        service = ReworkService(db)
        material = service.add_rework_material(
            rework_id=rework_id,
            product_id=product_id,
            qty_used=qty_used,
            uom=uom,
            unit_cost=unit_cost,
            user_id=user_id,
        )
        return {
            "id": material.id,
            "rework_id": rework_id,
            "product_id": product_id,
            "qty": float(qty_used),
            "uom": uom,
            "unit_cost": float(unit_cost),
            "total_cost": float(material.total_cost),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
