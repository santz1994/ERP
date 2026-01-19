"""
Cutting Module Business Logic & Services
Handles material allocation, output tracking, QT-09 protocol
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from app.core.models.manufacturing import WorkOrder, ManufacturingOrder, MaterialConsumption, Department, WorkOrderStatus
from app.core.models.warehouse import StockQuant, StockMove, Location
from app.core.models.transfer import TransferLog, TransferStatus, LineOccupancy, TransferDept
from app.core.models.products import Product
from decimal import Decimal
from datetime import datetime
from typing import Optional, Tuple, List
from fastapi import HTTPException


class CuttingService:
    """Business logic for cutting department operations"""
    
    @staticmethod
    def receive_spk_and_allocate_material(
        db: Session,
        work_order_id: int,
        operator_id: int
    ) -> dict:
        """
        Step 200: Receive SPK & Allocate Material
        - Check material availability
        - Create stock move (warehouse → cutting line)
        - Return material issue slip info
        """
        
        # Fetch work order
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        if wo.status != WorkOrderStatus.PENDING:
            raise HTTPException(status_code=400, detail=f"Cannot allocate material for WO in {wo.status} status")
        
        # Fetch BOM to get material requirements
        from app.core.models.bom import BOMHeader, BOMDetail
        bom = db.query(BOMHeader).filter(
            BOMHeader.product_id == wo.product_id,
            BOMHeader.is_active == True
        ).first()
        
        if not bom:
            raise HTTPException(status_code=404, detail=f"No active BOM for product {wo.product_id}")
        
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
                shortage = total_needed - (stock.qty_on_hand - stock.qty_reserved if stock else 0)
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
    
    @staticmethod
    def complete_cutting_operation(
        db: Session,
        work_order_id: int,
        actual_output: Decimal,
        reject_qty: Decimal,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 220: Record cutting output and handle shortage/surplus
        - Record actual output
        - Check vs target (shortage/surplus handling)
        - Prepare for transfer
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        if wo.status != WorkOrderStatus.RUNNING:
            raise HTTPException(status_code=400, detail=f"Cannot complete WO in {wo.status} status")
        
        # Get MO for target quantity
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        # Record output
        wo.output_qty = actual_output
        wo.reject_qty = reject_qty
        wo.end_time = datetime.utcnow()
        wo.status = WorkOrderStatus.FINISHED
        
        # Update MO total produced
        mo.qty_produced = (mo.qty_produced or 0) + actual_output
        
        db.commit()
        
        # Analyze shortage/surplus
        variance = actual_output - wo.input_qty
        variance_percentage = (variance / wo.input_qty * 100) if wo.input_qty > 0 else 0
        
        handling_result = {
            "work_order_id": work_order_id,
            "actual_output": float(actual_output),
            "target": float(wo.input_qty),
            "variance": float(variance),
            "variance_percentage": float(variance_percentage),
            "reject_qty": float(reject_qty),
            "notes": notes,
            "handling_type": None,
            "actions_taken": []
        }
        
        if variance < 0:  # SHORTAGE
            shortage_qty = abs(variance)
            handling_result["handling_type"] = "SHORTAGE"
            handling_result["actions_taken"] = [
                f"Shortage detected: {shortage_qty} units short",
                "Generate Waste Report (Step 230)",
                "Request Approval for Additional Material (Step 240)",
                "Awaiting SPV approval for unplanned requisition"
            ]
        
        elif variance > 0:  # SURPLUS
            surplus_qty = variance
            handling_result["handling_type"] = "SURPLUS"
            handling_result["actions_taken"] = [
                f"Surplus detected: {surplus_qty} units extra",
                "System records surplus in Surplus Log (Step 270)",
                "Trigger Auto-Revision of SPK Sewing (Step 280)",
                "Update downstream SPK with new material quantities"
            ]
        
        else:  # EXACT
            handling_result["handling_type"] = "EXACT"
            handling_result["actions_taken"] = [
                "Output matches target - no variance",
                "Ready for transfer to next department"
            ]
        
        return handling_result
    
    @staticmethod
    def handle_shortage(
        db: Session,
        work_order_id: int,
        shortage_qty: Decimal,
        reason: str
    ) -> dict:
        """
        Step 230-250: SHORTAGE LOGIC
        - Record waste report
        - Generate unplanned requisition
        - Await SPV approval
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
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
    
    @staticmethod
    def check_line_clearance(
        db: Session,
        work_order_id: int,
        destination_dept: str
    ) -> Tuple[bool, Optional[str], dict]:
        """
        Step 290: LINE CLEARANCE CHECK (QT-09 Cek 1-2)
        - Verify destination line is empty (no previous batch)
        - Check line status
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        # Map destination_dept to TransferDept enum
        dept_mapping = {
            "Sewing": TransferDept.SEWING,
            "Embroidery": TransferDept.EMBROIDERY,
            "Subcon": TransferDept.SUBCON
        }
        
        target_dept = dept_mapping.get(destination_dept)
        if not target_dept:
            raise HTTPException(status_code=400, detail=f"Invalid destination department: {destination_dept}")
        
        # Check line occupancy
        line_occupancy = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == target_dept
        ).first()
        
        if not line_occupancy:
            # Create new line occupancy if doesn't exist
            line_occupancy = LineOccupancy(
                dept_name=target_dept,
                current_article=None,
                current_batch=None,
                status="Clear"
            )
            db.add(line_occupancy)
            db.flush()
        
        # Check if line is clear
        is_clear = line_occupancy.status == "Clear" or line_occupancy.current_article is None
        
        blocking_reason = None
        if not is_clear:
            blocking_reason = f"{destination_dept} line still processing: {line_occupancy.current_article} (batch: {line_occupancy.current_batch})"
        
        line_check_info = {
            "work_order_id": work_order_id,
            "destination_dept": destination_dept,
            "line_status": line_occupancy.status,
            "current_article": line_occupancy.current_article,
            "current_batch": line_occupancy.current_batch,
            "can_transfer": is_clear,
            "blocking_reason": blocking_reason,
            "checked_at": datetime.utcnow().isoformat()
        }
        
        return is_clear, blocking_reason, line_check_info
    
    @staticmethod
    def create_transfer_to_next_dept(
        db: Session,
        work_order_id: int,
        destination_dept: str,
        transfer_qty: Decimal,
        user_id: int
    ) -> dict:
        """
        Step 291-293: Print Transfer Slip & Handshake Digital
        - Line clearance verified
        - Create transfer log
        - Lock WIP CUT in system (Handshake Step 3)
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        # Map to transfer dept
        dept_mapping = {
            "Sewing": TransferDept.SEWING,
            "Embroidery": TransferDept.EMBROIDERY,
            "Subcon": TransferDept.SUBCON
        }
        target_dept = dept_mapping[destination_dept]
        
        # Create transfer log (Step 291: Print Surat Jalan)
        transfer = TransferLog(
            mo_id=wo.mo_id,
            from_dept=TransferDept.CUTTING,
            to_dept=target_dept,
            article_code=wo.product.code,
            batch_id=mo.batch_number,
            qty_sent=transfer_qty,
            is_line_clear=True,
            line_checked_by=user_id,
            line_checked_at=datetime.utcnow(),
            status=TransferStatus.LOCKED  # Step 293: HANDSHAKE - Lock the stock
        )
        db.add(transfer)
        db.flush()
        
        # Update line occupancy
        line_occ = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == target_dept
        ).first()
        if line_occ:
            line_occ.status = "Occupied"
            line_occ.current_article = wo.product.code
            line_occ.current_batch = mo.batch_number
        
        db.commit()
        
        return {
            "transfer_slip": {
                "slip_number": f"TSLIP-{mo.batch_number}-{transfer.id}",
                "timestamp": datetime.utcnow().isoformat(),
                "from_dept": "Cutting",
                "to_dept": destination_dept,
                "article_code": wo.product.code,
                "batch_number": mo.batch_number,
                "qty_sent": float(transfer_qty),
                "status": "LOCKED",
                "handshake_protocol": "QT-09 (Awaiting ACCEPT from receiving dept)"
            },
            "handshake_info": {
                "stock_locked": True,
                "lock_time": datetime.utcnow().isoformat(),
                "lock_reason": "Digital Handshake - Awaiting receiving department ACCEPT",
                "next_action": f"Operator in {destination_dept} scans transfer slip to ACCEPT"
            }
        }
