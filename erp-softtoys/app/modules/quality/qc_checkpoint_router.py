"""QC Checkpoint Router — 4-Checkpoint inline quality inspection.

Endpoints consumed by QCCheckpointPage.tsx frontend:
  POST /qc/checkpoint                           — record new inspection
  GET  /qc/checkpoint-history/{spk_id}          — history per SPK (filtered by checkpoint)
  GET  /qc/statistics/{spk_id}                  — aggregated stats per SPK
"""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.models.quality import QCCheckpoint, QCCheckpointType

router = APIRouter(
    prefix="/qc",
    tags=["QC Checkpoints"],
    responses={404: {"description": "Not found"}},
)


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class QCCheckpointCreate(BaseModel):
    spk_id: int
    checkpoint: str  # AFTER_CUTTING | AFTER_SEWING | AFTER_FINISHING | PRE_PACKING
    inspection_date: Optional[str] = None
    inspected_qty: int
    pass_qty: int
    fail_qty: int
    defect_type: Optional[str] = None
    defect_description: Optional[str] = None
    inspector_name: str
    notes: Optional[str] = None


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/checkpoint")
def create_qc_checkpoint(
    data: QCCheckpointCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Record a 4-checkpoint QC inspection for an SPK.

    Validates pass + fail == inspected, then saves to qc_checkpoints table.
    Returns the created record with computed FPY.
    """
    # Basic validation
    if data.pass_qty + data.fail_qty != data.inspected_qty:
        raise HTTPException(
            status_code=400,
            detail=f"pass_qty ({data.pass_qty}) + fail_qty ({data.fail_qty}) must equal inspected_qty ({data.inspected_qty})"
        )

    # Map checkpoint string to enum
    try:
        checkpoint_enum = QCCheckpointType(data.checkpoint)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid checkpoint: {data.checkpoint}. Must be one of: AFTER_CUTTING, AFTER_SEWING, AFTER_FINISHING, PRE_PACKING"
        )

    # Compute FPY
    fpy = round((data.pass_qty / data.inspected_qty) * 100, 2) if data.inspected_qty > 0 else 0.0

    record = QCCheckpoint(
        spk_id=data.spk_id,
        checkpoint=checkpoint_enum,
        inspection_date=data.inspection_date or str(date.today()),
        inspected_qty=data.inspected_qty,
        pass_qty=data.pass_qty,
        fail_qty=data.fail_qty,
        defect_type=data.defect_type,
        defect_description=data.defect_description,
        inspector_name=data.inspector_name,
        inspected_by=current_user.get("id"),
        notes=data.notes,
        first_pass_yield=fpy,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "spk_id": record.spk_id,
        "checkpoint": record.checkpoint.value,
        "inspection_date": record.inspection_date,
        "inspected_qty": record.inspected_qty,
        "pass_qty": record.pass_qty,
        "fail_qty": record.fail_qty,
        "defect_type": record.defect_type,
        "defect_description": record.defect_description,
        "inspector_name": record.inspector_name,
        "notes": record.notes,
        "first_pass_yield": float(record.first_pass_yield or 0),
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


@router.get("/checkpoint-history/{spk_id}")
def get_checkpoint_history(
    spk_id: int,
    checkpoint: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list:
    """Return QC checkpoint history for one SPK.

    Query params:
    - checkpoint: filter by specific checkpoint (AFTER_CUTTING etc.)
    - limit: max records to return (default 50)
    """
    q = db.query(QCCheckpoint).filter(QCCheckpoint.spk_id == spk_id)

    if checkpoint:
        try:
            cp_enum = QCCheckpointType(checkpoint)
            q = q.filter(QCCheckpoint.checkpoint == cp_enum)
        except ValueError:
            pass  # Ignore invalid checkpoint filter — return all

    records = q.order_by(QCCheckpoint.created_at.desc()).limit(limit).all()

    return [
        {
            "id": r.id,
            "spk_id": r.spk_id,
            "checkpoint": r.checkpoint.value,
            "inspection_date": r.inspection_date,
            "inspected_qty": r.inspected_qty,
            "pass_qty": r.pass_qty,
            "fail_qty": r.fail_qty,
            "defect_type": r.defect_type,
            "defect_description": r.defect_description,
            "inspector_name": r.inspector_name,
            "notes": r.notes,
            "first_pass_yield": float(r.first_pass_yield or 0),
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]


@router.get("/statistics/{spk_id}")
def get_qc_statistics(
    spk_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Return aggregated QC statistics for one SPK.

    Returns total_inspected, total_pass, total_fail, pass_percentage,
    fail_percentage, yield_rate, plus per-checkpoint breakdown.
    """
    records = db.query(QCCheckpoint).filter(QCCheckpoint.spk_id == spk_id).all()

    total_inspected = sum(r.inspected_qty for r in records)
    total_pass = sum(r.pass_qty for r in records)
    total_fail = sum(r.fail_qty for r in records)

    pass_pct = round((total_pass / total_inspected) * 100, 1) if total_inspected > 0 else 0.0
    fail_pct = round((total_fail / total_inspected) * 100, 1) if total_inspected > 0 else 0.0

    # Per-checkpoint breakdown
    breakdown: dict[str, dict] = {}
    for cp in QCCheckpointType:
        cp_records = [r for r in records if r.checkpoint == cp]
        cp_inspected = sum(r.inspected_qty for r in cp_records)
        cp_pass = sum(r.pass_qty for r in cp_records)
        cp_fail = sum(r.fail_qty for r in cp_records)
        breakdown[cp.value] = {
            "total_inspected": cp_inspected,
            "total_pass": cp_pass,
            "total_fail": cp_fail,
            "pass_rate": round((cp_pass / cp_inspected) * 100, 1) if cp_inspected > 0 else 0.0,
            "inspection_count": len(cp_records),
        }

    return {
        "spk_id": spk_id,
        "total_inspected": total_inspected,
        "total_pass": total_pass,
        "total_fail": total_fail,
        "pass_percentage": pass_pct,
        "fail_percentage": fail_pct,
        "yield_rate": pass_pct,  # FPY = pass / inspected
        "inspection_count": len(records),
        "checkpoint_breakdown": breakdown,
    }
