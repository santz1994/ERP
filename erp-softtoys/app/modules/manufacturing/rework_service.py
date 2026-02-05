"""Rework & QC Service - Phase 2B

Service layer for rework and quality control operations
Handles defect tracking, rework requests, and QC approval workflow

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.core.models.manufacturing import (
    ReworkRequest,
    ReworkStatus,
    ReworkMaterial,
    DefectCategory,
    SPK,
)


class ReworkService:
    """Business logic for rework & QC operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_rework_request(
        self,
        spk_id: int,
        defect_qty: Decimal,
        defect_category_id: int,
        defect_notes: Optional[str] = None,
        requested_by_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> ReworkRequest:
        """Create rework request from defective units

        Args:
            spk_id: SPK with defects
            defect_qty: Number of defective units
            defect_category_id: Type of defect (from DefectCategory)
            defect_notes: Details about defects
            requested_by_id: User requesting rework (usually QC inspector)
            user_id: User creating record (for audit)

        Returns:
            Created ReworkRequest (status: PENDING)

        Raises:
            ValueError: If SPK or DefectCategory not found
        """
        spk = self.db.query(SPK).filter_by(id=spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")

        category = (
            self.db.query(DefectCategory)
            .filter_by(id=defect_category_id)
            .first()
        )
        if not category:
            raise ValueError(
                f"DefectCategory {defect_category_id} not found"
            )

        rework = ReworkRequest(
            spk_id=spk_id,
            defect_qty=defect_qty,
            defect_category_id=defect_category_id,
            defect_notes=defect_notes,
            requested_by_id=requested_by_id,
            status=ReworkStatus.PENDING,
        )

        self.db.add(rework)
        self.db.commit()
        self.db.refresh(rework)

        return rework

    def approve_rework(
        self,
        rework_id: int,
        qc_approval_notes: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> ReworkRequest:
        """Approve rework request (QC manager action)

        Args:
            rework_id: Rework request to approve
            qc_approval_notes: QC approval comments
            user_id: QC manager ID

        Returns:
            Updated ReworkRequest (status: APPROVED)

        Raises:
            ValueError: If rework not found or not in PENDING status
        """
        rework = (
            self.db.query(ReworkRequest)
            .filter_by(id=rework_id)
            .first()
        )
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")

        if rework.status != ReworkStatus.PENDING:
            raise ValueError(
                f"Cannot approve rework in {rework.status} status"
            )

        rework.status = ReworkStatus.APPROVED  # type: ignore
        rework.qc_reviewed_by_id = user_id  # type: ignore
        rework.qc_reviewed_at = datetime.utcnow()  # type: ignore
        rework.qc_approval_notes = qc_approval_notes  # type: ignore

        self.db.commit()
        self.db.refresh(rework)

        return rework

    def reject_rework(
        self,
        rework_id: int,
        rejection_reason: str,
        user_id: Optional[int] = None,
    ) -> ReworkRequest:
        """Reject rework request (discard instead of rework)

        Args:
            rework_id: Rework to reject
            rejection_reason: Why reject (discard reason)
            user_id: QC manager ID

        Returns:
            Updated ReworkRequest (status: REJECTED)

        Raises:
            ValueError: If rework not found or not in PENDING status
        """
        rework = (
            self.db.query(ReworkRequest)
            .filter_by(id=rework_id)
            .first()
        )
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")

        if rework.status != ReworkStatus.PENDING:
            raise ValueError(
                f"Cannot reject rework in {rework.status} status"
            )

        rework.status = ReworkStatus.REJECTED  # type: ignore
        rework.qc_reviewed_by_id = user_id  # type: ignore
        rework.qc_reviewed_at = datetime.utcnow()  # type: ignore
        rework.qc_approval_notes = rejection_reason  # type: ignore

        self.db.commit()
        self.db.refresh(rework)

        return rework

    def start_rework(
        self,
        rework_id: int,
        operator_id: int,
        user_id: Optional[int] = None,
    ) -> ReworkRequest:
        """Start rework process (operator action)

        Args:
            rework_id: Rework to start
            operator_id: Operator doing the rework
            user_id: User starting rework

        Returns:
            Updated ReworkRequest (status: IN_PROGRESS)

        Raises:
            ValueError: If rework not found or not APPROVED
        """
        rework = (
            self.db.query(ReworkRequest)
            .filter_by(id=rework_id)
            .first()
        )
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")

        if rework.status != ReworkStatus.APPROVED:
            raise ValueError(
                f"Cannot start rework in {rework.status} status"
            )

        rework.status = ReworkStatus.IN_PROGRESS  # type: ignore
        rework.rework_started_at = datetime.utcnow()  # type: ignore
        rework.rework_operator_id = operator_id  # type: ignore

        self.db.commit()
        self.db.refresh(rework)

        return rework

    def complete_rework(
        self,
        rework_id: int,
        rework_notes: Optional[str] = None,
        material_cost: Decimal = Decimal("0"),
        labor_cost: Decimal = Decimal("0"),
        user_id: Optional[int] = None,
    ) -> ReworkRequest:
        """Complete rework process (operator action)

        Args:
            rework_id: Completed rework
            rework_notes: What was done
            material_cost: Cost of materials used
            labor_cost: Cost of labor
            user_id: User completing

        Returns:
            Updated ReworkRequest (status: COMPLETED)

        Raises:
            ValueError: If rework not found or not IN_PROGRESS
        """
        rework = (
            self.db.query(ReworkRequest)
            .filter_by(id=rework_id)
            .first()
        )
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")

        if rework.status != ReworkStatus.IN_PROGRESS:
            raise ValueError(
                f"Cannot complete rework in {rework.status} status"
            )

        rework.status = ReworkStatus.COMPLETED  # type: ignore
        rework.rework_completed_at = datetime.utcnow()  # type: ignore
        rework.rework_notes = rework_notes  # type: ignore
        rework.material_cost = material_cost  # type: ignore
        rework.labor_cost = labor_cost  # type: ignore
        rework.total_cost = material_cost + labor_cost  # type: ignore

        self.db.commit()
        self.db.refresh(rework)

        return rework

    def verify_rework(
        self,
        rework_id: int,
        verified_good_qty: Decimal,
        verified_failed_qty: Decimal,
        user_id: Optional[int] = None,
    ) -> ReworkRequest:
        """Final QC verification of reworked units

        Args:
            rework_id: Rework to verify
            verified_good_qty: Units that passed verification
            verified_failed_qty: Units that still failed (discard)
            user_id: QC verifier ID

        Returns:
            Updated ReworkRequest (status: VERIFIED)

        Raises:
            ValueError: If quantities don't match or rework not COMPLETED
        """
        rework = (
            self.db.query(ReworkRequest)
            .filter_by(id=rework_id)
            .first()
        )
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")

        if rework.status != ReworkStatus.COMPLETED:
            raise ValueError(
                f"Cannot verify rework in {rework.status} status"
            )

        # Validation: good + failed should equal defect qty
        total_verified = verified_good_qty + verified_failed_qty
        if total_verified != rework.defect_qty:
            raise ValueError(
                f"Verification quantities ({total_verified}) "
                f"must equal defect quantity ({rework.defect_qty})"
            )

        rework.status = ReworkStatus.VERIFIED  # type: ignore
        rework.verified_by_id = user_id  # type: ignore
        rework.verified_at = datetime.utcnow()  # type: ignore
        rework.verified_good_qty = verified_good_qty  # type: ignore
        rework.verified_failed_qty = verified_failed_qty  # type: ignore

        self.db.commit()
        self.db.refresh(rework)

        return rework

    def add_rework_material(
        self,
        rework_id: int,
        product_id: int,
        qty_used: Decimal,
        uom: str,
        unit_cost: Decimal,
        user_id: Optional[int] = None,
    ) -> ReworkMaterial:
        """Add material consumed during rework

        Args:
            rework_id: Which rework request
            product_id: Material/product used
            qty_used: Quantity used
            uom: Unit of measure (KG, PIECES, METERS, etc.)
            unit_cost: Cost per unit
            user_id: User recording

        Returns:
            Created ReworkMaterial

        Raises:
            ValueError: If rework not found
        """
        rework = (
            self.db.query(ReworkRequest)
            .filter_by(id=rework_id)
            .first()
        )
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")

        material = ReworkMaterial(
            rework_request_id=rework_id,
            product_id=product_id,
            qty_used=qty_used,
            uom=uom,
            unit_cost=unit_cost,
            total_cost=qty_used * unit_cost,
        )

        self.db.add(material)
        self.db.commit()
        self.db.refresh(material)

        return material
