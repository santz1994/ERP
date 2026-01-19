"""
Sewing Module Business Logic & Services
Handles material input validation, 3-stage sewing, inline QC, segregation, and transfer
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.core.models.manufacturing import WorkOrder, ManufacturingOrder, MaterialConsumption, Department, WorkOrderStatus
from app.core.models.transfer import TransferLog, TransferStatus, LineOccupancy, TransferDept
from app.core.models.products import Product
from app.core.models.bom import BOMDetail, BOMHeader
from app.core.models.quality import QCInspection
from decimal import Decimal
from datetime import datetime
from typing import Optional, Tuple, Dict
from fastapi import HTTPException


class SewingService:
    """Business logic for sewing department operations"""
    
    @staticmethod
    def accept_transfer_and_validate(
        db: Session,
        transfer_slip_number: str,
        received_qty: Decimal,
        user_id: int,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 300: Accept Transfer & Material Validation
        - Scan transfer slip (Handshake ACCEPT from Cutting/Embroidery)
        - Unlock stock from previous dept
        - Record material receipt
        - Prepare for qty validation vs BOM
        """
        
        # Find transfer log
        transfer = db.query(TransferLog).filter(
            TransferLog.status == TransferStatus.LOCKED
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=404,
                detail=f"No pending transfer found. Ensure Cutting has printed transfer slip."
            )
        
        if transfer.status != TransferStatus.LOCKED:
            raise HTTPException(
                status_code=400,
                detail=f"Transfer status is {transfer.status.value}, expected LOCKED"
            )
        
        # Step 293 (from Cutting): Digital Handshake - Accept
        transfer.status = TransferStatus.ACCEPTED
        transfer.qty_received = received_qty
        transfer.timestamp_accept = datetime.utcnow()
        transfer.accepted_by = user_id
        
        # Get work order
        wo = db.query(WorkOrder).filter(
            WorkOrder.mo_id == transfer.mo_id,
            WorkOrder.department == Department.SEWING
        ).first()
        
        if not wo:
            raise HTTPException(status_code=404, detail="Sewing work order not found")
        
        wo.input_qty = received_qty
        wo.status = WorkOrderStatus.RUNNING
        wo.start_time = datetime.utcnow()
        wo.worker_id = user_id
        
        # Update line occupancy - mark Cutting line as CLEAR (line clearance complete)
        cutting_line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == TransferDept.CUTTING
        ).first()
        if cutting_line:
            cutting_line.status = "Clear"
            cutting_line.current_article = None
        
        db.commit()
        
        return {
            "transfer_slip_number": transfer_slip_number,
            "received_qty": float(received_qty),
            "handshake_status": "ACCEPTED",
            "work_order_id": wo.id,
            "next_step": "Validate input qty vs BOM",
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def validate_input_vs_bom(
        db: Session,
        work_order_id: int,
        received_qty: Decimal
    ) -> dict:
        """
        Step 310: VALIDASI INPUT - Check Received Qty vs BOM Target
        - Compare received material vs BOM requirements
        - If shortage: Auto-request additional material (Step 320)
        - If OK: Proceed to assembly
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        # Get BOM
        bom = db.query(BOMHeader).filter(
            BOMHeader.product_id == wo.product_id,
            BOMHeader.is_active == True
        ).first()
        
        if not bom:
            raise HTTPException(status_code=404, detail=f"No active BOM for product {wo.product_id}")
        
        # Get target from BOM
        target_qty = bom.qty_output if bom.qty_output > 0 else received_qty
        
        # Compare
        variance = received_qty - target_qty
        
        result = {
            "work_order_id": work_order_id,
            "received_qty": float(received_qty),
            "target_qty": float(target_qty),
            "variance": float(variance),
            "status": "OK"
        }
        
        if variance < 0:
            # Shortage - Step 320: Auto-request supplementary materials
            shortage = abs(variance)
            result["status"] = "SHORTAGE"
            result["shortage_qty"] = float(shortage)
            result["action"] = "AUTO-REQ: Requesting additional label/benang"
            result["requisition_status"] = "Pending Warehouse Approval"
        
        elif variance > 0:
            # Surplus
            result["status"] = "SURPLUS"
            result["surplus_qty"] = float(variance)
            result["action"] = "Material surplus - proceed with full qty"
        
        return result
    
    @staticmethod
    def process_sewing_step(
        db: Session,
        work_order_id: int,
        step_number: int,
        qty_processed: Decimal,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 330-350: 3-Stage Sewing Process
        - Step 330: Proses Jahit 1 - Assembly (rakit body)
        - Step 340: Proses Jahit 2 - Labeling (attach label)
        - Step 350: Proses Jahit 3 - Stik Balik (loop stitching)
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        stage_names = {
            1: "Assembly (Rakit Body)",
            2: "Labeling (Attach Label)",
            3: "Stik Balik (Loop Stitching)"
        }
        
        if step_number not in [1, 2, 3]:
            raise HTTPException(status_code=400, detail="Invalid step number. Must be 1, 2, or 3")
        
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
        """
        Step 360-375: INLINE QC INSPECTION
        - Step 360: Check jahitan quality
        - Step 370: Rework process (can go back to step 350)
        - Step 375: Scrap/reject flow
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        total_qty = pass_qty + rework_qty + scrap_qty
        
        if total_qty != wo.input_qty:
            raise HTTPException(
                status_code=400,
                detail=f"Total inspected qty ({total_qty}) != input qty ({wo.input_qty})"
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
            "pass_rate": float(pass_qty / wo.input_qty * 100 if wo.input_qty > 0 else 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if rework_qty > 0:
            result["rework_action"] = "Step 370: Send to rework - return to Stik Balik"
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
    ) -> Tuple[bool, Optional[str], dict]:
        """
        Step 380: SEGREGASI CHECK - Verify Destination Consistency
        
        QT-09 Segregation Rule:
        - All WIP in same batch MUST go to same destination/week
        - If destination DIFFERS from current line → ALARM
        - If different: Require 5-meter jeda or manual line clearance
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        # Get current line destination (from last batch on Finishing line)
        finishing_line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == TransferDept.FINISHING
        ).first()
        
        current_destination = finishing_line.destination if finishing_line else None
        batch_destination = mo.destination if hasattr(mo, 'destination') else None
        
        destinations_match = (current_destination == batch_destination) or (current_destination is None)
        
        check_result = {
            "work_order_id": work_order_id,
            "batch_destination": batch_destination,
            "current_line_destination": current_destination,
            "destinations_match": destinations_match,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        blocking_reason = None
        if not destinations_match:
            blocking_reason = f"ALARM: Destination mismatch - Line has {current_destination}, batch is {batch_destination}. Require 5m jeda or line clearance."
            check_result["alarm"] = blocking_reason
            check_result["segregation_status"] = "BLOCKED - Destination Mismatch"
            check_result["requires_jeda"] = True
            check_result["jeda_duration_minutes"] = 5
        else:
            check_result["segregation_status"] = "CLEAR - Same destination"
            check_result["requires_jeda"] = False
        
        return destinations_match, blocking_reason, check_result
    
    @staticmethod
    def transfer_to_finishing(
        db: Session,
        work_order_id: int,
        transfer_qty: Decimal,
        user_id: int
    ) -> dict:
        """
        Step 381-383: Print Transfer & Handshake Digital
        - Step 381: Print Surat Jalan to Finishing
        - Step 383: HANDSHAKE - Lock WIP SEW (same pattern as Cutting)
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        # Create transfer log (Step 381: Print Surat Jalan)
        transfer = TransferLog(
            mo_id=wo.mo_id,
            from_dept=TransferDept.SEWING,
            to_dept=TransferDept.FINISHING,
            article_code=wo.product.code,
            batch_id=mo.batch_number,
            qty_sent=transfer_qty,
            is_line_clear=True,
            line_checked_by=user_id,
            line_checked_at=datetime.utcnow(),
            status=TransferStatus.LOCKED  # Step 383: HANDSHAKE - Lock WIP SEW
        )
        db.add(transfer)
        db.flush()
        
        # Update line occupancy
        sewing_line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == TransferDept.SEWING
        ).first()
        if sewing_line:
            sewing_line.status = "Occupied"
            sewing_line.current_article = wo.product.code
            sewing_line.current_batch = mo.batch_number
        
        db.commit()
        
        return {
            "transfer_slip": {
                "slip_number": f"TSLIP-{mo.batch_number}-{transfer.id}",
                "timestamp": datetime.utcnow().isoformat(),
                "from_dept": "Sewing",
                "to_dept": "Finishing",
                "article_code": wo.product.code,
                "batch_number": mo.batch_number,
                "qty_sent": float(transfer_qty),
                "status": "LOCKED",
                "handshake_protocol": "QT-09 (Awaiting ACCEPT from Finishing)"
            },
            "handshake_info": {
                "stock_locked": True,
                "lock_time": datetime.utcnow().isoformat(),
                "lock_reason": "Digital Handshake - Awaiting Finishing department ACCEPT",
                "next_action": "Operator in Finishing scans transfer slip to ACCEPT"
            }
        }
