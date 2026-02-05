"""Warehouse Finishing Service - Phase 2A

Service layer for warehouse finishing operations (2-stage process)
Handles SPK creation and daily input/output recording

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.core.models.manufacturing import SPK, Department
from app.core.models.finishing import (
    WarehouseFinishingStock,
    FinishingMaterialConsumption,
    FinishingInputOutput,
    FinishingStage,
)
from app.shared.audit import log_audit


class FinishingService:
    """Business logic for warehouse finishing operations"""

    def __init__(self, db: Session):
        self.db = db

    def create_stage1_spk(
        self,
        mo_id: int,
        target_qty: Decimal,
        buffer_pct: Decimal = Decimal("0"),
        user_id: int = None,
    ) -> SPK:
        """Create Stage 1 (Stuffing) SPK for Warehouse Finishing

        Args:
            mo_id: Manufacturing Order ID
            target_qty: Base target quantity from Packing demand
            buffer_pct: Buffer percentage (default 0%)
            user_id: User creating SPK

        Returns:
            Created SPK for Stuffing stage
        """
        from app.core.models.manufacturing import ManufacturingOrder

        mo = self.db.query(ManufacturingOrder).filter_by(id=mo_id).first()
        if not mo:
            raise ValueError(f"MO {mo_id} not found")

        # Create SPK for Stuffing
        spk = SPK(
            mo_id=mo_id,
            department=Department.FINISHING,
            original_qty=int(target_qty),
            buffer_percentage=buffer_pct,
            target_qty=int(target_qty * (1 + buffer_pct / 100)),
            production_status="NOT_STARTED",
            created_by_id=user_id,
            extra_metadata=f'{{"finishing_stage": 1, "stage_name": "Stuffing"}}',
        )

        self.db.add(spk)
        self.db.commit()

        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="CREATE_STAGE1_SPK",
                entity_type="SPK",
                entity_id=spk.id,
                changes={"stage": "Stuffing", "target_qty": int(target_qty)},
            )

        return spk

    def create_stage2_spk(
        self,
        stage1_spk_id: int,
        target_qty: Decimal,
        user_id: int = None,
    ) -> SPK:
        """Create Stage 2 (Closing) SPK based on Stage 1 output

        Args:
            stage1_spk_id: Stage 1 SPK ID (for linking)
            target_qty: Target for closing stage
            user_id: User creating SPK

        Returns:
            Created SPK for Closing stage
        """
        stage1_spk = self.db.query(SPK).filter_by(id=stage1_spk_id).first()
        if not stage1_spk:
            raise ValueError(f"Stage 1 SPK {stage1_spk_id} not found")

        # Create SPK for Closing
        spk = SPK(
            mo_id=stage1_spk.mo_id,
            department=Department.FINISHING,
            original_qty=int(target_qty),
            buffer_percentage=Decimal("0"),
            target_qty=int(target_qty),
            production_status="NOT_STARTED",
            created_by_id=user_id,
            extra_metadata=f'{{"finishing_stage": 2, "stage_name": "Closing", "prev_spk_id": {stage1_spk_id}}}',
        )

        self.db.add(spk)
        self.db.commit()

        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="CREATE_STAGE2_SPK",
                entity_type="SPK",
                entity_id=spk.id,
                changes={
                    "stage": "Closing",
                    "target_qty": int(target_qty),
                    "linked_to_stage1": stage1_spk_id,
                },
            )

        return spk

    def input_stage1_result(
        self,
        spk_id: int,
        input_qty: Decimal,
        good_qty: Decimal,
        defect_qty: Decimal,
        rework_qty: Decimal,
        filling_consumed: Decimal,
        operator_id: int,
        production_date: date = None,
        notes: str = None,
        user_id: int = None,
    ) -> FinishingInputOutput:
        """Record Stage 1 (Stuffing) completion

        Args:
            spk_id: Stage 1 SPK ID
            input_qty: Pieces received for stuffing
            good_qty: Good stuffed bodies produced
            defect_qty: Defective output
            rework_qty: Units sent to rework
            filling_consumed: Filling (kapas) consumed in KG
            operator_id: Operator who did the work
            production_date: Date of production
            notes: Additional notes
            user_id: User recording the result

        Returns:
            Created FinishingInputOutput record
        """
        spk = self.db.query(SPK).filter_by(id=spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")

        if production_date is None:
            production_date = date.today()

        # Create input/output record
        io_record = FinishingInputOutput(
            spk_id=spk_id,
            stage=FinishingStage.STAGE_1_STUFFING,
            production_date=production_date,
            input_qty=input_qty,
            good_qty=good_qty,
            defect_qty=defect_qty,
            rework_qty=rework_qty,
            yield_rate=(good_qty / input_qty * 100) if input_qty > 0 else 0,
            operator_id=operator_id,
            notes=notes,
        )

        self.db.add(io_record)

        # Update SPK status
        spk.produced_qty = good_qty + defect_qty
        spk.good_qty = good_qty
        spk.defect_qty = defect_qty
        spk.production_status = "COMPLETED"

        self.db.commit()

        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="INPUT_STAGE1_RESULT",
                entity_type="SPK",
                entity_id=spk_id,
                changes={
                    "good_qty": int(good_qty),
                    "defect_qty": int(defect_qty),
                    "yield": float(io_record.yield_rate),
                    "filling_kg": float(filling_consumed),
                },
            )

        return io_record

    def input_stage2_result(
        self,
        spk_id: int,
        input_qty: Decimal,
        good_qty: Decimal,
        defect_qty: Decimal,
        rework_qty: Decimal,
        thread_consumed: Decimal,
        operator_id: int,
        production_date: date = None,
        notes: str = None,
        user_id: int = None,
    ) -> FinishingInputOutput:
        """Record Stage 2 (Closing) completion

        Args:
            spk_id: Stage 2 SPK ID
            input_qty: Stuffed bodies received for closing
            good_qty: Finished dolls produced
            defect_qty: Defective output
            rework_qty: Units sent to rework
            thread_consumed: Thread consumed in meters
            operator_id: Operator who did the work
            production_date: Date of production
            notes: Additional notes
            user_id: User recording the result

        Returns:
            Created FinishingInputOutput record
        """
        spk = self.db.query(SPK).filter_by(id=spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")

        if production_date is None:
            production_date = date.today()

        io_record = FinishingInputOutput(
            spk_id=spk_id,
            stage=FinishingStage.STAGE_2_CLOSING,
            production_date=production_date,
            input_qty=input_qty,
            good_qty=good_qty,
            defect_qty=defect_qty,
            rework_qty=rework_qty,
            yield_rate=(good_qty / input_qty * 100) if input_qty > 0 else 0,
            operator_id=operator_id,
            notes=notes,
        )

        self.db.add(io_record)

        # Update SPK status
        spk.produced_qty = good_qty + defect_qty
        spk.good_qty = good_qty
        spk.defect_qty = defect_qty
        spk.production_status = "COMPLETED"

        self.db.commit()

        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="INPUT_STAGE2_RESULT",
                entity_type="SPK",
                entity_id=spk_id,
                changes={
                    "good_qty": int(good_qty),
                    "defect_qty": int(defect_qty),
                    "yield": float(io_record.yield_rate),
                    "thread_m": float(thread_consumed),
                },
            )

        return io_record
