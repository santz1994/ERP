"""Material Debt API Endpoints - Phase 2C

REST API for material debt tracking and settlement
Exposes material debt operations to frontend

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.models.user import User
from app.modules.warehouse.material_debt_service import MaterialDebtService


router = APIRouter(prefix="/material-debts", tags=["Material Debt"])


# Pydantic Schemas
class MaterialDebtCreate(BaseModel):
    """Request schema for creating material debt"""

    product_id: int = Field(..., description="Material with negative stock")
    debt_qty: Decimal = Field(..., gt=0, description="Debt quantity")
    uom: str = Field(..., max_length=10, description="Unit of measure")
    reference_doc: str = Field(
        ..., max_length=100, description="SPK or transaction ref"
    )
    spk_id: Optional[int] = Field(None, description="Optional SPK ID")
    estimated_cost: Optional[Decimal] = Field(
        None, description="Estimated cost"
    )
    risk_level: str = Field(
        "MEDIUM", description="LOW/MEDIUM/HIGH/CRITICAL"
    )


class DebtSettlementCreate(BaseModel):
    """Request schema for settling debt"""

    settlement_qty: Decimal = Field(..., gt=0, description="Quantity to settle")
    po_id: Optional[int] = Field(None, description="PO reference")
    po_line_id: Optional[int] = Field(None, description="PO line reference")
    grn_number: Optional[str] = Field(
        None, max_length=50, description="GRN number"
    )
    notes: Optional[str] = Field(None, description="Settlement notes")


class AutoSettleRequest(BaseModel):
    """Request schema for auto-settlement from GRN"""

    product_id: int = Field(..., description="Material received")
    received_qty: Decimal = Field(..., gt=0, description="GRN quantity")
    po_id: int = Field(..., description="PO reference")
    po_line_id: Optional[int] = Field(None, description="PO line reference")
    grn_number: Optional[str] = Field(
        None, max_length=50, description="GRN number"
    )


class RiskUpdateRequest(BaseModel):
    """Request schema for updating risk level"""

    risk_level: str = Field(..., description="NEW risk level")
    notes: Optional[str] = Field(None, description="Reason for update")


class WriteOffRequest(BaseModel):
    """Request schema for writing off debt"""

    reason: str = Field(..., description="Reason for write-off")


# API Endpoints
@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_material_debt(
    request: MaterialDebtCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create material debt record (negative stock situation)

    Creates debt when stock goes negative due to production using
    materials before PO received.

    **Business Flow:**
    1. Stock checker detects negative stock
    2. Debt created with reference to SPK
    3. Risk level assessed (LOW/MEDIUM/HIGH/CRITICAL)
    4. Financial impact estimated
    5. Triggers alert to purchasing team
    """
    try:
        service = MaterialDebtService(db)
        debt = service.create_debt(
            product_id=request.product_id,
            debt_qty=request.debt_qty,
            uom=request.uom,
            reference_doc=request.reference_doc,
            spk_id=request.spk_id,
            user_id=current_user.id,
            estimated_cost=request.estimated_cost,
            risk_level=request.risk_level,
        )

        return {
            "success": True,
            "message": "Material debt created",
            "data": {
                "debt_id": debt.id,
                "product_id": debt.product_id,
                "balance_qty": float(debt.balance_qty),
                "uom": debt.uom,
                "status": debt.status.value,
                "risk_level": debt.risk_level,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post(
    "/{debt_id}/settle",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
)
async def settle_debt(
    debt_id: int,
    request: DebtSettlementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Settle material debt (apply GRN receipt)

    Applies received material quantity to outstanding debt.
    Can be partial or full settlement.

    **Business Flow:**
    1. GRN received from supplier
    2. Settlement applied to oldest debt (FIFO)
    3. Debt balance updated
    4. Status changed to PARTIAL_PAID or FULLY_PAID
    5. Financial tracking updated
    """
    try:
        service = MaterialDebtService(db)
        settlement = service.settle_debt(
            debt_id=debt_id,
            settlement_qty=request.settlement_qty,
            po_id=request.po_id,
            po_line_id=request.po_line_id,
            grn_number=request.grn_number,
            user_id=current_user.id,
            auto_settled=False,
            notes=request.notes,
        )

        # Refresh debt to get updated status
        debt = db.query(
            service.db.query(
                service.db.query.__self__.__class__
            ).__self__.MaterialDebt
        ).get(debt_id)

        return {
            "success": True,
            "message": "Debt settlement applied",
            "data": {
                "settlement_id": settlement.id,
                "debt_id": debt_id,
                "settled_qty": float(settlement.settlement_qty),
                "remaining_balance": float(debt.balance_qty),
                "debt_status": debt.status.value,
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/auto-settle", response_model=dict)
async def auto_settle_debts(
    request: AutoSettleRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Auto-settle debts from GRN (FIFO)

    Automatically applies GRN receipt to outstanding debts
    for the material, oldest debts first (FIFO).

    **Business Flow:**
    1. GRN created in system
    2. System finds active debts for material
    3. Applies received qty to debts (oldest first)
    4. Creates settlement records
    5. Updates debt balances
    6. Returns list of settlements created
    """
    try:
        service = MaterialDebtService(db)
        settlements = service.auto_settle_from_grn(
            product_id=request.product_id,
            received_qty=request.received_qty,
            po_id=request.po_id,
            po_line_id=request.po_line_id,
            grn_number=request.grn_number,
            user_id=current_user.id,
        )

        return {
            "success": True,
            "message": f"Auto-settled {len(settlements)} debt(s)",
            "data": {
                "settlements_count": len(settlements),
                "settlements": [
                    {
                        "settlement_id": s.id,
                        "debt_id": s.debt_id,
                        "settled_qty": float(s.settlement_qty),
                    }
                    for s in settlements
                ],
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/active", response_model=dict)
async def get_active_debts(
    product_id: Optional[int] = Query(
        None, description="Filter by material"
    ),
    risk_level: Optional[str] = Query(
        None, description="Filter by risk level"
    ),
    min_balance: Optional[Decimal] = Query(
        None, description="Minimum balance"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get list of active/partial debts

    Returns all outstanding material debts with filters.

    **Use Cases:**
    - Dashboard: Show critical debts
    - Purchasing: Materials needing urgent PO
    - Finance: Total debt exposure
    - Production: At-risk materials
    """
    try:
        service = MaterialDebtService(db)
        debts = service.get_active_debts(
            product_id=product_id,
            risk_level=risk_level,
            min_balance=min_balance,
        )

        return {
            "success": True,
            "total": len(debts),
            "data": [
                {
                    "debt_id": d.id,
                    "product_id": d.product_id,
                    "total_debt": float(d.total_debt_qty),
                    "settled": float(d.settled_qty),
                    "balance": float(d.balance_qty),
                    "uom": d.uom,
                    "status": d.status.value,
                    "risk_level": d.risk_level,
                    "estimated_cost": (
                        float(d.estimated_cost)
                        if d.estimated_cost
                        else None
                    ),
                    "reference": d.reference_doc,
                    "created_at": d.created_at.isoformat(),
                }
                for d in debts
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/summary", response_model=dict)
async def get_debt_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get debt summary statistics

    Returns high-level overview of debt situation.

    **Dashboard Metrics:**
    - Total active debts count
    - Total financial exposure
    - Breakdown by risk level
    - Top 10 materials with debt
    """
    try:
        service = MaterialDebtService(db)
        summary = service.get_debt_summary()

        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/{debt_id}/risk", response_model=dict)
async def update_debt_risk(
    debt_id: int,
    request: RiskUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update debt risk level

    Changes risk assessment based on new information.

    **Use Cases:**
    - Escalate to CRITICAL if PO delayed
    - Downgrade to LOW if rush PO confirmed
    - Update based on production impact assessment
    """
    try:
        service = MaterialDebtService(db)
        debt = service.update_risk_level(
            debt_id=debt_id,
            new_risk_level=request.risk_level,
            notes=request.notes,
        )

        return {
            "success": True,
            "message": "Risk level updated",
            "data": {
                "debt_id": debt.id,
                "new_risk_level": debt.risk_level,
                "balance": float(debt.balance_qty),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/{debt_id}/write-off", response_model=dict)
async def write_off_debt(
    debt_id: int,
    request: WriteOffRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Write off debt (cancel/void)

    Marks debt as WRITTEN_OFF (no longer expected to be settled).

    **Use Cases:**
    - Material substitution (used different material)
    - Process change (no longer needed)
    - Supplier failure (never received)
    - Management decision to absorb loss

    **Note:** Requires proper authorization/approval workflow
    """
    try:
        service = MaterialDebtService(db)
        debt = service.write_off_debt(
            debt_id=debt_id, reason=request.reason, user_id=current_user.id
        )

        return {
            "success": True,
            "message": "Debt written off",
            "data": {
                "debt_id": debt.id,
                "status": debt.status.value,
                "balance_written_off": float(debt.balance_qty),
            },
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{debt_id}", response_model=dict)
async def get_debt_detail(
    debt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get detailed debt information with settlement history

    Returns complete debt record including all settlements.
    """
    try:
        from app.core.models.material_debt import MaterialDebt

        debt = db.query(MaterialDebt).get(debt_id)
        if not debt:
            raise HTTPException(
                status_code=404, detail=f"Debt {debt_id} not found"
            )

        return {
            "success": True,
            "data": {
                "debt_id": debt.id,
                "product_id": debt.product_id,
                "total_debt": float(debt.total_debt_qty),
                "settled": float(debt.settled_qty),
                "balance": float(debt.balance_qty),
                "uom": debt.uom,
                "status": debt.status.value,
                "risk_level": debt.risk_level,
                "estimated_cost": (
                    float(debt.estimated_cost)
                    if debt.estimated_cost
                    else None
                ),
                "rush_cost": float(debt.rush_order_cost),
                "total_cost": (
                    float(debt.total_cost_impact)
                    if debt.total_cost_impact
                    else None
                ),
                "reference": debt.reference_doc,
                "spk_id": debt.spk_id,
                "created_at": debt.created_at.isoformat(),
                "resolved_at": (
                    debt.resolved_at.isoformat()
                    if debt.resolved_at
                    else None
                ),
                "settlements": [
                    {
                        "settlement_id": s.id,
                        "qty": float(s.settlement_qty),
                        "po_id": s.po_id,
                        "grn_number": s.grn_number,
                        "auto_settled": s.auto_settled,
                        "date": s.settlement_date.isoformat(),
                    }
                    for s in debt.settlements
                ],
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
