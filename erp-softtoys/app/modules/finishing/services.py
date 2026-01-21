"""
Finishing Module Business Logic & Services
Handles stuffing, closing, metal detector QC, and conversion to FG

Refactored: Now extends BaseProductionService to eliminate code duplication
"""

from sqlalchemy.orm import Session
from app.core.models.manufacturing import (
    WorkOrder, ManufacturingOrder, Department, WorkOrderStatus
)
from app.core.models.transfer import (
    TransferLog, TransferStatus, LineOccupancy, TransferDept
)
from app.core.models.quality import QCInspection
from app.core.models.products import Product
from app.core.base_production_service import BaseProductionService
from decimal import Decimal
from datetime import datetime
from typing import Optional, Tuple
from fastapi import HTTPException


class FinishingService(BaseProductionService):
    """
    Business logic for finishing department operations
    Extends BaseProductionService for common production patterns
    """
    
    # Department configuration
    DEPARTMENT = Department.FINISHING
    DEPARTMENT_NAME = "Finishing"
    TRANSFER_DEPT = TransferDept.FINISHING
    
    @classmethod
    def accept_wip_transfer(
        cls,
        db: Session,
        transfer_slip_number: str,
        received_qty: Decimal,
        user_id: int,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 400: Accept WIP SEW from Sewing
        Uses base class accept_transfer_from_previous_dept
        """
        # Delegate to base class
        result = cls.accept_transfer_from_previous_dept(
            db=db,
            transfer_slip_number=transfer_slip_number,
            received_qty=received_qty,
            user_id=user_id,
            from_dept=TransferDept.SEWING,
            notes=notes
        )
        
        # Add finishing-specific next step
        result["next_step"] = "Line Clearance Check (Step 405-406)"
        
        return result
    
    @classmethod
    def check_line_clearance_packing(
        cls,
        db: Session,
        work_order_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Step 405-406: LINE CLEARANCE CHECK (Packing Line)
        Uses base class check_line_clearance
        """
        # Delegate to base class
        return cls.check_line_clearance(
            db=db,
            work_order_id=work_order_id,
            target_dept=TransferDept.PACKING
        )
    
    @staticmethod
    def perform_stuffing(
        db: Session,
        work_order_id: int,
        operator_id: int,
        stuffing_material: str,
        qty_stuffed: Decimal,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 410: Perform Stuffing (Isi Dacron)
        - Add filling material
        - Record qty completed
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        return {
            "work_order_id": work_order_id,
            "operation": "Stuffing - Isi Dacron",
            "stuffing_material": stuffing_material,
            "qty_stuffed": float(qty_stuffed),
            "operator_id": operator_id,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes,
            "next_step": "Step 420: Closing & Grooming"
        }
    
    @staticmethod
    def perform_closing_and_grooming(
        db: Session,
        work_order_id: int,
        operator_id: int,
        qty_closed: Decimal,
        quality_notes: Optional[str] = None
    ) -> dict:
        """
        Step 420: Closing & Grooming (Jahit Tutup & Rapih)
        - Close seams
        - Groom/straighten product
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        return {
            "work_order_id": work_order_id,
            "operation": "Closing & Grooming",
            "qty_closed": float(qty_closed),
            "operator_id": operator_id,
            "quality_notes": quality_notes,
            "timestamp": datetime.utcnow().isoformat(),
            "next_step": "Step 430: CRITICAL - Metal Detector Test"
        }
    
    @staticmethod
    def metal_detector_test(
        db: Session,
        work_order_id: int,
        inspector_id: int,
        pass_qty: Decimal,
        fail_qty: Decimal,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 430-435: CRITICAL POINT - Metal Detector Test
        - Step 430: Run metal detector
        - Step 435: If fail → Segregate & investigate
        
        This is a **CRITICAL QC POINT** - IKEA requirement for safety
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        # Create QC record
        qc = QCInspection(
            work_order_id=work_order_id,
            type="Final Metal Detector",
            status="Pass" if fail_qty == 0 else "Fail",
            defect_reason=f"Metal detected in {fail_qty} units" if fail_qty > 0 else None,
            inspected_by=inspector_id
        )
        db.add(qc)
        db.commit()
        
        result = {
            "work_order_id": work_order_id,
            "qc_inspection_id": qc.id,
            "operation": "CRITICAL - Metal Detector Test",
            "pass_qty": float(pass_qty),
            "fail_qty": float(fail_qty),
            "pass_rate": float(pass_qty / (pass_qty + fail_qty) * 100 if (pass_qty + fail_qty) > 0 else 0),
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes
        }
        
        if fail_qty > 0:
            result["status"] = "BLOCKED"
            result["action"] = f"Step 435: Segregate & Investigate {fail_qty} units"
            result["severity"] = "CRITICAL"
            result["next_step"] = "QC Supervisor review required"
            # Metal detected is a critical failure
            wo.reject_qty = (wo.reject_qty or 0) + fail_qty
        else:
            result["status"] = "PASSED"
            result["next_step"] = "Step 440: Physical & Symmetry Check"
        
        db.commit()
        
        return result
    
    @staticmethod
    def physical_qc_check(
        db: Session,
        work_order_id: int,
        inspector_id: int,
        pass_qty: Decimal,
        repair_qty: Decimal,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 440-445: Physical & Symmetry QC Check
        - Check physical appearance
        - Verify symmetry
        - If fail → repair (Step 445)
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        result = {
            "work_order_id": work_order_id,
            "operation": "Physical & Symmetry Check",
            "pass_qty": float(pass_qty),
            "repair_qty": float(repair_qty),
            "inspector_id": inspector_id,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if repair_qty > 0:
            result["action"] = f"Step 445: Repair/Cleaning {repair_qty} units"
            result["next_step"] = "Return to Physical Check"
        else:
            result["next_step"] = "Step 450: Conversion to FG Code"
        
        return result
    
    @staticmethod
    def convert_wip_to_fg(
        db: Session,
        work_order_id: int,
        wip_product_id: int,
        fg_product_id: int,
        qty_converted: Decimal,
        user_id: int
    ) -> dict:
        """
        Step 450: CONVERSION - Transform WIP Code to FG (Finish Good) Code
        - Change from internal WIP code (e.g., WIP-FIN-SHARK-001)
        - To external IKEA article code (e.g., BLAHAJ-100)
        - This is the point where product becomes "Finish Good"
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        # Get product codes
        wip_product = db.query(Product).filter(Product.id == wip_product_id).first()
        fg_product = db.query(Product).filter(Product.id == fg_product_id).first()
        
        if not wip_product or not fg_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Record conversion
        wo.output_qty = qty_converted
        mo.qty_produced = (mo.qty_produced or 0) + qty_converted
        
        db.commit()
        
        return {
            "work_order_id": work_order_id,
            "operation": "CONVERSION to Finish Good",
            "wip_code": wip_product.code,
            "fg_code": fg_product.code,
            "qty_converted": float(qty_converted),
            "conversion_completed_at": datetime.utcnow().isoformat(),
            "converted_by": user_id,
            "batch_number": mo.batch_number,
            "next_step": "Step 460: Packing Instructions & Sortation"
        }
