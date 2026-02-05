"""Material Debt Service - Phase 2C

Business logic for material debt tracking and settlement
Manages negative stock situations and automatic debt resolution

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.core.models.material_debt import (
    MaterialDebt,
    MaterialDebtSettlement,
    MaterialDebtStatus,
)
from app.core.models.warehouse import Product, PurchaseOrder, PurchaseOrderLine
from app.core.models.manufacturing import SPK


class MaterialDebtService:
    """Business logic for material debt operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_debt(
        self,
        product_id: int,
        debt_qty: Decimal,
        uom: str,
        reference_doc: str,
        spk_id: Optional[int] = None,
        user_id: Optional[int] = None,
        estimated_cost: Optional[Decimal] = None,
        risk_level: str = "MEDIUM",
    ) -> MaterialDebt:
        """Create material debt record when stock goes negative

        Args:
            product_id: Material with negative stock
            debt_qty: Amount of debt (absolute value)
            uom: Unit of measure
            reference_doc: SPK or transaction reference
            spk_id: Optional SPK that caused debt
            user_id: User recording debt
            estimated_cost: Estimated financial impact
            risk_level: LOW/MEDIUM/HIGH/CRITICAL

        Returns:
            Created MaterialDebt

        Raises:
            ValueError: If product not found or debt_qty <= 0
        """
        # Validate product exists
        product = self.db.query(Product).get(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if debt_qty <= 0:
            raise ValueError("Debt quantity must be positive")

        # Calculate cost if not provided
        if estimated_cost is None and hasattr(product, "standard_cost"):
            estimated_cost = debt_qty * product.standard_cost

        # Create debt record
        debt = MaterialDebt(
            product_id=product_id,
            uom=uom,
            total_debt_qty=debt_qty,
            settled_qty=Decimal(0),
            balance_qty=debt_qty,
            status=MaterialDebtStatus.ACTIVE,
            spk_id=spk_id,
            reference_doc=reference_doc,
            estimated_cost=estimated_cost,
            total_cost_impact=estimated_cost,
            risk_level=risk_level,
            created_by_id=user_id,
        )

        self.db.add(debt)
        self.db.commit()
        self.db.refresh(debt)

        return debt

    def settle_debt(
        self,
        debt_id: int,
        settlement_qty: Decimal,
        po_id: Optional[int] = None,
        po_line_id: Optional[int] = None,
        grn_number: Optional[str] = None,
        user_id: Optional[int] = None,
        auto_settled: bool = False,
        notes: Optional[str] = None,
    ) -> MaterialDebtSettlement:
        """Apply settlement to debt (when GRN received)

        Args:
            debt_id: Debt to settle
            settlement_qty: Quantity received to apply
            po_id: Optional PO reference
            po_line_id: Optional PO line reference
            grn_number: GRN number
            user_id: User processing settlement
            auto_settled: True if automatically applied
            notes: Optional settlement notes

        Returns:
            Created MaterialDebtSettlement

        Raises:
            ValueError: If debt not found or settlement exceeds balance
        """
        debt = self.db.query(MaterialDebt).get(debt_id)
        if not debt:
            raise ValueError(f"MaterialDebt {debt_id} not found")

        if debt.status == MaterialDebtStatus.FULLY_PAID:
            raise ValueError("Debt already fully paid")

        if settlement_qty > debt.balance_qty:
            raise ValueError(
                f"Settlement qty ({settlement_qty}) exceeds "
                f"balance ({debt.balance_qty})"
            )

        # Create settlement record
        settlement = MaterialDebtSettlement(
            debt_id=debt_id,
            settlement_qty=settlement_qty,
            po_id=po_id,
            po_line_id=po_line_id,
            grn_number=grn_number,
            settled_by_id=user_id,
            auto_settled=auto_settled,
            notes=notes,
        )

        self.db.add(settlement)

        # Update debt balance
        debt.settled_qty += settlement_qty  # type: ignore
        debt.balance_qty -= settlement_qty  # type: ignore

        # Update status based on balance
        if debt.balance_qty == 0:
            debt.status = MaterialDebtStatus.FULLY_PAID  # type: ignore
            debt.resolved_by_id = user_id  # type: ignore
            debt.resolved_at = datetime.utcnow()  # type: ignore
        elif debt.settled_qty > 0:
            debt.status = MaterialDebtStatus.PARTIAL_PAID  # type: ignore

        self.db.commit()
        self.db.refresh(settlement)
        self.db.refresh(debt)

        return settlement

    def get_active_debts(
        self,
        product_id: Optional[int] = None,
        risk_level: Optional[str] = None,
        min_balance: Optional[Decimal] = None,
    ) -> List[MaterialDebt]:
        """Get list of active/partial debts

        Args:
            product_id: Filter by specific material
            risk_level: Filter by risk level
            min_balance: Minimum balance to include

        Returns:
            List of MaterialDebt records
        """
        query = self.db.query(MaterialDebt).filter(
            or_(
                MaterialDebt.status == MaterialDebtStatus.ACTIVE,
                MaterialDebt.status == MaterialDebtStatus.PARTIAL_PAID,
            )
        )

        if product_id:
            query = query.filter(MaterialDebt.product_id == product_id)

        if risk_level:
            query = query.filter(MaterialDebt.risk_level == risk_level)

        if min_balance:
            query = query.filter(MaterialDebt.balance_qty >= min_balance)

        return query.order_by(MaterialDebt.created_at.desc()).all()

    def get_debt_summary(self) -> dict:
        """Get debt summary statistics

        Returns:
            Dictionary with:
            - total_debts: Count of active debts
            - total_value: Sum of estimated costs
            - by_risk: Breakdown by risk level
            - top_materials: Top 10 materials with debt
        """
        active_debts = self.get_active_debts()

        total_value = sum(
            (d.total_cost_impact or Decimal(0)) for d in active_debts
        )

        # Group by risk level
        by_risk = {}
        for debt in active_debts:
            risk = debt.risk_level
            if risk not in by_risk:
                by_risk[risk] = {"count": 0, "value": Decimal(0)}
            by_risk[risk]["count"] += 1
            by_risk[risk]["value"] += debt.total_cost_impact or Decimal(0)

        # Top materials
        material_debts = {}
        for debt in active_debts:
            pid = debt.product_id
            if pid not in material_debts:
                material_debts[pid] = {
                    "product_id": pid,
                    "total_balance": Decimal(0),
                    "total_value": Decimal(0),
                    "debt_count": 0,
                }
            material_debts[pid]["total_balance"] += debt.balance_qty
            material_debts[pid]["total_value"] += (
                debt.total_cost_impact or Decimal(0)
            )
            material_debts[pid]["debt_count"] += 1

        top_materials = sorted(
            material_debts.values(),
            key=lambda x: x["total_value"],
            reverse=True,
        )[:10]

        return {
            "total_debts": len(active_debts),
            "total_value": float(total_value),
            "by_risk": by_risk,
            "top_materials": top_materials,
        }

    def auto_settle_from_grn(
        self,
        product_id: int,
        received_qty: Decimal,
        po_id: int,
        po_line_id: Optional[int] = None,
        grn_number: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> List[MaterialDebtSettlement]:
        """Automatically settle debts when GRN received

        Args:
            product_id: Material received
            received_qty: Quantity from GRN
            po_id: PO reference
            po_line_id: PO line reference
            grn_number: GRN number
            user_id: User processing GRN

        Returns:
            List of settlements created (FIFO order)

        Business Logic:
            1. Find active debts for material (FIFO - oldest first)
            2. Apply received qty to oldest debts first
            3. If qty exceeds debt, move to next debt
            4. Stop when received_qty fully allocated or no more debts
        """
        settlements = []
        remaining_qty = received_qty

        # Get active debts for this material (FIFO)
        active_debts = (
            self.db.query(MaterialDebt)
            .filter(
                and_(
                    MaterialDebt.product_id == product_id,
                    or_(
                        MaterialDebt.status == MaterialDebtStatus.ACTIVE,
                        MaterialDebt.status == MaterialDebtStatus.PARTIAL_PAID,
                    ),
                )
            )
            .order_by(MaterialDebt.created_at.asc())  # FIFO
            .all()
        )

        for debt in active_debts:
            if remaining_qty <= 0:
                break

            # Settle as much as possible
            settle_qty = min(remaining_qty, debt.balance_qty)

            settlement = self.settle_debt(
                debt_id=debt.id,
                settlement_qty=settle_qty,
                po_id=po_id,
                po_line_id=po_line_id,
                grn_number=grn_number,
                user_id=user_id,
                auto_settled=True,
                notes=f"Auto-settled from GRN {grn_number or 'N/A'}",
            )

            settlements.append(settlement)
            remaining_qty -= settle_qty

        return settlements

    def update_risk_level(
        self,
        debt_id: int,
        new_risk_level: str,
        notes: Optional[str] = None,
    ) -> MaterialDebt:
        """Update risk level of debt

        Args:
            debt_id: Debt to update
            new_risk_level: New risk (LOW/MEDIUM/HIGH/CRITICAL)
            notes: Reason for update

        Returns:
            Updated MaterialDebt
        """
        debt = self.db.query(MaterialDebt).get(debt_id)
        if not debt:
            raise ValueError(f"MaterialDebt {debt_id} not found")

        debt.risk_level = new_risk_level  # type: ignore

        if notes:
            existing = debt.impact_notes or ""
            timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
            debt.impact_notes = (  # type: ignore
                f"{existing}\n[{timestamp}] Risk updated to "
                f"{new_risk_level}: {notes}"
            )

        self.db.commit()
        self.db.refresh(debt)

        return debt

    def write_off_debt(
        self,
        debt_id: int,
        reason: str,
        user_id: Optional[int] = None,
    ) -> MaterialDebt:
        """Write off debt (cancel/void)

        Args:
            debt_id: Debt to write off
            reason: Reason for write-off
            user_id: User authorizing write-off

        Returns:
            Updated MaterialDebt with WRITTEN_OFF status
        """
        debt = self.db.query(MaterialDebt).get(debt_id)
        if not debt:
            raise ValueError(f"MaterialDebt {debt_id} not found")

        if debt.status == MaterialDebtStatus.FULLY_PAID:
            raise ValueError("Cannot write off fully paid debt")

        debt.status = MaterialDebtStatus.WRITTEN_OFF  # type: ignore
        debt.resolved_by_id = user_id  # type: ignore
        debt.resolved_at = datetime.utcnow()  # type: ignore

        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
        debt.impact_notes = (  # type: ignore
            f"{debt.impact_notes or ''}\n[{timestamp}] "
            f"WRITTEN OFF: {reason}"
        )

        self.db.commit()
        self.db.refresh(debt)

        return debt
