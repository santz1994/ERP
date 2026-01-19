"""
Packing Module Business Logic & Services
Handles sorting, packaging, and shipping mark generation
"""

from sqlalchemy.orm import Session
from app.core.models.manufacturing import WorkOrder, ManufacturingOrder, Department, WorkOrderStatus
from app.core.models.products import Product
from decimal import Decimal
from datetime import datetime
from typing import Optional
from fastapi import HTTPException
import uuid


class PackingService:
    """Business logic for packing department operations"""
    
    @staticmethod
    def sort_by_destination_and_week(
        db: Session,
        work_order_id: int,
        qty_sorted: Decimal,
        destination: str,
        week_number: Optional[int] = None
    ) -> dict:
        """
        Step 470: Sortir by Week & Destination
        - Categorize finish good by destination country
        - Group by delivery week
        - Prepare for cartonization
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        return {
            "work_order_id": work_order_id,
            "operation": "Sort by Destination & Week",
            "qty_sorted": float(qty_sorted),
            "destination": destination,
            "week_number": week_number,
            "batch_number": mo.batch_number,
            "timestamp": datetime.utcnow().isoformat(),
            "next_step": "Step 480: Package into cartons",
            "status": "Sorting Complete - Ready for cartonization"
        }
    
    @staticmethod
    def package_into_cartons(
        db: Session,
        work_order_id: int,
        qty_packaged: Decimal,
        pcs_per_carton: int,
        num_cartons: int,
        notes: Optional[str] = None
    ) -> dict:
        """
        Step 480: Masukkan Polybag & Carton
        - Pack items into individual polybags (for product protection)
        - Place polybag-wrapped items into shipping cartons
        - Record carton count and packing details
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        # Validate carton count
        expected_cartons = qty_packaged / pcs_per_carton
        if num_cartons < int(expected_cartons):
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient cartons: {qty_packaged} items ÷ {pcs_per_carton} pcs/carton = {expected_cartons} cartons, but only {num_cartons} provided"
            )
        
        return {
            "work_order_id": work_order_id,
            "operation": "Package into Cartons",
            "qty_packaged": float(qty_packaged),
            "pcs_per_carton": pcs_per_carton,
            "num_cartons": num_cartons,
            "avg_fill_rate": float((qty_packaged / (num_cartons * pcs_per_carton)) * 100),
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat(),
            "next_step": "Step 490: Generate Shipping Marks",
            "status": "Cartonization Complete"
        }
    
    @staticmethod
    def generate_shipping_mark(
        db: Session,
        work_order_id: int,
        carton_number: int,
        fg_code: str,
        qty_in_carton: int,
        destination: str,
        week_number: int,
        user_id: int
    ) -> dict:
        """
        Step 490: Generate Shipping Mark
        - Create barcode label for carton
        - Include: Article code, qty, destination, week
        - Generate QR code for tracking
        - Print physical label
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        # Generate unique mark ID
        mark_id = f"MARK-{mo.batch_number}-{carton_number:04d}"
        barcode_number = f"{destination}{week_number:02d}{fg_code}{carton_number:06d}"
        
        return {
            "shipping_mark_id": mark_id,
            "barcode_number": barcode_number,
            "carton_label": {
                "carton_number": f"{carton_number:04d}",
                "fg_code": fg_code,
                "qty": qty_in_carton,
                "destination": destination,
                "week": week_number,
                "batch": mo.batch_number
            },
            "timestamp": datetime.utcnow().isoformat(),
            "generated_by": user_id,
            "print_instructions": f"Print label for carton {carton_number} and apply to top of box",
            "next_step": "Physical printing & label attachment",
            "status": "Shipping Mark Generated - Ready to Print"
        }
    
    @staticmethod
    def complete_packing(
        db: Session,
        work_order_id: int,
        total_cartons: int,
        total_pcs: Decimal
    ) -> dict:
        """
        Complete packing operation
        - Final qty confirmation
        - Mark WO as completed
        - Prepare for logistics/FG warehouse
        """
        
        wo = db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        if not wo:
            raise HTTPException(status_code=404, detail=f"Work order {work_order_id} not found")
        
        wo.output_qty = total_pcs
        wo.status = WorkOrderStatus.FINISHED
        wo.end_time = datetime.utcnow()
        
        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
        
        db.commit()
        
        return {
            "work_order_id": work_order_id,
            "operation": "Packing Completed",
            "total_cartons": total_cartons,
            "total_pcs": float(total_pcs),
            "batch_number": mo.batch_number,
            "completed_at": datetime.utcnow().isoformat(),
            "next_step": "Transfer to Finish Good Warehouse",
            "status": "COMPLETED - Ready for logistics"
        }
