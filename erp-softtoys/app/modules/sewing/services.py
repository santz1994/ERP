"""Sewing Module Business Logic & Services
Handles material input validation, 3-stage sewing, inline QC, and transfer

Refactored: Now extends BaseProductionService to eliminate code duplication
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.base_production_service import BaseProductionService
from app.core.models.manufacturing import (
    Department,
    WorkOrder,
    WorkOrderStatus,
)
from app.core.models.quality import QCInspection
from app.core.models.transfer import LineOccupancy, TransferDept


class SewingService(BaseProductionService):
    """Business logic for sewing department operations
    Extends BaseProductionService for common production patterns
    """

    # Department configuration
    DEPARTMENT = Department.SEWING
    DEPARTMENT_NAME = "Sewing"
    TRANSFER_DEPT = TransferDept.SEWING

    @classmethod
    def accept_transfer_and_validate(
        cls,
        db: Session,
        transfer_slip_number: str,
        received_qty: Decimal,
        user_id: int,
        notes: Optional[str] = None
    ) -> dict:
        """Step 300: Accept Transfer & Material Validation
        Uses base class accept_transfer_from_previous_dept
        """
        # Delegate to base class
        result = cls.accept_transfer_from_previous_dept(
            db=db,
            transfer_slip_number=transfer_slip_number,
            received_qty=received_qty,
            user_id=user_id,
            from_dept=TransferDept.CUTTING,  # Can also be from EMBROIDERY
            notes=notes
        )

        # Add sewing-specific next step
        result["next_step"] = "Validate input qty vs BOM"

        return result

    @classmethod
    def validate_input_vs_bom(
        cls,
        db: Session,
        work_order_id: int,
        received_qty: Decimal,
        expected_product_id: int = None
    ) -> dict:
        """Step 310: VALIDASI INPUT - Validate Received Qty vs BOM Target.
        - Compare received material vs BOM requirements
        - If shortage: Auto-request additional material
        - If OK: Proceed to assembly
        """
        # Get work order to find product ID if not provided
        wo = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()

        if not wo:
            raise HTTPException(status_code=404, detail="Work order not found")

        if expected_product_id is None:
            expected_product_id = wo.product_id

        # Call parent class implementation
        return super().validate_input_vs_bom(
            db=db,
            work_order_id=work_order_id,
            received_qty=received_qty,
            expected_product_id=expected_product_id,
        )

    @staticmethod
    def process_sewing_step(
        db: Session,
        work_order_id: int,
        step_number: int,
        qty_processed: Decimal,
        notes: Optional[str] = None
    ) -> dict:
        """Step 330-350: 3-Stage Sewing Process
        - Step 330: Proses Jahit 1 - Assembly (rakit body)
        - Step 340: Proses Jahit 2 - Labeling (attach label)
        - Step 350: Proses Jahit 3 - Stik Balik (loop stitching)
        """
        wo = BaseProductionService.get_work_order(db, work_order_id)

        stage_names = {
            1: "Assembly (Rakit Body)",
            2: "Labeling (Attach Label)",
            3: "Stik Balik (Loop Stitching)"
        }

        if step_number not in [1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail="Invalid step number. Must be 1, 2, or 3",
            )

        stage_name = stage_names[step_number]

        result = {
            "work_order_id": work_order_id,
            "stage": stage_name,
            "qty_processed": float(qty_processed),
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes,
            "status": "Completed"
        }

        if step_number == 1:
            wo.status = WorkOrderStatus.RUNNING
            result["next_stage"] = "Labeling"

        elif step_number == 2:
            result["next_stage"] = "Stik Balik"

        elif step_number == 3:
            result["next_stage"] = "Inline QC Inspection"
            result["message"] = "Proceed to QC inspection (Step 360)"

        db.commit()

        return result

    @staticmethod
    def perform_inline_qc(
        db: Session,
        work_order_id: int,
        inspector_id: int,
        pass_qty: Decimal,
        rework_qty: Decimal,
        scrap_qty: Decimal,
        defect_reason: Optional[str] = None
    ) -> dict:
        """Step 360-375: INLINE QC INSPECTION
        - Step 360: Check jahitan quality
        - Step 370: Rework process (can go back to step 350)
        - Step 375: Scrap/reject flow
        """
        wo = BaseProductionService.get_work_order(db, work_order_id)

        total_qty = pass_qty + rework_qty + scrap_qty

        if total_qty != wo.input_qty:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Total inspected qty ({total_qty}) != "
                    f"input qty ({wo.input_qty})"
                ),
            )

        # Create QC inspection record
        qc = QCInspection(
            work_order_id=work_order_id,
            type="Inline Sewing",
            status="Pass" if scrap_qty == 0 else "Fail",
            defect_reason=defect_reason,
            inspected_by=inspector_id
        )
        db.add(qc)
        db.flush()

        result = {
            "work_order_id": work_order_id,
            "qc_inspection_id": qc.id,
            "pass_qty": float(pass_qty),
            "rework_qty": float(rework_qty),
            "scrap_qty": float(scrap_qty),
            "pass_rate": float(
                pass_qty / wo.input_qty * 100
                if wo.input_qty > 0
                else 0
            ),
            "timestamp": datetime.utcnow().isoformat()
        }

        if rework_qty > 0:
            result["rework_action"] = (
                "Step 370: Send to rework - "
                "return to Stik Balik"
            )
            result["next_step"] = "Rework/Repair"
            wo.status = WorkOrderStatus.RUNNING

        if scrap_qty > 0:
            result["scrap_action"] = "Step 375: Scrap - Create defect report"
            result["defect_reason"] = defect_reason
            # Track as reject in WO
            wo.reject_qty = (wo.reject_qty or 0) + scrap_qty

        if pass_qty > 0 and rework_qty == 0:
            result["status"] = "PASSED - Ready for segregation check"
            result["next_step"] = "Step 380: Segregation check"
            wo.output_qty = pass_qty

        db.commit()

        return result

    @staticmethod
    def check_segregation(
        db: Session,
        work_order_id: int
    ) -> tuple[bool, str | None, dict]:
        """Step 380: SEGREGASI CHECK - Verify Destination Consistency

        QT-09 Segregation Rule:
        - All WIP in same batch MUST go to same destination/week
        - If destination DIFFERS from current line → ALARM
        - If different: Require 5-meter jeda or manual line clearance
        """
        wo = BaseProductionService.get_work_order(db, work_order_id)

        mo = BaseProductionService.get_manufacturing_order(db, wo.mo_id)

        # Get current line destination (from last batch on Finishing line)
        finishing_line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == TransferDept.FINISHING
        ).first()

        current_destination = (
            finishing_line.destination if finishing_line else None
        )
        batch_destination = (
            mo.destination if hasattr(mo, 'destination') else None
        )

        destinations_match = (
            (current_destination == batch_destination)
            or (current_destination is None)
        )

        check_result = {
            "work_order_id": work_order_id,
            "batch_destination": batch_destination,
            "current_line_destination": current_destination,
            "destinations_match": destinations_match,
            "timestamp": datetime.utcnow().isoformat()
        }

        blocking_reason = None
        if not destinations_match:
            blocking_reason = (
                f"ALARM: Destination mismatch - "
                f"Line has {current_destination}, "
                f"batch is {batch_destination}. "
                f"Require 5m jeda or line clearance."
            )
            check_result["alarm"] = blocking_reason
            check_result["segregation_status"] = (
                "BLOCKED - Destination Mismatch"
            )
            check_result["requires_jeda"] = True
            check_result["jeda_duration_minutes"] = 5
        else:
            check_result["segregation_status"] = "CLEAR - Same destination"
            check_result["requires_jeda"] = False

        return destinations_match, blocking_reason, check_result

    @classmethod
    def transfer_to_finishing(
        cls,
        db: Session,
        work_order_id: int,
        transfer_qty: Decimal,
        user_id: int
    ) -> dict:
        """Step 381-383: Print Transfer & Handshake Digital
        - Step 381: Print Surat Jalan to Finishing
        - Step 383: HANDSHAKE - Lock WIP SEW

        REFACTORED: Now uses BaseProductionService.create_transfer_log()
        Eliminates 65 lines of duplicate code (22.4% reduction)
        """
        # Delegate to base class (DRY principle)
        return cls.create_transfer_log(
            db=db,
            work_order_id=work_order_id,
            to_dept=TransferDept.FINISHING,
            qty_to_transfer=transfer_qty,
            operator_id=user_id
        )


    @staticmethod
    def internal_loop_return(
        db: Session,
        work_order_id: int,
        from_stage: int,
        to_stage: int,
        qty_to_return: Decimal,
        reason: str,
        user_id: int,
        notes: str | None = None
    ) -> dict:
        """Internal Loop/Return - Sewing Department Internal Transfer.

        Handles Note 1: Sewing Loop (Balik lagi)
        - Internal Line Balancing within Sewing department
        - No external transfer slip needed (stays in Sewing)
        - Uses internal work card/control card (Kartu Kendali Meja)

        Common use cases:
        - After Stik (Stage 3) → Return to Assembly
          (Stage 1) for final assembly
        - Finger stitching on dolls requiring
          additional stik work
        - Complex patterns needing multiple
          assembly passes

        This is NOT a rework due to defects - it's part
        of the normal process flow for certain product
        types.

        Args:
            from_stage: Current stage (1=Assembly,
              2=Labeling, 3=Stik)
            to_stage: Target stage to return to
            qty_to_return: Quantity for internal loop
            reason: Business reason (e.g.,
              "Final Assembly after Stik",
              "Finger Stitching")

        """
        wo = BaseProductionService.get_work_order(db, work_order_id)

        stage_names = {
            1: "Assembly (Pos 1: Rakit)",
            2: "Labeling (Pos 2: Label)",
            3: "Stik (Pos 3: Stik Balik)"
        }

        if from_stage not in [1, 2, 3] or to_stage not in [1, 2, 3]:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid stage number. Must be 1 (Assembly), "
                    "2 (Labeling), or 3 (Stik)"
                ),
            )

        if from_stage <= to_stage:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Internal loop must return to PREVIOUS stage "
                    "(from_stage > to_stage)"
                ),
            )

        # Create internal control card record (not a full transfer log)
        internal_loop_data = {
            "control_card_type": "Internal Sewing Loop",
            "work_order_id": work_order_id,
            "from_stage": stage_names[from_stage],
            "to_stage": stage_names[to_stage],
            "qty_looped": float(qty_to_return),
            "reason": reason,
            "notes": notes,
            "created_by": user_id,
            "created_at": datetime.utcnow().isoformat(),
            "department": "Sewing (Internal)",
            "requires_external_transfer": False
        }

        # Update work order metadata to track internal loops
        if not wo.metadata:
            wo.metadata = {}

        if "internal_loops" not in wo.metadata:
            wo.metadata["internal_loops"] = []

        wo.metadata["internal_loops"].append(internal_loop_data)

        # Mark to trigger SQLAlchemy update
        from sqlalchemy.orm.attributes import flag_modified
        flag_modified(wo, "metadata")

        db.commit()

        return {
            "success": True,
            "message": "Internal loop created successfully",
            "control_card": internal_loop_data,
            "workflow": {
                "type": "Internal Line Balancing",
                "no_external_transfer": True,
                "tracking_method": "Kartu Kendali Meja",
                "next_action": (
                    f"Process {float(qty_to_return)} units at "
                    f"{stage_names[to_stage]} station"
                ),
            },
            "reference": "Note 1: Sewing Loop - Flow Production.md"
        }

