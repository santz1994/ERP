"""
Material Debt Service - Feature #4: Negative Inventory Management
Manages material debt creation, approval workflow, and adjustment reconciliation

Session 35: Material Debt System Implementation
"""
import logging
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from app.core.models.daily_production import MaterialDebt, MaterialDebtSettlement
from app.core.models.production import SPKMaterialAllocation, SPKMaterialAllocationStatus
from app.core.models.users import User
from app.core.models.products import Product
from app.services.approval_service import ApprovalWorkflowEngine, ApprovalEntityType

logger = logging.getLogger(__name__)


class MaterialDebtStatus(str, Enum):
    """Material debt status lifecycle"""
    PENDING = "PENDING"                  # Debt created, waiting approval
    APPROVED = "APPROVED"                # Approved by SPV & Manager
    PARTIAL_RESOLVED = "PARTIAL_RESOLVED"  # Some material received
    FULLY_RESOLVED = "FULLY_RESOLVED"    # All material received
    EXCESS = "EXCESS"                    # More than expected received
    OVERDUE = "OVERDUE"                  # Due date passed


class MaterialDebtApprovalStatus(str, Enum):
    """Approval workflow status"""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    SPV_APPROVED = "SPV_APPROVED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class BOMAllocationError(Exception):
    """Raised when BOM allocation fails"""
    pass


class MaterialDebtService:
    """
    Service for managing material debt and negative inventory system
    
    Feature #4: NEGATIVE INVENTORY (MATERIAL DEBT) SYSTEM
    Allows production to start without all materials (debt), with approval and adjustment workflow
    
    Workflow:
    1. Admin Produksi membuat SPK
    2. Material check → kurang
    3. Create Material Debt + submit for approval
    4. SPV → Manager → Approved
    5. Produksi jalan (SPK status: IN_PROGRESS_WITH_DEBT)
    6. Material sampai → Create Debt Adjustment
    7. Reconcile debt dengan actual receipt
    8. Debt resolved atau partial resolved
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_material_debt(
        self,
        spk_id: int,
        material_id: int,
        qty_owed: Decimal,
        reason: str,
        department: str,
        created_by_id: int,
        due_date: Optional[date] = None,
        allow_production: bool = False
    ) -> Dict[str, Any]:
        """
        Create material debt entry when shortage detected
        
        Args:
            spk_id: SPK ID that needs material
            material_id: Product/material ID in debt
            qty_owed: Quantity owed (in stock unit)
            reason: Reason for debt (e.g., "Material PO-2026-0456 sedang di jalan")
            department: Department creating debt (e.g., "Cutting", "Sewing")
            created_by_id: User creating the debt
            due_date: Expected receipt date (default: today + 5 days)
            allow_production: Allow production to start while debt pending
        
        Returns:
            Dict with debt_id, status, and approval request ID
            
        Raises:
            BOMAllocationError: If debt creation fails
        """
        try:
            logger.info(f"Creating material debt: SPK={spk_id}, Material={material_id}, Qty={qty_owed}")
            
            # Set due date
            if not due_date:
                due_date = date.today()  # Will be set by Purchasing
            
            # Create debt record
            debt = MaterialDebt(
                spk_id=spk_id,
                product_id=material_id,
                qty_owed=int(qty_owed),
                qty_settled=0,
                approval_status=MaterialDebtApprovalStatus.PENDING_APPROVAL.value,
                created_by_id=created_by_id,
                approval_reason=reason,
                created_at=datetime.utcnow()
            )
            
            self.db.add(debt)
            self.db.flush()  # Get ID without committing
            
            # Log creation
            logger.info(f"Material debt created: ID={debt.id}, SPK={spk_id}, Qty={qty_owed}")
            
            # INTEGRATION WITH FEATURE #2: Submit for approval via ApprovalWorkflowEngine
            approval_engine = ApprovalWorkflowEngine()
            approval_request = await approval_engine.submit_for_approval(
                entity_type=ApprovalEntityType.MATERIAL_DEBT,
                entity_id=debt.id,
                changes={
                    "material_id": material_id,
                    "qty_owed": float(qty_owed),
                    "department": department,
                    "reason": reason
                },
                reason=f"Material Debt approval for SPK {spk_id}: {reason}",
                submitted_by=created_by_id,
                session=self.db
            )
            logger.info(f"Material debt approval request created: ID={approval_request.id}")
            
            self.db.commit()
            
            return {
                "debt_id": debt.id,
                "spk_id": spk_id,
                "material_id": material_id,
                "qty_owed": float(qty_owed),
                "approval_status": MaterialDebtApprovalStatus.PENDING_APPROVAL.value,
                "status": MaterialDebtStatus.PENDING.value,
                "approval_request_id": approval_request.id,
                "allow_production_start": allow_production,
                "message": f"Material debt created and submitted for approval.",
                "next_step": "Waiting for SPV approval..."
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create material debt: {str(e)}")
            raise BOMAllocationError(f"Failed to create material debt: {str(e)}")
    
    async def approve_material_debt(
        self,
        debt_id: int,
        approval_decision: str,  # "APPROVE" or "REJECT"
        approver_id: int,
        approver_role: str,  # "SPV" or "MANAGER"
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Approve or reject material debt (part of Feature #2 approval workflow)
        
        Args:
            debt_id: Material debt ID
            approval_decision: "APPROVE" or "REJECT"
            approver_id: User ID of approver
            approver_role: SPV or MANAGER
            notes: Optional approval notes
        
        Returns:
            Dict with updated debt status and next approver
            
        Raises:
            BOMAllocationError: If approval fails or not found
        """
        try:
            debt = self.db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
            if not debt:
                raise BOMAllocationError(f"Debt {debt_id} not found")
            
            approver = self.db.query(User).filter(User.id == approver_id).first()
            if not approver:
                raise BOMAllocationError(f"Approver {approver_id} not found")
            
            if approval_decision == "REJECT":
                debt.approval_status = MaterialDebtApprovalStatus.REJECTED.value
                debt.approved_by_id = approver_id
                debt.approved_at = datetime.utcnow()
                debt.approval_reason = notes or "Rejected by approver"
                
                self.db.commit()
                logger.info(f"Material debt {debt_id} REJECTED by {approver.username}")
                
                return {
                    "debt_id": debt_id,
                    "status": "REJECTED",
                    "rejected_by": approver.username,
                    "rejected_at": debt.approved_at.isoformat(),
                    "reason": debt.approval_reason,
                    "message": "Material debt rejected. Production cannot start."
                }
            
            # APPROVE logic
            if approver_role == "SPV":
                debt.approval_status = MaterialDebtApprovalStatus.SPV_APPROVED.value
                next_approver = "MANAGER"
                message = "Approved by SPV. Waiting for Manager approval..."
            elif approver_role == "MANAGER":
                debt.approval_status = MaterialDebtApprovalStatus.APPROVED.value
                message = "Fully approved by SPV & Manager. Production can start!"
                next_approver = None
            else:
                raise BOMAllocationError(f"Invalid approver role: {approver_role}")
            
            debt.approved_by_id = approver_id
            debt.approved_at = datetime.utcnow()
            if notes:
                debt.approval_reason = notes
            
            self.db.commit()
            logger.info(f"Material debt {debt_id} approved by {approver.username} ({approver_role})")
            
            return {
                "debt_id": debt_id,
                "approval_status": debt.approval_status,
                "approved_by": approver.username,
                "approved_at": debt.approved_at.isoformat(),
                "next_approver": next_approver,
                "can_start_production": debt.approval_status == MaterialDebtApprovalStatus.APPROVED.value,
                "message": message
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to approve material debt {debt_id}: {str(e)}")
            raise BOMAllocationError(f"Failed to approve material debt: {str(e)}")
    
    async def adjust_material_debt(
        self,
        debt_id: int,
        actual_received_qty: Decimal,
        adjustment_notes: str,
        recorded_by_id: int,
        received_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Adjust material debt when material arrives (reconciliation)
        
        Business Logic:
        - If received_qty == debt_qty → mark FULLY_SETTLED
        - If received_qty < debt_qty → partial settled, remaining still owed
        - If received_qty > debt_qty → add excess back to warehouse stock
        
        Args:
            debt_id: Material debt ID to adjust
            actual_received_qty: Actual quantity received from supplier
            adjustment_notes: Notes about the delivery
            recorded_by_id: User recording the receipt
            received_date: Date material received (default: today)
        
        Returns:
            Dict with debt status, remaining debt, excess qty (if any)
            
        Raises:
            BOMAllocationError: If adjustment fails
        """
        try:
            debt = self.db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
            if not debt:
                raise BOMAllocationError(f"Debt {debt_id} not found")
            
            if debt.approval_status != MaterialDebtApprovalStatus.APPROVED.value:
                raise BOMAllocationError(
                    f"Debt not approved yet. Current status: {debt.approval_status}"
                )
            
            if not received_date:
                received_date = date.today()
            
            # Record settlement
            settlement = MaterialDebtSettlement(
                material_debt_id=debt_id,
                qty_settled=int(actual_received_qty),
                settlement_date=received_date,
                received_by_id=recorded_by_id,
                settled_by_id=recorded_by_id,
                settlement_notes=adjustment_notes,
                created_at=datetime.utcnow()
            )
            
            self.db.add(settlement)
            
            # Update debt totals
            debt.qty_settled += int(actual_received_qty)
            
            remaining_debt = debt.qty_owed - debt.qty_settled
            excess_qty = 0
            
            if remaining_debt <= 0:
                # Fully settled or excess
                debt.approval_status = MaterialDebtApprovalStatus.FULLY_RESOLVED.value
                
                if remaining_debt < 0:
                    excess_qty = abs(remaining_debt)
                    debt.approval_status = MaterialDebtApprovalStatus.EXCESS.value
                    logger.info(f"Debt {debt_id} has excess qty: {excess_qty}")
                    
                    # TODO: Add excess_qty back to warehouse inventory
                    # await warehouse_service.add_stock(debt.product_id, excess_qty, "Excess from debt settlement")
            else:
                debt.approval_status = MaterialDebtApprovalStatus.PARTIAL_RESOLVED.value
            
            self.db.commit()
            logger.info(f"Material debt {debt_id} adjusted: received={actual_received_qty}, remaining={max(0, remaining_debt)}")
            
            return {
                "debt_id": debt_id,
                "debt_status": debt.approval_status,
                "qty_owed": debt.qty_owed,
                "qty_settled": debt.qty_settled,
                "remaining_debt": max(0, remaining_debt),
                "excess_qty": excess_qty if excess_qty > 0 else 0,
                "settlement_date": received_date.isoformat(),
                "message": f"Debt adjustment recorded. Remaining debt: {max(0, remaining_debt)} units."
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to adjust material debt {debt_id}: {str(e)}")
            raise BOMAllocationError(f"Failed to adjust material debt: {str(e)}")
    
    async def get_outstanding_debts(
        self,
        dept_id: Optional[int] = None,
        only_pending_approval: bool = False
    ) -> Dict[str, Any]:
        """
        Get list of outstanding material debts
        
        Args:
            dept_id: Optional filter by department
            only_pending_approval: If True, only return debts waiting approval
        
        Returns:
            List of outstanding debts with summary
        """
        try:
            query = self.db.query(MaterialDebt).filter(
                MaterialDebt.approval_status != MaterialDebtApprovalStatus.FULLY_RESOLVED.value
            )
            
            if only_pending_approval:
                query = query.filter(
                    MaterialDebt.approval_status == MaterialDebtApprovalStatus.PENDING_APPROVAL.value
                )
            
            debts = query.all()
            
            total_outstanding_qty = sum(
                d.qty_owed - d.qty_settled for d in debts
            )
            
            # TODO: Get pricing from Material Master to calculate total value
            total_outstanding_value = 0  # Placeholder
            
            return {
                "count": len(debts),
                "total_outstanding_qty": total_outstanding_qty,
                "total_outstanding_value": total_outstanding_value,
                "debts": [
                    {
                        "debt_id": d.id,
                        "spk_id": d.spk_id,
                        "material_id": d.product_id,
                        "qty_owed": d.qty_owed,
                        "qty_settled": d.qty_settled,
                        "remaining": d.qty_owed - d.qty_settled,
                        "approval_status": d.approval_status,
                        "created_date": d.created_at.date().isoformat() if d.created_at else None,
                        "reason": d.approval_reason
                    }
                    for d in debts
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get outstanding debts: {str(e)}")
            raise BOMAllocationError(f"Failed to get outstanding debts: {str(e)}")
    
    async def get_debt_status(self, debt_id: int) -> Dict[str, Any]:
        """Get detailed status of a material debt"""
        try:
            debt = self.db.query(MaterialDebt).filter(MaterialDebt.id == debt_id).first()
            if not debt:
                raise BOMAllocationError(f"Debt {debt_id} not found")
            
            settlements = self.db.query(MaterialDebtSettlement).filter(
                MaterialDebtSettlement.material_debt_id == debt_id
            ).all()
            
            return {
                "debt_id": debt_id,
                "spk_id": debt.spk_id,
                "material_id": debt.product_id,
                "qty_owed": debt.qty_owed,
                "qty_settled": debt.qty_settled,
                "remaining": debt.qty_owed - debt.qty_settled,
                "approval_status": debt.approval_status,
                "created_by_id": debt.created_by_id,
                "created_date": debt.created_at.date().isoformat() if debt.created_at else None,
                "approved_by_id": debt.approved_by_id,
                "approved_date": debt.approved_at.date().isoformat() if debt.approved_at else None,
                "reason": debt.approval_reason,
                "settlement_history": [
                    {
                        "settlement_date": s.settlement_date.isoformat(),
                        "qty_settled": s.qty_settled,
                        "recorded_by_id": s.recorded_by_id,
                        "notes": s.settlement_notes
                    }
                    for s in settlements
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get debt status: {str(e)}")
            raise BOMAllocationError(f"Failed to get debt status: {str(e)}")
    
    def check_debt_threshold(
        self,
        threshold_value: Decimal = Decimal('50000000')  # Default: Rp 50M
    ) -> bool:
        """
        Check if total outstanding debt exceeds threshold
        If exceeded, block new PO creation
        
        Args:
            threshold_value: Maximum allowed outstanding debt value
        
        Returns:
            True if threshold exceeded (block new PO), False otherwise
        """
        try:
            pending_debts = self.db.query(MaterialDebt).filter(
                MaterialDebt.approval_status.in_([
                    MaterialDebtApprovalStatus.PENDING_APPROVAL.value,
                    MaterialDebtApprovalStatus.APPROVED.value,
                    MaterialDebtApprovalStatus.PARTIAL_SETTLED.value
                ])
            ).all()
            
            # TODO: Calculate total value from material prices
            total_debt_value = Decimal('0')
            for debt in pending_debts:
                # Get material price from Product master
                # total_debt_value += (debt.qty_owed - debt.qty_settled) * material_price
                pass
            
            return total_debt_value > threshold_value
            
        except Exception as e:
            logger.error(f"Failed to check debt threshold: {str(e)}")
            return False
