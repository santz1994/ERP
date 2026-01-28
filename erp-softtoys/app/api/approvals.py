"""
API Endpoints for Approval Workflow
Route: /api/v1/approvals
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.services.approval_service import ApprovalWorkflowEngine, ApprovalEntityType
from app.core.auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session

router = APIRouter(prefix="/api/v1/approvals", tags=["approvals"])

# Initialize approval engine
approval_engine = ApprovalWorkflowEngine()


class SubmitApprovalRequest(BaseModel):
    """Request to submit entity for approval"""
    entity_type: str  # SPK_CREATE, SPK_EDIT_QUANTITY, etc
    entity_id: UUID
    changes: dict  # What is being changed
    reason: str  # Why the change


class ApprovalActionRequest(BaseModel):
    """Request to approve/reject"""
    notes: Optional[str] = None


class RejectApprovalRequest(BaseModel):
    """Request to reject approval"""
    reason: str


@router.post("/submit", response_model=dict)
async def submit_for_approval(
    request: SubmitApprovalRequest,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Submit entity for approval
    
    Requires: ADMIN or SPV role (admin can submit)
    
    Example:
    ```
    POST /api/v1/approvals/submit
    {
        "entity_type": "SPK_EDIT_QUANTITY",
        "entity_id": "123e4567-e89b-12d3-a456-426614174000",
        "changes": {"quantity": 500},
        "reason": "Customer requested increase"
    }
    ```
    
    Response:
    ```
    {
        "approval_request_id": "456e7891-e89b-12d3-a456-426614174111",
        "status": "PENDING",
        "approval_chain": ["SPV", "MANAGER"],
        "current_step": 0,
        "next_approver": "SPV"
    }
    ```
    """
    try:
        # Verify entity_type is valid
        try:
            entity_type = ApprovalEntityType(request.entity_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid entity_type: {request.entity_type}"
            )

        # Submit for approval
        result = await approval_engine.submit_for_approval(
            entity_type=entity_type,
            entity_id=request.entity_id,
            changes=request.changes,
            reason=request.reason,
            submitted_by=current_user.id,
            session=session,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting approval: {str(e)}")


@router.put("/{approval_id}/approve", response_model=dict)
async def approve_request(
    approval_id: UUID,
    request: ApprovalActionRequest,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Approve current approval step
    
    Requires: SPV or MANAGER role (depending on current step)
    
    Example:
    ```
    PUT /api/v1/approvals/456e7891-e89b-12d3-a456-426614174111/approve
    {
        "notes": "Looks good, proceed"
    }
    ```
    
    Response:
    ```
    {
        "status": "SPV_APPROVED",  or "MANAGER_APPROVED" or "APPROVED"
        "current_step": 1,
        "next_approver": "MANAGER",  or null if final
        "is_final_approval": false
    }
    ```
    """
    try:
        result = await approval_engine.approve(
            approval_request_id=approval_id,
            approver_id=current_user.id,
            notes=request.notes or "",
            session=session,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error approving: {str(e)}")


@router.put("/{approval_id}/reject", response_model=dict)
async def reject_request(
    approval_id: UUID,
    request: RejectApprovalRequest,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Reject approval request
    
    Requires: Current approver role
    
    Example:
    ```
    PUT /api/v1/approvals/456e7891-e89b-12d3-a456-426614174111/reject
    {
        "reason": "Does not meet quality standards"
    }
    ```
    
    Response:
    ```
    {
        "status": "REJECTED",
        "reason": "Does not meet quality standards"
    }
    ```
    """
    try:
        result = await approval_engine.reject(
            approval_request_id=approval_id,
            rejector_id=current_user.id,
            reason=request.reason,
            session=session,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error rejecting: {str(e)}")


@router.get("/my-pending", response_model=List[dict])
async def get_my_pending_approvals(
    entity_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all pending approvals for current user
    
    Requires: Any authenticated user
    
    Query Parameters:
    - entity_type: Optional filter (SPK_CREATE, SPK_EDIT_QUANTITY, etc)
    - limit: Max results (default 50)
    
    Example:
    ```
    GET /api/v1/approvals/my-pending?entity_type=SPK_EDIT_QUANTITY&limit=20
    ```
    
    Response:
    ```
    [
        {
            "approval_request_id": "456e7891-e89b-12d3-a456-426614174111",
            "entity_type": "SPK_EDIT_QUANTITY",
            "entity_id": "123e4567-e89b-12d3-a456-426614174000",
            "changes": {"quantity": 500},
            "reason": "Customer request",
            "submitted_by": "user-123",
            "submitted_at": "2026-01-28T10:30:00",
            "current_approver_role": "SPV",
            "status": "PENDING"
        }
    ]
    ```
    """
    try:
        # Parse entity_type if provided
        filter_entity_type = None
        if entity_type:
            try:
                filter_entity_type = ApprovalEntityType(entity_type)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid entity_type: {entity_type}")

        # Get pending approvals
        pending = await approval_engine.get_pending_approvals(
            user_id=current_user.id,
            entity_type=filter_entity_type,
            session=session,
        )

        return pending[:limit]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching approvals: {str(e)}")


@router.get("/{approval_id}/history", response_model=List[dict])
async def get_approval_history(
    approval_id: UUID,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get complete approval history for an entity
    
    Requires: Any authenticated user
    
    Example:
    ```
    GET /api/v1/approvals/456e7891-e89b-12d3-a456-426614174111/history
    ```
    
    Response:
    ```
    [
        {
            "approval_request_id": "456e7891-e89b-12d3-a456-426614174111",
            "status": "APPROVED",
            "approvals": [
                {
                    "step": "SPV",
                    "approved_by": "user-123",
                    "approved_at": "2026-01-28T10:30:00",
                    "notes": "Looks good"
                },
                {
                    "step": "MANAGER",
                    "approved_by": "user-456",
                    "approved_at": "2026-01-28T11:00:00",
                    "notes": "Approved"
                }
            ],
            "created_at": "2026-01-28T10:00:00"
        }
    ]
    ```
    """
    try:
        # TODO: Get entity_type and entity_id from approval_id
        # For now, just return empty
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")


# Register router
def register_approval_routes(app):
    """Register approval routes to app"""
    app.include_router(router)
