"""Cutting Module Business Logic & Services
Handles material allocation, output tracking, QT-09 protocol.

Refactored: Now extends BaseProductionService to eliminate code duplication
"""

from datetime import datetime
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.base_production_service import BaseProductionService
from app.core.models.manufacturing import (
    Department,
    MaterialConsumption,
    WorkOrderStatus,
)
from app.core.models.transfer import (  # noqa: E501
    TransferDept,
)
from app.core.models.warehouse import Location, StockMove, StockQuant


class CuttingService(BaseProductionService):
    """Business logic for cutting department operations
    Extends BaseProductionService for common production patterns.
    """

    # Department configuration
    DEPARTMENT = Department.CUTTING
    DEPARTMENT_NAME = "Cutting"
    TRANSFER_DEPT = TransferDept.CUTTING

    @classmethod
    def receive_spk_and_allocate_material(
        cls,
        db: Session,
        work_order_id: int,
        operator_id: int
    ) -> dict:
        """Step 200: Receive SPK & Allocate Material
        - Check material availability
        - Create stock move (warehouse → cutting line)
        - Return material issue slip info.
        """
        # Fetch work order using centralized helper
        wo = cls.get_work_order(db, work_order_id)

        if wo.status != WorkOrderStatus.PENDING:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot allocate material for WO in {wo.status} status"  # noqa: E501
            )

        # Fetch BOM to get material requirements
        from app.core.models.bom import BOMDetail, BOMHeader
        bom = db.query(BOMHeader).filter(
            BOMHeader.product_id == wo.product_id,
            BOMHeader.is_active == True  # noqa: E712
        ).first()

        if not bom:
            raise HTTPException(
                status_code=404,
                detail=f"No active BOM for product {wo.product_id}"
            )

        # Get BOM details
        bom_details = db.query(BOMDetail).filter(
            BOMDetail.bom_header_id == bom.id
        ).all()

        material_allocations = []
        total_value = Decimal(0)

        for detail in bom_details:
            # Calculate needed quantity (with wastage)
            base_qty = detail.qty_needed * wo.input_qty
            wastage = base_qty * (detail.wastage_percent / 100)
            total_needed = base_qty + wastage

            # Check stock availability (FIFO - on_hand - reserved)
            stock = db.query(StockQuant).filter(
                StockQuant.product_id == detail.component_id,
                StockQuant.qty_on_hand > 0
            ).order_by(StockQuant.lot_id).first()  # FIFO by lot

            if not stock or (stock.qty_on_hand - stock.qty_reserved) < total_needed:
                total_needed - (stock.qty_on_hand - stock.qty_reserved if stock else 0)
                raise HTTPException(
                    status_code=400,
                    detail=f"Material shortage for product {detail.component_id}: need {total_needed}, available {stock.qty_on_hand - stock.qty_reserved if stock else 0}"
                )

            # Create stock move (warehouse → cutting line)
            cutting_line = db.query(Location).filter(Location.name == "Line Cutting").first()
            if not cutting_line:
                cutting_line = Location(name="Line Cutting", type="Production")
                db.add(cutting_line)
                db.flush()

            stock_move = StockMove(
                product_id=detail.component_id,
                qty=total_needed,
                uom=detail.component.uom,
                location_id_from=stock.location_id,  # Warehouse location
                location_id_to=cutting_line.id,
                reference_doc=f"SPK-CUT-{wo.mo_id}",
                lot_id=stock.lot_id,
                state="Draft"
            )
            db.add(stock_move)
            db.flush()

            # Update stock reservation (locked for this WO)
            stock.qty_reserved += total_needed

            # Record material consumption plan
            consumption = MaterialConsumption(
                work_order_id=work_order_id,
                product_id=detail.component_id,
                qty_planned=total_needed,
                lot_id=stock.lot_id
            )
            db.add(consumption)

            material_allocations.append({
                "component_id": detail.component_id,
                "component_code": stock.product.code,
                "qty_allocated": float(total_needed),
                "lot_id": stock.lot_id,
                "stock_move_id": stock_move.id
            })

            total_value += total_needed

        # Update work order status
        wo.status = WorkOrderStatus.RUNNING
        wo.start_time = datetime.utcnow()
        wo.worker_id = operator_id

        db.commit()

        return {
            "work_order_id": work_order_id,
            "mo_id": wo.mo_id,
            "material_issue_slip": {
                "slip_number": f"MAT-ISSUE-{wo.mo_id}-{work_order_id}",
                "timestamp": datetime.utcnow().isoformat(),
                "operator_id": operator_id,
                "materials": material_allocations,
                "total_items": len(material_allocations),
                "status": "Pending Stock Move Confirmation"
            }
        }

    @classmethod
    def complete_cutting_operation(
        cls,
        db: Session,
        work_order_id: int,
        actual_output: Decimal,
        reject_qty: Decimal,
        notes: str | None = None
    ) -> dict:
        """Step 220: Record cutting output and handle shortage/surplus
        Uses base class record_output_and_variance for common logic.
        """
        # Delegate to base class for common variance analysis
        result = cls.record_output_and_variance(
            db=db,
            work_order_id=work_order_id,
            actual_output=actual_output,
            reject_qty=reject_qty,
            notes=notes
        )

        # Add cutting-specific handling actions
        if result["handling_type"] == "SHORTAGE":
            result["actions_taken"].extend([
                "Generate Waste Report (Step 230)",
                "Request Approval for Additional Material (Step 240)"
            ])
        elif result["handling_type"] == "SURPLUS":
            result["actions_taken"].extend([
                "System records surplus in Surplus Log (Step 270)",
                "Trigger Auto-Revision of SPK Sewing (Step 280)"
            ])

        return result

    @classmethod
    def handle_shortage(
        cls,
        db: Session,
        work_order_id: int,
        shortage_qty: Decimal,
        reason: str
    ) -> dict:
        """Step 230-250: SHORTAGE LOGIC
        - Record waste report
        - Generate unplanned requisition
        - Await SPV approval.
        """
        wo = cls.get_work_order(db, work_order_id)

        # Create waste report
        waste_report = {
            "report_id": f"WASTE-{wo.mo_id}-{work_order_id}",
            "timestamp": datetime.utcnow().isoformat(),
            "work_order_id": work_order_id,
            "product_id": wo.product_id,
            "shortage_qty": float(shortage_qty),
            "reason": reason,
            "status": "Pending SPV Approval",
            "approval_required": "SPV Cutting"
        }

        # Mark WO as requiring approval
        wo.status = WorkOrderStatus.PENDING  # Reset to pending until approval
        db.commit()

        return {
            "waste_report": waste_report,
            "next_steps": [
                "SPV Cutting reviews shortage reason",
                "If approved: Warehouse issues additional material",
                "Resume cutting operation",
                "Update output and proceed to transfer"
            ]
        }

    @classmethod
    def check_line_clearance(
        cls,
        db: Session,
        work_order_id: int,
        destination_dept: str
    ) -> tuple[bool, str | None, dict]:
        """Step 290: LINE CLEARANCE CHECK (QT-09 Cek 1-2)
        Uses base class check_line_clearance.
        """
        # Map destination_dept string to TransferDept enum
        dept_mapping = {
            "Sewing": TransferDept.SEWING,
            "Embroidery": TransferDept.EMBROIDERY,
            "Subcon": TransferDept.SUBCON
        }

        target_dept = dept_mapping.get(destination_dept)
        if not target_dept:
            raise HTTPException(status_code=400, detail=f"Invalid destination department: {destination_dept}")

        # Delegate to base class
        return cls.check_line_clearance(db=db, work_order_id=work_order_id, target_dept=target_dept)

    @classmethod
    def create_transfer_to_next_dept(
        cls,
        db: Session,
        work_order_id: int,
        destination_dept: str,
        transfer_qty: Decimal,
        user_id: int
    ) -> dict:
        """Step 291-293: Print Transfer Slip & Handshake Digital
        Uses base class create_transfer_log.
        """
        # Map to transfer dept
        dept_mapping = {
            "Sewing": TransferDept.SEWING,
            "Embroidery": TransferDept.EMBROIDERY,
            "Subcon": TransferDept.SUBCON
        }
        target_dept = dept_mapping.get(destination_dept)
        if not target_dept:
            raise HTTPException(status_code=400, detail=f"Invalid destination department: {destination_dept}")

        # Delegate to base class (DRY principle)
        # Base class handles: transfer log creation, line occupancy, handshake protocol
        return cls.create_transfer_log(
            db=db,
            work_order_id=work_order_id,
            to_dept=target_dept,
            qty_to_transfer=transfer_qty,
            operator_id=user_id
        )
