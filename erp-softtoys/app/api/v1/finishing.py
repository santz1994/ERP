"""Warehouse Finishing API v1 - Phase 2A

FastAPI endpoints for warehouse finishing operations (2-stage process)

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models.manufacturing import SPK
from app.modules.finishing.finishing_service import FinishingService
from app.shared.schemas.manufacturing import SPKResponse

# Create router
router = APIRouter(prefix="/api/v1/finishing", tags=["Finishing"])


# ============================================================================
# Stage 1 (Stuffing) Endpoints
# ============================================================================


@router.post("/stage1-spk", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_stage1_spk(
    mo_id: int,
    target_qty: Decimal,
    buffer_pct: Decimal = Decimal("0"),
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Create Stage 1 (Stuffing) SPK for Warehouse Finishing

    Request body:
    {
        "mo_id": 1,
        "target_qty": 1000,
        "buffer_pct": 0,
        "user_id": 5
    }
    """
    try:
        service = FinishingService(db)
        spk = service.create_stage1_spk(
            mo_id=mo_id,
            target_qty=target_qty,
            buffer_pct=buffer_pct,
            user_id=user_id,
        )

        return {
            "id": spk.id,
            "mo_id": spk.mo_id,
            "stage": "Stuffing",
            "target_qty": int(spk.target_qty),
            "status": spk.production_status,
            "created_at": spk.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stage1-input", response_model=dict, status_code=status.HTTP_201_CREATED)
async def input_stage1_result(
    spk_id: int,
    input_qty: Decimal,
    good_qty: Decimal,
    defect_qty: Decimal,
    rework_qty: Decimal,
    filling_consumed: Decimal,
    operator_id: int,
    production_date: Optional[date] = None,
    notes: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Record Stage 1 (Stuffing) completion

    Request body:
    {
        "spk_id": 1,
        "input_qty": 1000,
        "good_qty": 950,
        "defect_qty": 30,
        "rework_qty": 20,
        "filling_consumed": 15.5,
        "operator_id": 3,
        "notes": "Normal production run"
    }
    """
    try:
        if (good_qty + defect_qty + rework_qty) != input_qty:
            raise ValueError(
                f"Sum of output ({good_qty + defect_qty + rework_qty}) "
                f"must equal input quantity ({input_qty})"
            )

        service = FinishingService(db)
        io_record = service.input_stage1_result(
            spk_id=spk_id,
            input_qty=input_qty,
            good_qty=good_qty,
            defect_qty=defect_qty,
            rework_qty=rework_qty,
            filling_consumed=filling_consumed,
            operator_id=operator_id,
            production_date=production_date,
            notes=notes,
            user_id=user_id,
        )

        return {
            "id": io_record.id,
            "spk_id": spk_id,
            "stage": "Stuffing",
            "production_date": io_record.production_date,
            "input_qty": int(input_qty),
            "good_qty": int(good_qty),
            "defect_qty": int(defect_qty),
            "yield_rate": float(io_record.yield_rate),
            "filling_kg": float(filling_consumed),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Stage 2 (Closing) Endpoints
# ============================================================================


@router.post("/stage2-spk", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_stage2_spk(
    stage1_spk_id: int,
    target_qty: Decimal,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Create Stage 2 (Closing) SPK based on Stage 1 output

    Request body:
    {
        "stage1_spk_id": 1,
        "target_qty": 950,
        "user_id": 5
    }
    """
    try:
        service = FinishingService(db)
        spk = service.create_stage2_spk(
            stage1_spk_id=stage1_spk_id,
            target_qty=target_qty,
            user_id=user_id,
        )

        return {
            "id": spk.id,
            "mo_id": spk.mo_id,
            "stage": "Closing",
            "target_qty": int(spk.target_qty),
            "status": spk.production_status,
            "linked_to_stage1": stage1_spk_id,
            "created_at": spk.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stage2-input", response_model=dict, status_code=status.HTTP_201_CREATED)
async def input_stage2_result(
    spk_id: int,
    input_qty: Decimal,
    good_qty: Decimal,
    defect_qty: Decimal,
    rework_qty: Decimal,
    thread_consumed: Decimal,
    operator_id: int,
    production_date: Optional[date] = None,
    notes: Optional[str] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """Record Stage 2 (Closing) completion

    Request body:
    {
        "spk_id": 2,
        "input_qty": 950,
        "good_qty": 920,
        "defect_qty": 20,
        "rework_qty": 10,
        "thread_consumed": 2850.5,
        "operator_id": 4,
        "notes": "High quality run"
    }
    """
    try:
        if (good_qty + defect_qty + rework_qty) != input_qty:
            raise ValueError(
                f"Sum of output ({good_qty + defect_qty + rework_qty}) "
                f"must equal input quantity ({input_qty})"
            )

        service = FinishingService(db)
        io_record = service.input_stage2_result(
            spk_id=spk_id,
            input_qty=input_qty,
            good_qty=good_qty,
            defect_qty=defect_qty,
            rework_qty=rework_qty,
            thread_consumed=thread_consumed,
            operator_id=operator_id,
            production_date=production_date,
            notes=notes,
            user_id=user_id,
        )

        return {
            "id": io_record.id,
            "spk_id": spk_id,
            "stage": "Closing",
            "production_date": io_record.production_date,
            "input_qty": int(input_qty),
            "good_qty": int(good_qty),
            "defect_qty": int(defect_qty),
            "yield_rate": float(io_record.yield_rate),
            "thread_m": float(thread_consumed),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
