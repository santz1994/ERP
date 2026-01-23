"""Copyright (c) 2026 PT Quty Karunia / Daniel Rizaldy - All Rights Reserved

Embroidery Service - Business Logic
Handles embroidery operations, WIP EMBO transfers, quality checks
"""

from datetime import datetime

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.core.models.exceptions import AlertLog
from app.core.models.manufacturing import WorkOrder
from app.core.models.transfer import LineOccupancy, TransferLog
from app.shared.audit import log_audit


class EmbroideryService:
    """Business logic for Embroidery operations"""

    def __init__(self, db: Session):
        self.db = db

    def _get_work_order(self, work_order_id: int) -> WorkOrder:
        """Helper method - Get work order by ID with error handling"""
        work_order = self.db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not work_order:
            raise ValueError(f"Work order {work_order_id} not found")
        return work_order

    def get_work_orders(self, status: str | None = None) -> list[WorkOrder]:
        """Get work orders for Embroidery department"""
        query = self.db.query(WorkOrder).filter(WorkOrder.department == "Embroidery")

        if status:
            query = query.filter(WorkOrder.status == status)

        return query.order_by(WorkOrder.created_at.desc()).all()

    def start_work_order(self, work_order_id: int, user_id: int) -> WorkOrder:
        """Start embroidery work order"""
        work_order = self._get_work_order(work_order_id)

        if work_order.status != "Pending":
            raise ValueError(f"Cannot start work order with status {work_order.status}")

        # Check line clearance
        line_status = self.db.query(LineOccupancy).filter(
            and_(
                LineOccupancy.line_id == f"EMBO-LINE-{work_order.id % 5 + 1}",
                LineOccupancy.is_occupied == True
            )
        ).first()

        if line_status and line_status.current_article != work_order.mo.product_code:
            raise ValueError(
                f"Line clearance required. Line occupied by {line_status.current_article}"
            )

        # Update work order
        work_order.status = "Running"
        work_order.start_time = datetime.utcnow()

        # Create line occupancy
        line_occupancy = LineOccupancy(
            line_id=f"EMBO-LINE-{work_order.id % 5 + 1}",
            current_article=work_order.mo.product_code,
            is_occupied=True,
            department="Embroidery",
            destination="Sewing"
        )
        self.db.add(line_occupancy)

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="START_EMBROIDERY",
            entity_type="WorkOrder",
            entity_id=work_order.id,
            changes={"status": "Running", "start_time": work_order.start_time.isoformat()}
        )

        self.db.commit()
        self.db.refresh(work_order)

        return work_order

    def record_embroidery_output(
        self,
        work_order_id: int,
        embroidered_qty: int,
        reject_qty: int,
        user_id: int,
        design_type: str | None = None,
        thread_colors: list[str] | None = None
    ) -> WorkOrder:
        """Record embroidery output with design details"""
        work_order = self._get_work_order(work_order_id)

        if work_order.status != "Running":
            raise ValueError(f"Cannot record output for work order with status {work_order.status}")

        # Validate quantities
        total_qty = embroidered_qty + reject_qty
        if total_qty > work_order.input_qty:
            raise ValueError(
                f"Total quantity ({total_qty}) exceeds input quantity ({work_order.input_qty})"
            )

        # Update work order
        work_order.output_qty = embroidered_qty
        work_order.reject_qty = reject_qty

        # Store embroidery details in metadata
        if not work_order.metadata:
            work_order.metadata = {}

        work_order.metadata.update({
            "design_type": design_type,
            "thread_colors": thread_colors or [],
            "embroidery_completion": datetime.utcnow().isoformat()
        })

        # Check for shortages
        shortage = work_order.input_qty - total_qty
        if shortage > 0:
            self._create_shortage_alert(work_order, shortage, user_id)

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="RECORD_EMBROIDERY_OUTPUT",
            entity_type="WorkOrder",
            entity_id=work_order.id,
            changes={
                "embroidered_qty": embroidered_qty,
                "reject_qty": reject_qty,
                "design_type": design_type
            }
        )

        self.db.commit()
        self.db.refresh(work_order)

        return work_order

    def complete_embroidery(self, work_order_id: int, user_id: int) -> WorkOrder:
        """Complete embroidery work order"""
        work_order = self._get_work_order(work_order_id)

        if work_order.status != "Running":
            raise ValueError(f"Cannot complete work order with status {work_order.status}")

        if work_order.output_qty == 0:
            raise ValueError("Cannot complete work order with zero output")

        # Update work order
        work_order.status = "Finished"
        work_order.end_time = datetime.utcnow()

        # Release line
        line_occupancy = self.db.query(LineOccupancy).filter(
            and_(
                LineOccupancy.line_id == f"EMBO-LINE-{work_order.id % 5 + 1}",
                LineOccupancy.is_occupied == True
            )
        ).first()

        if line_occupancy:
            line_occupancy.is_occupied = False
            line_occupancy.current_article = None

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="COMPLETE_EMBROIDERY",
            entity_type="WorkOrder",
            entity_id=work_order.id,
            changes={"status": "Finished", "end_time": work_order.end_time.isoformat()}
        )

        self.db.commit()
        self.db.refresh(work_order)

        return work_order

    def transfer_to_sewing(self, work_order_id: int, user_id: int) -> TransferLog:
        """Transfer embroidered items to Sewing (QT-09 Protocol)"""
        work_order = self._get_work_order(work_order_id)

        if work_order.status != "Finished":
            raise ValueError("Work order must be finished before transfer")

        # Check line clearance at Sewing
        sewing_line = self.db.query(LineOccupancy).filter(
            and_(
                LineOccupancy.department == "Sewing",
                LineOccupancy.is_occupied == True,
                LineOccupancy.current_article != work_order.mo.product_code
            )
        ).first()

        if sewing_line:
            raise ValueError(
                f"Sewing line blocked. Current article: {sewing_line.current_article}"
            )

        # Create transfer log (QT-09)
        transfer = TransferLog(
            mo_id=work_order.mo_id,
            from_department="Embroidery",
            to_department="Sewing",
            product_code=work_order.mo.product_code,
            transfer_qty=work_order.output_qty,
            transfer_type="WIP_EMBO_to_WIP_SEW",
            status="Completed",
            acknowledged_by=user_id,
            acknowledged_at=datetime.utcnow()
        )

        self.db.add(transfer)

        # Create new work order for Sewing
        sewing_wo = WorkOrder(
            mo_id=work_order.mo_id,
            department="Sewing",
            status="Pending",
            input_qty=work_order.output_qty,
            output_qty=0,
            reject_qty=0
        )
        self.db.add(sewing_wo)

        # Audit log
        log_audit(
            self.db,
            user_id=user_id,
            action="TRANSFER_TO_SEWING",
            entity_type="TransferLog",
            entity_id=transfer.id,
            changes={
                "from": "Embroidery",
                "to": "Sewing",
                "qty": work_order.output_qty
            }
        )

        self.db.commit()
        self.db.refresh(transfer)

        return transfer

    def get_line_status(self) -> list[LineOccupancy]:
        """Get all embroidery line statuses"""
        return self.db.query(LineOccupancy).filter(
            LineOccupancy.department == "Embroidery"
        ).all()

    def _create_shortage_alert(self, work_order: WorkOrder, shortage_qty: int, user_id: int):
        """Create alert for embroidery shortage"""
        alert = AlertLog(
            alert_type="EMBROIDERY_SHORTAGE",
            severity="HIGH",
            message=f"Embroidery shortage detected: {shortage_qty} units missing for WO #{work_order.id}",
            department="Embroidery",
            mo_id=work_order.mo_id,
            work_order_id=work_order.id,
            acknowledged=False
        )

        self.db.add(alert)
        self.db.commit()
