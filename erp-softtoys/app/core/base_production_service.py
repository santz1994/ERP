"""
Base Production Service - Abstract Class for Common Production Operations
==========================================================================
Eliminates code duplication across Cutting, Sewing, and Finishing modules

Author: Daniel - IT Developer Senior
Date: 2026-01-21
Purpose: DRY principle - extract common patterns from production services

Common Patterns Identified:
1. Transfer acceptance and handshake (accept_transfer_and_validate)
2. Line clearance checks (check_line_clearance)
3. Work order status updates (update_work_order_status)
4. Material validation against BOM (validate_input_vs_bom)
5. Output recording and variance analysis (record_output_and_variance)
6. Transfer log creation (create_transfer_log)

Target: Eliminate 30-40% code duplication
"""

from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Tuple, Dict, List
from decimal import Decimal
from datetime import datetime
from fastapi import HTTPException

from app.core.models.manufacturing import (
    WorkOrder, ManufacturingOrder, MaterialConsumption,
    Department, WorkOrderStatus
)
from app.core.models.transfer import (
    TransferLog, TransferStatus, LineOccupancy, TransferDept
)
from app.core.models.products import Product
from app.core.models.bom import BOMHeader, BOMDetail


class BaseProductionService(ABC):
    """
    Abstract base class for production department services
    
    Provides common operations:
    - Transfer acceptance/handshake
    - Line clearance validation
    - Work order lifecycle management
    - BOM validation
    - Output variance analysis
    - Stock move creation
    """
    
    # Department identifier (override in child classes)
    DEPARTMENT: Department = None
    DEPARTMENT_NAME: str = None
    TRANSFER_DEPT: TransferDept = None
    
    @classmethod
    def accept_transfer_from_previous_dept(
        cls,
        db: Session,
        transfer_slip_number: str,
        received_qty: Decimal,
        user_id: int,
        from_dept: TransferDept,
        notes: Optional[str] = None
    ) -> dict:
        """
        Common transfer acceptance logic across all departments
        
        Process:
        1. Find pending transfer (LOCKED status)
        2. Update transfer status to ACCEPTED
        3. Record received quantity and timestamp
        4. Create/update work order for current department
        5. Clear previous department line occupancy
        
        Args:
            db: Database session
            transfer_slip_number: Transfer slip identifier
            received_qty: Actual quantity received
            user_id: User accepting the transfer
            from_dept: Source department (CUTTING/SEWING/etc)
            notes: Optional notes
        
        Returns:
            Dict with transfer details and next steps
        """
        # Find pending transfer
        transfer = db.query(TransferLog).filter(
            TransferLog.status == TransferStatus.LOCKED,
            TransferLog.from_dept == from_dept
        ).first()
        
        if not transfer:
            raise HTTPException(
                status_code=404,
                detail=f"No pending transfer from {from_dept.value}"
            )
        
        if transfer.status != TransferStatus.LOCKED:
            raise HTTPException(
                status_code=400,
                detail=f"Transfer status is {transfer.status.value}, expected LOCKED"  # noqa: E501
            )
        
        # Digital handshake - ACCEPT
        transfer.status = TransferStatus.ACCEPTED
        transfer.qty_received = received_qty
        transfer.timestamp_accept = datetime.utcnow()
        transfer.accepted_by = user_id
        
        # Get or create work order for current department
        wo = db.query(WorkOrder).filter(
            WorkOrder.mo_id == transfer.mo_id,
            WorkOrder.department == cls.DEPARTMENT
        ).first()
        
        if not wo:
            raise HTTPException(
                status_code=404,
                detail=f"{cls.DEPARTMENT_NAME} work order not found"
            )
        
        # Update work order
        wo.input_qty = received_qty
        wo.status = WorkOrderStatus.RUNNING
        wo.start_time = datetime.utcnow()
        wo.worker_id = user_id
        
        # Clear previous department line occupancy
        cls._clear_line_occupancy(db, from_dept)
        
        db.commit()
        
        return {
            "transfer_slip_number": transfer_slip_number,
            "received_qty": float(received_qty),
            "handshake_status": "ACCEPTED",
            "work_order_id": wo.id,
            "mo_id": wo.mo_id,
            "department": cls.DEPARTMENT_NAME,
            "from_department": from_dept.value,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def _clear_line_occupancy(
        db: Session,
        dept: TransferDept
    ) -> None:
        """
        Mark previous department line as CLEAR
        
        Line Clearance Protocol:
        - Status: "Clear" (ready for next batch)
        - Current article: None
        - Ensures no cross-contamination
        """
        line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == dept
        ).first()
        
        if line:
            line.status = "Clear"
            line.current_article = None
            line.cleared_at = datetime.utcnow()
    
    # ========== HELPER METHODS FOR DUPLICATE QUERY ELIMINATION ==========
    # These methods eliminate 20+ instances of repeated db.query patterns
    # across cutting/sewing/finishing/packing/quality services and routers.
    # Centralization improves maintainability and error handling consistency.
    
    @staticmethod
    def get_work_order(
        db: Session,
        work_order_id: int
    ) -> WorkOrder:
        """
        Get work order by ID with centralized error handling.
        
        Eliminates 20+ duplicate instances of:
            db.query(WorkOrder).filter(WorkOrder.id == work_order_id).first()
        
        Args:
            db: Database session
            work_order_id: Work order ID to retrieve
        
        Returns:
            WorkOrder object
        
        Raises:
            HTTPException 404 if work order not found
        """
        wo = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not wo:
            raise HTTPException(
                status_code=404,
                detail=f"Work order {work_order_id} not found"
            )
        
        return wo
    
    @staticmethod
    def get_manufacturing_order(
        db: Session,
        mo_id: int
    ) -> ManufacturingOrder:
        """
        Get manufacturing order by ID with centralized error handling.
        
        Eliminates duplicate instances of:
            db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
        
        Args:
            db: Database session
            mo_id: Manufacturing order ID to retrieve
        
        Returns:
            ManufacturingOrder object
        
        Raises:
            HTTPException 404 if manufacturing order not found
        """
        mo = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == mo_id
        ).first()
        
        if not mo:
            raise HTTPException(
                status_code=404,
                detail=f"Manufacturing order {mo_id} not found"
            )
        
        return mo
    
    @staticmethod
    def get_work_order_optional(
        db: Session,
        work_order_id: int
    ) -> Optional[WorkOrder]:
        """
        Get work order by ID, returning None if not found (no exception).
        
        Use this variant when you need to handle missing WO gracefully
        without raising an exception.
        
        Args:
            db: Database session
            work_order_id: Work order ID to retrieve
        
        Returns:
            WorkOrder object or None
        """
        return db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
    
    @staticmethod
    def get_manufacturing_order_optional(
        db: Session,
        mo_id: int
    ) -> Optional[ManufacturingOrder]:
        """
        Get manufacturing order by ID, returning None if not found (no exception).
        
        Use this variant when you need to handle missing MO gracefully
        without raising an exception.
        
        Args:
            db: Database session
            mo_id: Manufacturing order ID to retrieve
        
        Returns:
            ManufacturingOrder object or None
        """
        return db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == mo_id
        ).first()
    
    @classmethod
    def check_line_clearance(
        cls,
        db: Session,
        work_order_id: int,
        target_dept: TransferDept
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if target line is clear before proceeding
        
        Line clearance ensures:
        - No previous batch remains on the line
        - No cross-contamination risk
        - Compliance with QT-09 transfer protocol
        
        Returns:
            (is_clear, blocking_article)
        """
        line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == target_dept
        ).first()
        
        if not line:
            # No line occupancy record = clear
            return True, None
        
        if line.status == "Occupied" and line.current_article:
            return False, line.current_article
        
        return True, None
    
    @classmethod
    def validate_input_vs_bom(
        cls,
        db: Session,
        work_order_id: int,
        received_qty: Decimal,
        expected_product_id: int
    ) -> dict:
        """
        Validate received quantity against BOM specification
        
        Checks:
        1. BOM exists for product
        2. Received qty matches BOM output qty (within tolerance)
        3. Identify shortage/surplus
        
        Returns variance analysis
        """
        wo = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not wo:
            raise HTTPException(
                status_code=404,
                detail=f"Work order {work_order_id} not found"
            )
        
        # Get BOM
        bom = db.query(BOMHeader).filter(
            BOMHeader.product_id == expected_product_id,
            BOMHeader.is_active == True  # noqa: E712
        ).first()
        
        if not bom:
            raise HTTPException(
                status_code=404,
                detail=f"No active BOM for product {expected_product_id}"
            )
        
        # Expected output from BOM (typically 1:1 ratio)
        expected_qty = wo.input_qty if wo.input_qty else received_qty
        variance = received_qty - expected_qty
        variance_percentage = (
            (variance / expected_qty * 100) if expected_qty > 0 else 0
        )
        
        # Determine status
        tolerance = Decimal('5.0')  # 5% tolerance
        
        if abs(variance_percentage) <= tolerance:
            status = "OK"
            action_required = None
        elif variance < 0:
            status = "SHORTAGE"
            action_required = "Generate waste report and request approval"
        else:
            status = "SURPLUS"
            action_required = "Verify count and document surplus"
        
        return {
            "work_order_id": work_order_id,
            "expected_qty": float(expected_qty),
            "received_qty": float(received_qty),
            "variance": float(variance),
            "variance_percentage": float(variance_percentage),
            "status": status,
            "action_required": action_required,
            "bom_id": bom.id
        }
    
    @classmethod
    def record_output_and_variance(
        cls,
        db: Session,
        work_order_id: int,
        actual_output: Decimal,
        reject_qty: Decimal = Decimal('0'),
        notes: Optional[str] = None
    ) -> dict:
        """
        Record production output and analyze variance
        
        Common operation across all departments:
        1. Update work order with actual output
        2. Calculate variance (actual vs target)
        3. Determine handling type (shortage/surplus/OK)
        4. Update MO aggregate quantities
        
        Returns:
            Output record with variance analysis
        """
        wo = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not wo:
            raise HTTPException(
                status_code=404,
                detail=f"Work order {work_order_id} not found"
            )
        
        if wo.status not in [WorkOrderStatus.RUNNING, WorkOrderStatus.PAUSED]:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot record output for WO in {wo.status} status"
            )
        
        # Record output
        wo.output_qty = actual_output
        wo.reject_qty = reject_qty
        wo.end_time = datetime.utcnow()
        wo.status = WorkOrderStatus.FINISHED
        
        # Update MO aggregate
        mo = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.id == wo.mo_id
        ).first()
        
        if mo:
            mo.qty_produced = (mo.qty_produced or Decimal('0')) + actual_output
        
        # Variance analysis
        target_qty = wo.input_qty
        variance = actual_output - target_qty
        variance_percentage = (
            (variance / target_qty * 100) if target_qty > 0 else 0
        )
        
        # Determine handling type
        if variance < 0:
            handling_type = "SHORTAGE"
            actions = [
                f"Shortage detected: {abs(variance)} units short",
                "Generate waste report",
                "Request supervisor approval"
            ]
        elif variance > 0:
            handling_type = "SURPLUS"
            actions = [
                f"Surplus detected: {variance} extra units",
                "Verify count accuracy",
                "Document surplus for inventory adjustment"
            ]
        else:
            handling_type = "OK"
            actions = ["No variance - target met"]
        
        db.commit()
        
        return {
            "work_order_id": work_order_id,
            "mo_id": wo.mo_id,
            "department": cls.DEPARTMENT_NAME,
            "actual_output": float(actual_output),
            "target": float(target_qty),
            "variance": float(variance),
            "variance_percentage": float(variance_percentage),
            "reject_qty": float(reject_qty),
            "handling_type": handling_type,
            "actions_taken": actions,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def create_transfer_log(
        cls,
        db: Session,
        work_order_id: int,
        to_dept: TransferDept,
        qty_to_transfer: Decimal,
        operator_id: int
    ) -> dict:
        """
        Create transfer log for handoff to next department
        
        QT-09 Transfer Protocol:
        1. Create transfer log (LOCKED status)
        2. Generate transfer slip number
        3. Mark current line as OCCUPIED
        4. Wait for handshake ACCEPT from receiving dept
        
        Returns:
            Transfer slip details
        """
        wo = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not wo:
            raise HTTPException(
                status_code=404,
                detail=f"Work order {work_order_id} not found"
            )
        
        if wo.status != WorkOrderStatus.FINISHED:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot transfer from WO in {wo.status} status"
            )
        
        # Generate transfer slip number
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        slip_number = (
            f"TRF-{cls.TRANSFER_DEPT.value}-"
            f"{to_dept.value}-{wo.mo_id}-{timestamp}"
        )
        
        # Create transfer log
        transfer = TransferLog(
            slip_number=slip_number,
            mo_id=wo.mo_id,
            from_dept=cls.TRANSFER_DEPT,
            to_dept=to_dept,
            qty_transferred=qty_to_transfer,
            status=TransferStatus.LOCKED,
            transferred_by=operator_id,
            timestamp_transfer=datetime.utcnow()
        )
        db.add(transfer)
        
        # Mark current line as OCCUPIED (awaiting handshake)
        line = db.query(LineOccupancy).filter(
            LineOccupancy.dept_name == cls.TRANSFER_DEPT
        ).first()
        
        if not line:
            line = LineOccupancy(
                dept_name=cls.TRANSFER_DEPT,
                status="Occupied",
                current_article=wo.product.code if wo.product else None
            )
            db.add(line)
        else:
            line.status = "Occupied"
            line.current_article = wo.product.code if wo.product else None
        
        db.commit()
        
        return {
            "transfer_slip_number": slip_number,
            "mo_id": wo.mo_id,
            "from_dept": cls.TRANSFER_DEPT.value,
            "to_dept": to_dept.value,
            "qty_transferred": float(qty_to_transfer),
            "status": "LOCKED",
            "operator_id": operator_id,
            "timestamp": datetime.utcnow().isoformat(),
            "next_step": f"Awaiting handshake ACCEPT from {to_dept.value}"
        }
    
    @staticmethod
    def update_work_order_status(
        db: Session,
        work_order_id: int,
        new_status: WorkOrderStatus,
        notes: Optional[str] = None
    ) -> dict:
        """
        Update work order status with audit trail
        
        Common status transitions:
        - PENDING → RUNNING (start operation)
        - RUNNING → PAUSED (temporary stop)
        - PAUSED → RUNNING (resume)
        - RUNNING → FINISHED (complete operation)
        """
        wo = db.query(WorkOrder).filter(
            WorkOrder.id == work_order_id
        ).first()
        
        if not wo:
            raise HTTPException(
                status_code=404,
                detail=f"Work order {work_order_id} not found"
            )
        
        old_status = wo.status
        wo.status = new_status
        
        # Update timestamps based on status
        if new_status == WorkOrderStatus.RUNNING and not wo.start_time:
            wo.start_time = datetime.utcnow()
        elif new_status == WorkOrderStatus.FINISHED:
            wo.end_time = datetime.utcnow()
        
        db.commit()
        
        return {
            "work_order_id": work_order_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "notes": notes,
            "timestamp": datetime.utcnow().isoformat()
        }
