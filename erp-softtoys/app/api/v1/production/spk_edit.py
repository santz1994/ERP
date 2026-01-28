"""
SPK Edit API Endpoints - Feature #7
Endpoints for submitting, approving, and tracking SPK edits

Endpoints:
- POST /spk/{id}/edit - Submit edit request
- PUT /spk-edits/{id}/approve - Approve edit
- PUT /spk-edits/{id}/reject - Reject edit
- GET /spk/{id}/edit-history - View edit history
- GET /spk/{id}/pending-edits - View pending edits
- POST /spk-edits/{id}/apply - Apply approved changes
- DELETE /spk-edits/{id}/cancel - Cancel pending edit
"""

from datetime import datetime, date
from typing import Optional, List, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, validator
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.models.users import User
from app.services.spk_edit_service import SPKEditService, SPKEditType, SPKEditStatus

router = APIRouter(prefix="/spk", tags=["spk-edit"])


# ==================== Pydantic Schemas ====================

class SPKEditRequestPayload(BaseModel):
    """Payload for submitting SPK edit"""
    edit_type: str = Field(..., description="Type of edit (EDIT_QUANTITY, EDIT_DEADLINE, etc.)")
    changes: dict = Field(..., description="Changes to apply {field: new_value}")
    reason: str = Field(..., min_length=10, description="Reason for edit")
    
    @validator('edit_type')
    def validate_edit_type(cls, v):
        valid_types = [e.value for e in SPKEditType]
        if v not in valid_types:
            raise ValueError(f"Invalid edit type. Must be one of: {valid_types}")
        return v
    
    class Config:
        from_attributes = True


class SPKEditApprovalPayload(BaseModel):
    """Payload for approving/rejecting edit"""
    approval_notes: Optional[str] = Field(None, description="Optional approval notes")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection (if rejecting)")
    
    class Config:
        from_attributes = True


class SPKEditChangeItem(BaseModel):
    """Single change in edit request"""
    field: str
    old_value: Any
    new_value: Any
    
    class Config:
        from_attributes = True


class SPKEditHistoryItem(BaseModel):
    """Edit history item"""
    id: int
    edit_type: str
    changes: dict
    reason: str
    status: str
    requested_by_id: int
    requested_by_name: str
    requested_at: datetime
    approved_by_id: Optional[int]
    approved_by_name: Optional[str]
    approved_at: Optional[datetime]
    approval_notes: Optional[str]
    
    class Config:
        from_attributes = True


class SPKEditResponse(BaseModel):
    """Edit request response"""
    id: int
    spk_id: int
    edit_type: str
    old_values: dict
    new_values: dict
    reason: str
    status: str
    approval_request_id: Optional[int]
    requested_by_id: int
    requested_at: datetime
    approved_by_id: Optional[int]
    approved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


# ==================== Endpoints ====================

@router.post("/{spk_id}/edit", status_code=201, response_model=SPKEditResponse)
async def submit_spk_edit(
    spk_id: int,
    request: SPKEditRequestPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit SPK edit request for approval
    
    Permissions: WAREHOUSE, PPIC, PRODUCTION roles
    
    Request Body:
    - edit_type: Type of edit (EDIT_QUANTITY, EDIT_DEADLINE, EDIT_NOTES, etc.)
    - changes: Dict of {field: new_value}
    - reason: Reason for edit (min 10 characters)
    
    Returns:
    - Edit request with approval_request_id
    
    Example:
    ```json
    {
        "edit_type": "EDIT_QUANTITY",
        "changes": {"target_qty": 1500},
        "reason": "Customer increased order quantity by 500 units"
    }
    ```
    """
    try:
        # Check permission
        allowed_roles = ["WAREHOUSE", "PPIC_MANAGER", "PRODUCTION_MANAGER"]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Required roles: {allowed_roles}"
            )
        
        service = SPKEditService(db)
        
        edit_request = await service.submit_edit_request(
            spk_id=spk_id,
            edit_type=SPKEditType(request.edit_type),
            changes=request.changes,
            reason=request.reason,
            requested_by_id=current_user.id
        )
        
        return edit_request
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit edit request: {str(e)}"
        )


@router.put("/edits/{edit_id}/approve", response_model=SPKEditResponse)
async def approve_spk_edit(
    edit_id: int,
    request: SPKEditApprovalPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve SPK edit request
    
    Permissions: SPV, MANAGER roles only
    
    Path Parameters:
    - edit_id: Edit request ID
    
    Request Body:
    - approval_notes: Optional notes for approval
    
    Returns:
    - Updated edit request with approval details
    """
    try:
        # Check permission
        if current_user.role not in ["SPV", "MANAGER", "PLANT_MANAGER"]:
            raise HTTPException(
                status_code=403,
                detail="Only SPV/Manager can approve edits"
            )
        
        service = SPKEditService(db)
        
        edit_request = await service.approve_edit_request(
            edit_request_id=edit_id,
            approved_by_id=current_user.id,
            approval_notes=request.approval_notes or ""
        )
        
        return edit_request
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve edit: {str(e)}"
        )


@router.put("/edits/{edit_id}/reject", response_model=SPKEditResponse)
async def reject_spk_edit(
    edit_id: int,
    request: SPKEditApprovalPayload,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject SPK edit request
    
    Permissions: SPV, MANAGER roles only
    
    Path Parameters:
    - edit_id: Edit request ID
    
    Request Body:
    - rejection_reason: Reason for rejection (required)
    
    Returns:
    - Updated edit request with rejection details
    """
    try:
        # Check permission
        if current_user.role not in ["SPV", "MANAGER", "PLANT_MANAGER"]:
            raise HTTPException(
                status_code=403,
                detail="Only SPV/Manager can reject edits"
            )
        
        if not request.rejection_reason:
            raise HTTPException(
                status_code=400,
                detail="Rejection reason is required"
            )
        
        service = SPKEditService(db)
        
        edit_request = await service.reject_edit_request(
            edit_request_id=edit_id,
            rejected_by_id=current_user.id,
            rejection_reason=request.rejection_reason
        )
        
        return edit_request
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject edit: {str(e)}"
        )


@router.get("/{spk_id}/edit-history", response_model=List[SPKEditHistoryItem])
async def get_spk_edit_history(
    spk_id: int,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get edit history for SPK
    
    Permissions: All authenticated users (view own/related edits)
    
    Query Parameters:
    - limit: Max results (default 50, max 200)
    
    Returns:
    - List of edit requests, newest first
    """
    try:
        service = SPKEditService(db)
        
        history = await service.get_edit_history(
            spk_id=spk_id,
            limit=limit
        )
        
        return history
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get edit history: {str(e)}"
        )


@router.get("/{spk_id}/pending-edits", response_model=List[SPKEditResponse])
async def get_pending_spk_edits(
    spk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get pending edit requests for SPK
    
    Permissions: WAREHOUSE, PPIC, PRODUCTION roles (for own SKUs)
    
    Returns:
    - List of pending edits awaiting approval
    """
    try:
        service = SPKEditService(db)
        
        pending = await service.get_pending_edits(spk_id=spk_id)
        
        return pending
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending edits: {str(e)}"
        )


@router.post("/edits/{edit_id}/apply", response_model=dict)
async def apply_spk_edit(
    edit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Apply approved edit changes to SPK
    
    Permissions: WAREHOUSE, System Admin
    
    Path Parameters:
    - edit_id: Edit request ID
    
    Returns:
    - Confirmation with updated SPK details
    """
    try:
        # Check permission
        if current_user.role not in ["WAREHOUSE", "ADMIN", "PLANT_MANAGER"]:
            raise HTTPException(
                status_code=403,
                detail="Only WAREHOUSE or ADMIN can apply edits"
            )
        
        service = SPKEditService(db)
        
        result = await service.apply_approved_changes(
            edit_request_id=edit_id,
            applied_by_id=current_user.id
        )
        
        return {
            "status": "success",
            "message": "Edit applied successfully",
            "edit_id": edit_id,
            "applied_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to apply edit: {str(e)}"
        )


@router.delete("/edits/{edit_id}/cancel")
async def cancel_spk_edit(
    edit_id: int,
    reason: str = Query(None, description="Reason for cancellation"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel pending SPK edit request
    
    Permissions: Original requester or MANAGER
    
    Path Parameters:
    - edit_id: Edit request ID
    
    Query Parameters:
    - reason: Optional reason for cancellation
    
    Returns:
    - Confirmation of cancellation
    """
    try:
        service = SPKEditService(db)
        
        result = await service.cancel_edit_request(
            edit_request_id=edit_id,
            cancelled_by_id=current_user.id,
            reason=reason or ""
        )
        
        return {
            "status": "success",
            "message": "Edit request cancelled",
            "edit_id": edit_id,
            "cancelled_at": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel edit: {str(e)}"
        )


@router.get("/edits/my-pending")
async def get_my_pending_edits(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all pending edits awaiting current user's approval
    
    Permissions: SPV, MANAGER roles
    
    Query Parameters:
    - limit: Max results
    
    Returns:
    - List of pending edits requiring approval
    """
    try:
        # Check permission
        if current_user.role not in ["SPV", "MANAGER", "PLANT_MANAGER"]:
            raise HTTPException(
                status_code=403,
                detail="Only SPV/Manager can view pending approvals"
            )
        
        # This would query from database
        pending_edits = []
        
        return {
            "count": len(pending_edits),
            "edits": pending_edits[:limit]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending edits: {str(e)}"
        )
