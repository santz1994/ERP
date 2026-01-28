"""
Approval Workflow Engine - Multi-level approval system (SPV → Manager → Director)

Features:
- Submit entity for approval
- Sequential approval steps
- Director view-only notification
- Automatic transition between levels
- Rejection & revert logic
- Audit trail for all actions

Entity Types Supported:
- SPK_CREATE
- SPK_EDIT_QUANTITY
- SPK_EDIT_DEADLINE
- MO_EDIT
- MATERIAL_DEBT
- STOCK_ADJUSTMENT
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from enum import Enum
import json
import logging

from app.core.models.manufacturing import SPK, ManufacturingOrder
from app.core.models.audit import AuditLog

logger = logging.getLogger(__name__)


class ApprovalEntityType(str, Enum):
    """Entity types that require approval"""
    SPK_CREATE = "SPK_CREATE"
    SPK_EDIT_QUANTITY = "SPK_EDIT_QUANTITY"
    SPK_EDIT_DEADLINE = "SPK_EDIT_DEADLINE"
    MO_EDIT = "MO_EDIT"
    MATERIAL_DEBT = "MATERIAL_DEBT"
    STOCK_ADJUSTMENT = "STOCK_ADJUSTMENT"


class ApprovalStatus(str, Enum):
    """Approval request status"""
    PENDING = "PENDING"
    SPV_APPROVED = "SPV_APPROVED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    REVERTED = "REVERTED"


class ApprovalStep(str, Enum):
    """Approval step levels"""
    SPV = "SPV"
    MANAGER = "MANAGER"
    DIRECTOR = "DIRECTOR"


# Approval chain definition per entity type
APPROVAL_CHAINS: Dict[ApprovalEntityType, List[ApprovalStep]] = {
    ApprovalEntityType.SPK_CREATE: [ApprovalStep.SPV, ApprovalStep.MANAGER],
    ApprovalEntityType.SPK_EDIT_QUANTITY: [ApprovalStep.SPV, ApprovalStep.MANAGER],
    ApprovalEntityType.SPK_EDIT_DEADLINE: [ApprovalStep.SPV, ApprovalStep.MANAGER],
    ApprovalEntityType.MO_EDIT: [ApprovalStep.MANAGER],
    ApprovalEntityType.MATERIAL_DEBT: [ApprovalStep.SPV, ApprovalStep.MANAGER],
    ApprovalEntityType.STOCK_ADJUSTMENT: [ApprovalStep.MANAGER],
}


class ApprovalWorkflowEngine:
    """
    Manages multi-level approval workflows
    
    Example:
    ```python
    engine = ApprovalWorkflowEngine()
    
    # Submit for approval
    approval_req = await engine.submit_for_approval(
        entity_type="SPK_EDIT_QUANTITY",
        entity_id=spk_id,
        changes={"quantity": 500},
        reason="Production increased due to customer request",
        submitted_by=user_id,
        session=session
    )
    
    # Approve
    await engine.approve(
        approval_request_id=approval_req.id,
        approver_id=spv_user_id,
        notes="Looks good",
        session=session
    )
    
    # Get pending approvals
    pending = await engine.get_pending_approvals(user_id, session)
    ```
    """

    async def submit_for_approval(
        self,
        entity_type: ApprovalEntityType,
        entity_id: UUID,
        changes: Dict[str, Any],
        reason: str,
        submitted_by: UUID,
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Submit entity for approval
        
        Returns: {
            'approval_request_id': UUID,
            'status': 'PENDING',
            'approval_chain': [ApprovalStep, ...],
            'current_step': int,
            'next_approver': str  # Role name
        }
        """
        try:
            # Get approval chain
            approval_chain = APPROVAL_CHAINS.get(entity_type)
            if not approval_chain:
                raise ValueError(f"Unknown entity type: {entity_type}")

            # Create approval request
            approval_request_id = str(UUID)
            current_step = 0

            # Store in database
            query = """
            INSERT INTO approval_requests (
                id, entity_type, entity_id, submitted_by, 
                changes, reason, status, current_step, 
                approval_chain, created_at
            ) VALUES (
                :id, :entity_type, :entity_id, :submitted_by,
                :changes, :reason, :status, :current_step,
                :approval_chain, :created_at
            )
            """
            
            await session.execute(
                query,
                {
                    "id": approval_request_id,
                    "entity_type": entity_type.value,
                    "entity_id": str(entity_id),
                    "submitted_by": str(submitted_by),
                    "changes": json.dumps(changes),
                    "reason": reason,
                    "status": ApprovalStatus.PENDING.value,
                    "current_step": current_step,
                    "approval_chain": json.dumps([s.value for s in approval_chain]),
                    "created_at": datetime.now(),
                }
            )

            await session.commit()

            # Log audit trail
            await self._log_audit(
                action="APPROVAL_SUBMITTED",
                entity_type=entity_type.value,
                entity_id=str(entity_id),
                changes=changes,
                user_id=str(submitted_by),
                session=session
            )

            # Notify first approver (SPV)
            next_approver_role = approval_chain[current_step].value
            await self._notify_approver(
                approval_request_id=str(approval_request_id),
                approver_role=next_approver_role,
                entity_type=entity_type.value,
                entity_id=str(entity_id),
                reason=reason,
                session=session
            )

            logger.info(
                f"Approval submitted: {entity_type.value} {entity_id} → {next_approver_role}"
            )

            return {
                "approval_request_id": str(approval_request_id),
                "status": ApprovalStatus.PENDING.value,
                "approval_chain": [s.value for s in approval_chain],
                "current_step": current_step,
                "next_approver": next_approver_role,
            }

        except Exception as e:
            logger.error(f"Error submitting approval: {str(e)}")
            raise

    async def approve(
        self,
        approval_request_id: UUID,
        approver_id: UUID,
        notes: str = "",
        session: AsyncSession = None,
    ) -> Dict[str, Any]:
        """
        Approve current step and move to next
        
        Returns: {
            'status': 'SPV_APPROVED' | 'MANAGER_APPROVED' | 'APPROVED',
            'current_step': int,
            'next_approver': str | None,
            'is_final_approval': bool
        }
        """
        try:
            # Get approval request
            approval_req = await self._get_approval_request(
                str(approval_request_id), session
            )
            
            if not approval_req:
                raise ValueError(f"Approval request not found: {approval_request_id}")

            # Verify approver has right role for this step
            current_chain = approval_req["approval_chain"]
            current_step = approval_req["current_step"]
            current_approver_role = current_chain[current_step]
            
            approver_role = await self._get_user_role(str(approver_id), session)
            if approver_role != current_approver_role:
                raise ValueError(
                    f"Approver {approver_id} has role {approver_role}, "
                    f"but {current_approver_role} approval needed"
                )

            # Record approval
            approval_step = {
                "step": current_approver_role,
                "approved_by": str(approver_id),
                "approved_at": datetime.now().isoformat(),
                "notes": notes,
            }

            # Update approval request
            query = """
            UPDATE approval_requests SET
                approvals = approvals || :new_approval,
                current_step = current_step + 1
            WHERE id = :id
            """

            await session.execute(
                query,
                {
                    "id": str(approval_request_id),
                    "new_approval": json.dumps(approval_step),
                }
            )

            # Check if final approval
            is_final = (current_step + 1) >= len(current_chain)
            new_status = ApprovalStatus.APPROVED.value if is_final else f"{current_approver_role}_APPROVED"

            # Update status
            query_status = f"""
            UPDATE approval_requests SET status = :status WHERE id = :id
            """
            await session.execute(
                query_status,
                {"id": str(approval_request_id), "status": new_status}
            )

            await session.commit()

            # Log audit
            await self._log_audit(
                action="APPROVAL_APPROVED",
                entity_type=approval_req["entity_type"],
                entity_id=approval_req["entity_id"],
                changes={"approver": str(approver_id), "step": current_approver_role},
                user_id=str(approver_id),
                session=session
            )

            # Notify next approver (or Director for view-only)
            if not is_final:
                next_approver_role = current_chain[current_step + 1]
                await self._notify_approver(
                    approval_request_id=str(approval_request_id),
                    approver_role=next_approver_role,
                    entity_type=approval_req["entity_type"],
                    entity_id=approval_req["entity_id"],
                    session=session
                )
            else:
                # Notify Director (view-only)
                await self._notify_director(
                    approval_request_id=str(approval_request_id),
                    entity_type=approval_req["entity_type"],
                    entity_id=approval_req["entity_id"],
                    session=session
                )

            logger.info(
                f"Approval step {current_approver_role} approved by {approver_id}"
            )

            return {
                "status": new_status,
                "current_step": current_step + 1,
                "next_approver": current_chain[current_step + 1] if not is_final else None,
                "is_final_approval": is_final,
            }

        except Exception as e:
            logger.error(f"Error approving: {str(e)}")
            raise

    async def reject(
        self,
        approval_request_id: UUID,
        rejector_id: UUID,
        reason: str,
        session: AsyncSession,
    ) -> Dict[str, Any]:
        """
        Reject approval request and revert to PENDING
        
        Returns: {'status': 'REJECTED', 'reason': str}
        """
        try:
            # Get approval request
            approval_req = await self._get_approval_request(
                str(approval_request_id), session
            )

            # Update status
            query = """
            UPDATE approval_requests SET
                status = :status,
                rejection_reason = :reason,
                rejected_by = :rejected_by,
                rejected_at = :rejected_at
            WHERE id = :id
            """

            await session.execute(
                query,
                {
                    "id": str(approval_request_id),
                    "status": ApprovalStatus.REJECTED.value,
                    "reason": reason,
                    "rejected_by": str(rejector_id),
                    "rejected_at": datetime.now(),
                }
            )

            await session.commit()

            # Log audit
            await self._log_audit(
                action="APPROVAL_REJECTED",
                entity_type=approval_req["entity_type"],
                entity_id=approval_req["entity_id"],
                changes={"rejection_reason": reason},
                user_id=str(rejector_id),
                session=session
            )

            # Notify submitter
            await self._notify_submitter_rejected(
                approval_request_id=str(approval_request_id),
                rejection_reason=reason,
                session=session
            )

            logger.info(f"Approval {approval_request_id} rejected: {reason}")

            return {
                "status": ApprovalStatus.REJECTED.value,
                "reason": reason,
            }

        except Exception as e:
            logger.error(f"Error rejecting approval: {str(e)}")
            raise

    async def get_pending_approvals(
        self,
        user_id: UUID,
        session: AsyncSession,
        entity_type: Optional[ApprovalEntityType] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all pending approvals for user based on their role
        
        Returns: [
            {
                'approval_request_id': UUID,
                'entity_type': str,
                'entity_id': UUID,
                'changes': dict,
                'reason': str,
                'submitted_by': UUID,
                'submitted_at': datetime,
                'current_approver_role': str
            }
        ]
        """
        try:
            # Get user role
            user_role = await self._get_user_role(str(user_id), session)

            # Build query
            query = """
            SELECT 
                id, entity_type, entity_id, changes, reason,
                submitted_by, created_at, current_step, approval_chain,
                status
            FROM approval_requests
            WHERE status = :pending_status
            """

            params = {"pending_status": ApprovalStatus.PENDING.value}

            if entity_type:
                query += " AND entity_type = :entity_type"
                params["entity_type"] = entity_type.value

            query += " ORDER BY created_at DESC"

            result = await session.execute(query, params)
            approvals = []

            for row in result:
                chain = json.loads(row["approval_chain"])
                current_step = row["current_step"]
                
                # Only include if user's role matches current step
                if current_step < len(chain) and chain[current_step] == user_role:
                    approvals.append({
                        "approval_request_id": row["id"],
                        "entity_type": row["entity_type"],
                        "entity_id": row["entity_id"],
                        "changes": json.loads(row["changes"]),
                        "reason": row["reason"],
                        "submitted_by": row["submitted_by"],
                        "submitted_at": row["created_at"],
                        "current_approver_role": chain[current_step],
                        "status": row["status"],
                    })

            logger.info(
                f"Found {len(approvals)} pending approvals for {user_role}"
            )
            return approvals

        except Exception as e:
            logger.error(f"Error getting pending approvals: {str(e)}")
            raise

    async def get_approval_history(
        self,
        entity_type: ApprovalEntityType,
        entity_id: UUID,
        session: AsyncSession,
    ) -> List[Dict[str, Any]]:
        """
        Get complete approval history for an entity
        """
        try:
            query = """
            SELECT id, status, current_step, approvals, rejection_reason,
                   rejected_at, created_at
            FROM approval_requests
            WHERE entity_type = :entity_type AND entity_id = :entity_id
            ORDER BY created_at DESC
            """

            result = await session.execute(
                query,
                {
                    "entity_type": entity_type.value,
                    "entity_id": str(entity_id),
                }
            )

            history = []
            for row in result:
                approvals = json.loads(row["approvals"]) if row["approvals"] else []
                history.append({
                    "approval_request_id": row["id"],
                    "status": row["status"],
                    "approvals": approvals,
                    "rejection_reason": row["rejection_reason"],
                    "rejected_at": row["rejected_at"],
                    "created_at": row["created_at"],
                })

            return history

        except Exception as e:
            logger.error(f"Error getting approval history: {str(e)}")
            raise

    # ============ PRIVATE HELPER METHODS ============

    async def _get_approval_request(
        self, approval_request_id: str, session: AsyncSession
    ) -> Optional[Dict]:
        """Get approval request from database"""
        query = """
        SELECT id, entity_type, entity_id, changes, approval_chain,
               current_step, status, approvals
        FROM approval_requests WHERE id = :id
        """

        result = await session.execute(
            query, {"id": approval_request_id}
        )
        row = result.fetchone()

        if not row:
            return None

        return {
            "id": row["id"],
            "entity_type": row["entity_type"],
            "entity_id": row["entity_id"],
            "changes": json.loads(row["changes"]),
            "approval_chain": json.loads(row["approval_chain"]),
            "current_step": row["current_step"],
            "status": row["status"],
            "approvals": json.loads(row["approvals"]) if row["approvals"] else [],
        }

    async def _get_user_role(self, user_id: str, session: AsyncSession) -> str:
        """Get user's role"""
        query = "SELECT role FROM users WHERE id = :id"
        result = await session.execute(query, {"id": user_id})
        row = result.fetchone()
        return row["role"] if row else None

    async def _notify_approver(
        self,
        approval_request_id: str,
        approver_role: str,
        entity_type: str,
        entity_id: str,
        reason: str = "",
        session: AsyncSession = None,
    ):
        """Notify approver that action needed (email)"""
        # TODO: Integrate with notification service
        logger.info(f"[NOTIFY] {approver_role} approval needed for {entity_type}")

    async def _notify_director(
        self,
        approval_request_id: str,
        entity_type: str,
        entity_id: str,
        session: AsyncSession,
    ):
        """Notify Director (view-only)"""
        # TODO: Integrate with notification service
        logger.info(f"[NOTIFY] Director: {entity_type} {entity_id} approved")

    async def _notify_submitter_rejected(
        self,
        approval_request_id: str,
        rejection_reason: str,
        session: AsyncSession,
    ):
        """Notify submitter that approval was rejected"""
        # TODO: Integrate with notification service
        logger.info(f"[NOTIFY] Approval rejected: {rejection_reason}")

    async def _log_audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        changes: Dict,
        user_id: str,
        session: AsyncSession,
    ):
        """Log to audit trail"""
        query = """
        INSERT INTO audit_trail (
            action, entity_type, entity_id, changes, user_id, created_at
        ) VALUES (
            :action, :entity_type, :entity_id, :changes, :user_id, :created_at
        )
        """

        await session.execute(
            query,
            {
                "action": action,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "changes": json.dumps(changes),
                "user_id": user_id,
                "created_at": datetime.now(),
            }
        )

        await session.commit()


# Singleton instance
approval_engine = ApprovalWorkflowEngine()
