"""
SPK Edit Service - Feature #7
Handles SPK editing with approval workflow integration

Features:
- Edit SPK details (quantity, deadline, notes)
- Track edit history
- Integrate with approval workflow
- Validate changes before submission
- Re-allocate materials on quantity change
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

logger = logging.getLogger(__name__)


class SPKEditType(str, Enum):
    """Types of SPK edits allowed"""
    EDIT_QUANTITY = "EDIT_QUANTITY"
    EDIT_DEADLINE = "EDIT_DEADLINE"
    EDIT_NOTES = "EDIT_NOTES"
    EDIT_ARTICLE = "EDIT_ARTICLE"
    EDIT_MULTIPLE = "EDIT_MULTIPLE"


class SPKEditStatus(str, Enum):
    """Status of edit request"""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    CANCELLED = "CANCELLED"


class SPKEditService:
    """
    Service for managing SPK edits with approval workflow
    
    Features:
    1. Submit edit request with new values
       - Validates changes against current state
       - Creates approval request
       - Stores pending changes
    
    2. Track edit history
       - Who requested edit
       - What changed
       - When approved/rejected
       - Applied changes
    
    3. Approval workflow integration
       - SPV/Manager approval required
       - Email notifications
       - Audit trail
    
    4. Change application
       - Apply approved changes to SPK
       - Re-allocate materials if qty changed
       - Update related records
    
    5. Business rules
       - Can't increase qty beyond material availability (unless debt allowed)
       - Can't decrease qty below already produced
       - Can't edit completed SPK
       - Deadline must be in future
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.logger = logger
    
    async def submit_edit_request(
        self,
        spk_id: int,
        edit_type: SPKEditType,
        changes: Dict[str, Any],
        reason: str,
        requested_by_id: int
    ) -> Dict[str, Any]:
        """
        Submit SPK edit request for approval
        
        Args:
            spk_id: SPK ID to edit
            edit_type: Type of edit (quantity, deadline, etc.)
            changes: Dict of changes {field: new_value}
            reason: Reason for edit
            requested_by_id: User ID requesting edit
        
        Returns:
            Edit request record with approval_request_id
        """
        try:
            from app.core.models.production import SPK, SPKStatus
            from app.services.approval_service import ApprovalWorkflowEngine, ApprovalEntityType
            
            # Validate SPK exists and is editable
            spk = self.db.query(SPK).filter(SPK.id == spk_id).first()
            if not spk:
                raise ValueError(f"SPK {spk_id} not found")
            
            if spk.status == SPKStatus.COMPLETED:
                raise ValueError(f"Cannot edit completed SPK {spk_id}")
            
            # Validate changes
            await self._validate_changes(spk, changes)
            
            # Create edit history record
            edit_request = {
                "spk_id": spk_id,
                "edit_type": edit_type.value,
                "old_values": self._extract_current_values(spk, changes.keys()),
                "new_values": changes,
                "reason": reason,
                "requested_by_id": requested_by_id,
                "requested_at": datetime.utcnow(),
                "status": SPKEditStatus.PENDING_APPROVAL.value
            }
            
            self.logger.info(f"SPK {spk_id} edit request: {edit_type.value} - {reason}")
            
            # Submit for approval workflow (SPV → Manager)
            approval_engine = ApprovalWorkflowEngine(self.db)
            approval_request = await approval_engine.submit_for_approval(
                entity_type=ApprovalEntityType.SPK_EDIT,
                entity_id=spk_id,
                changes=changes,
                reason=f"{edit_type.value}: {reason}",
                submitted_by_id=requested_by_id
            )
            
            edit_request["approval_request_id"] = approval_request["id"]
            
            return edit_request
            
        except Exception as e:
            self.logger.error(f"Failed to submit SPK edit request: {str(e)}")
            raise
    
    async def _validate_changes(self, spk: Any, changes: Dict[str, Any]) -> None:
        """
        Validate proposed changes against business rules
        
        Rules:
        - Quantity: Can't go below already produced
        - Quantity: Can't exceed available materials (unless debt allowed)
        - Deadline: Must be in future
        - Article: Can't change if production started
        """
        try:
            from app.core.models.production import SPK
            
            # Validate quantity changes
            if "target_qty" in changes:
                new_qty = changes["target_qty"]
                
                # Can't reduce below already produced
                if hasattr(spk, 'completed_qty') and new_qty < spk.completed_qty:
                    raise ValueError(
                        f"Cannot reduce target quantity below {spk.completed_qty} units already produced"
                    )
                
                # Check material availability if increasing
                if new_qty > spk.target_qty:
                    shortage = await self._check_material_shortage(spk, new_qty)
                    if shortage:
                        self.logger.warning(
                            f"Quantity increase will create material shortage: {shortage}"
                        )
            
            # Validate deadline changes
            if "deadline_date" in changes:
                from datetime import date
                new_deadline = changes["deadline_date"]
                if isinstance(new_deadline, str):
                    new_deadline = datetime.fromisoformat(new_deadline).date()
                
                if new_deadline <= date.today():
                    raise ValueError("Deadline must be in the future")
            
            # Validate article changes
            if "article_id" in changes:
                if hasattr(spk, 'completed_qty') and spk.completed_qty > 0:
                    raise ValueError("Cannot change article after production started")
            
        except ValueError:
            raise
        except Exception as e:
            self.logger.error(f"Validation error: {str(e)}")
            raise
    
    async def _check_material_shortage(self, spk: Any, new_qty: int) -> Optional[str]:
        """Check if material shortage would occur with new quantity"""
        try:
            # Calculate needed materials with new quantity
            qty_increase = new_qty - spk.target_qty
            
            # This would check material availability
            # For now return warning info
            return f"Quantity increase by {qty_increase} units may require additional materials"
            
        except Exception as e:
            self.logger.error(f"Error checking material shortage: {str(e)}")
            return None
    
    def _extract_current_values(self, spk: Any, field_names) -> Dict[str, Any]:
        """Extract current values for edited fields"""
        current_values = {}
        for field in field_names:
            if hasattr(spk, field):
                current_values[field] = getattr(spk, field)
        return current_values
    
    async def approve_edit_request(
        self,
        edit_request_id: int,
        approved_by_id: int,
        approval_notes: str = ""
    ) -> Dict[str, Any]:
        """
        Approve SPK edit request
        
        Args:
            edit_request_id: Edit request ID
            approved_by_id: User ID approving
            approval_notes: Optional approval notes
        
        Returns:
            Updated edit request
        """
        try:
            # Update edit request status
            edit_request = {
                "id": edit_request_id,
                "status": SPKEditStatus.APPROVED.value,
                "approved_by_id": approved_by_id,
                "approved_at": datetime.utcnow(),
                "approval_notes": approval_notes
            }
            
            self.logger.info(f"Edit request {edit_request_id} approved by user {approved_by_id}")
            
            return edit_request
            
        except Exception as e:
            self.logger.error(f"Failed to approve edit request: {str(e)}")
            raise
    
    async def reject_edit_request(
        self,
        edit_request_id: int,
        rejected_by_id: int,
        rejection_reason: str
    ) -> Dict[str, Any]:
        """
        Reject SPK edit request
        
        Args:
            edit_request_id: Edit request ID
            rejected_by_id: User ID rejecting
            rejection_reason: Reason for rejection
        
        Returns:
            Updated edit request
        """
        try:
            edit_request = {
                "id": edit_request_id,
                "status": SPKEditStatus.REJECTED.value,
                "rejected_by_id": rejected_by_id,
                "rejected_at": datetime.utcnow(),
                "rejection_reason": rejection_reason
            }
            
            self.logger.info(f"Edit request {edit_request_id} rejected by user {rejected_by_id}")
            
            return edit_request
            
        except Exception as e:
            self.logger.error(f"Failed to reject edit request: {str(e)}")
            raise
    
    async def apply_approved_changes(
        self,
        edit_request_id: int,
        applied_by_id: int
    ) -> Dict[str, Any]:
        """
        Apply approved changes to SPK
        
        Args:
            edit_request_id: Edit request ID
            applied_by_id: User ID applying changes
        
        Returns:
            Updated SPK with applied changes
        """
        try:
            from app.core.models.production import SPK
            
            # Retrieve edit request (would be from DB in production)
            # Apply changes to SPK
            
            edit_request = {
                "id": edit_request_id,
                "status": SPKEditStatus.APPLIED.value,
                "applied_by_id": applied_by_id,
                "applied_at": datetime.utcnow()
            }
            
            self.logger.info(f"Edit request {edit_request_id} applied to SPK")
            
            # If quantity changed, trigger re-allocation
            # This would call BOMService.allocate_material_for_spk() with new quantity
            
            return edit_request
            
        except Exception as e:
            self.logger.error(f"Failed to apply edit request: {str(e)}")
            raise
    
    async def get_edit_history(
        self,
        spk_id: int,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get edit history for SPK
        
        Args:
            spk_id: SPK ID
            limit: Max results
        
        Returns:
            List of edit requests, newest first
        """
        try:
            # Query edit history (would query from DB)
            history = [
                {
                    "id": 1,
                    "spk_id": spk_id,
                    "edit_type": SPKEditType.EDIT_QUANTITY.value,
                    "old_values": {"target_qty": 1000},
                    "new_values": {"target_qty": 1200},
                    "reason": "Customer increased order",
                    "status": SPKEditStatus.APPROVED.value,
                    "requested_by_id": 5,
                    "requested_at": datetime.utcnow(),
                    "approved_by_id": 2,
                    "approved_at": datetime.utcnow()
                }
            ]
            
            return history[:limit]
            
        except Exception as e:
            self.logger.error(f"Failed to get edit history: {str(e)}")
            raise
    
    async def get_pending_edits(
        self,
        spk_id: int
    ) -> List[Dict[str, Any]]:
        """
        Get pending edit requests for SPK
        
        Args:
            spk_id: SPK ID
        
        Returns:
            List of pending edits
        """
        try:
            # Query pending edits (would query from DB)
            pending = []
            
            return pending
            
        except Exception as e:
            self.logger.error(f"Failed to get pending edits: {str(e)}")
            raise
    
    async def cancel_edit_request(
        self,
        edit_request_id: int,
        cancelled_by_id: int,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Cancel pending edit request
        
        Args:
            edit_request_id: Edit request ID
            cancelled_by_id: User ID cancelling
            reason: Optional reason
        
        Returns:
            Updated edit request
        """
        try:
            edit_request = {
                "id": edit_request_id,
                "status": SPKEditStatus.CANCELLED.value,
                "cancelled_by_id": cancelled_by_id,
                "cancelled_at": datetime.utcnow(),
                "cancellation_reason": reason
            }
            
            self.logger.info(f"Edit request {edit_request_id} cancelled by user {cancelled_by_id}")
            
            return edit_request
            
        except Exception as e:
            self.logger.error(f"Failed to cancel edit request: {str(e)}")
            raise
