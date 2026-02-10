"""
Material Debt Management API Endpoints
Feature #4: Negative Inventory (Material Debt) System

Endpoints for creating, approving, and adjusting material debt
Requires integration with Feature #2: Approval Workflow
"""
import logging
from datetime import date
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, require_permission
from app.core.permissions import ModuleName, Permission
from app.core.models.users import User
from app.services.material_debt_service import MaterialDebtService, BOMAllocationError

logger = logging.getLogger(__name__)


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class MaterialDebtCreateRequest(BaseModel):
    """Request to create new material debt"""
    spk_id: int = Field(..., description="SPK ID that needs material")
    material_id: int = Field(..., description="Product/Material ID in debt")
    qty_owed: Decimal = Field(..., gt=0, description="Quantity owed")
    reason: str = Field(..., max_length=500, description="Reason for debt (e.g., 'Material PO-XXX sedang di jalan')")
    department: str = Field(..., description="Department creating debt (e.g., 'Cutting')")
    due_date: Optional[date] = Field(None, description="Expected receipt date")
    allow_production: bool = Field(False, description="Allow production to start while debt pending")


class MaterialDebtCreateResponse(BaseModel):
    """Response when material debt created"""
    debt_id: int
    spk_id: int
    material_id: int
    qty_owed: float
    approval_status: str
    status: str
    allow_production_start: bool
    message: str
    next_step: str


class MaterialDebtApproveRequest(BaseModel):
    """Request to approve/reject material debt"""
    approval_decision: str = Field(..., description="'APPROVE' or 'REJECT'")
    approver_role: str = Field(..., description="'SPV' or 'MANAGER'")
    notes: Optional[str] = Field(None, max_length=500, description="Approval notes")


class MaterialDebtApproveResponse(BaseModel):
    """Response after approval decision"""
    debt_id: int
    approval_status: str
    approved_by: str
    approved_at: str
    next_approver: Optional[str]
    can_start_production: bool
    message: str


class MaterialDebtAdjustRequest(BaseModel):
    """Request to adjust debt when material arrives"""
    actual_received_qty: Decimal = Field(..., gt=0, description="Actual quantity received")
    adjustment_notes: str = Field(..., max_length=500, description="Notes about delivery")
    received_date: Optional[date] = Field(None, description="Date material received")


class MaterialDebtAdjustResponse(BaseModel):
    """Response after debt adjustment"""
    debt_id: int
    debt_status: str
    qty_owed: int
    qty_settled: int
    remaining_debt: int
    excess_qty: int
    settlement_date: str
    message: str


class MaterialDebtDetailResponse(BaseModel):
    """Detailed material debt information"""
    debt_id: int
    spk_id: int
    material_id: int
    qty_owed: int
    qty_settled: int
    remaining: int
    approval_status: str
    created_by_id: int
    created_date: Optional[str]
    approved_by_id: Optional[int]
    approved_date: Optional[str]
    reason: str
    settlement_history: list


class OutstandingDebtsResponse(BaseModel):
    """List of outstanding debts"""
    count: int
    total_outstanding_qty: int
    total_outstanding_value: float
    debts: list


# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="/api/v1/warehouse/material-debt",
    tags=["Warehouse - Material Debt Management"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post(
    "/create",
    response_model=MaterialDebtCreateResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Material Debt Entry",
    description="""
    Create a material debt entry when production needs to start without all materials available.
    
    **Required Permission**: warehouse.manage_debt
    
    **Business Rules**:
    - Production can proceed with debt if `allow_production=true`
    - Debt must be approved by SPV → Manager before production
    - Audit trail: who created, when, reason
    
    **Next Steps**:
    - Submit debt for approval via Feature #2: Approval Workflow
    - Wait for SPV & Manager approval
    - Production can start after approval
    """
)
async def create_material_debt(
    request: MaterialDebtCreateRequest,
    current_user: User = Depends(require_permission(ModuleName.WAREHOUSE, Permission.CREATE)),
    db: Session = Depends(get_db)
):
    """Create material debt entry"""
    try:
        service = MaterialDebtService(db)
        result = await service.create_material_debt(
            spk_id=request.spk_id,
            material_id=request.material_id,
            qty_owed=request.qty_owed,
            reason=request.reason,
            department=request.department,
            created_by_id=current_user.id,
            due_date=request.due_date,
            allow_production=request.allow_production
        )
        logger.info(f"Material debt created by {current_user.username}: SPK={request.spk_id}")
        return result
        
    except BOMAllocationError as e:
        logger.error(f"Material debt creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in create_material_debt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create material debt"
        )


@router.post(
    "/{debt_id}/approve",
    response_model=MaterialDebtApproveResponse,
    summary="Approve or Reject Material Debt",
    description="""
    Approve or reject material debt as part of Feature #2: Approval Workflow
    
    **Approval Chain**:
    1. SPV approves → status = SPV_APPROVED (waiting for Manager)
    2. Manager approves → status = APPROVED (production can start!)
    3. OR Reject at any step → status = REJECTED (production blocked)
    
    **Required Permissions**:
    - SPV: warehouse.approve_debt + role check
    - Manager: warehouse.approve_debt + role check
    
    **Business Rules**:
    - Only pending debts can be approved
    - Both SPV & Manager must approve
    - Director gets view-only notification
    """
)
async def approve_material_debt(
    debt_id: int,
    request: MaterialDebtApproveRequest,
    current_user: User = Depends(require_permission(ModuleName.WAREHOUSE, Permission.APPROVE)),
    db: Session = Depends(get_db)
):
    """Approve or reject material debt"""
    try:
        service = MaterialDebtService(db)
        result = await service.approve_material_debt(
            debt_id=debt_id,
            approval_decision=request.approval_decision,
            approver_id=current_user.id,
            approver_role=request.approver_role,
            notes=request.notes
        )
        logger.info(f"Material debt {debt_id} {request.approval_decision} by {current_user.username}")
        return result
        
    except BOMAllocationError as e:
        logger.error(f"Material debt approval failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in approve_material_debt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to approve material debt"
        )


@router.post(
    "/{debt_id}/adjust",
    response_model=MaterialDebtAdjustResponse,
    summary="Adjust Material Debt (Reconciliation)",
    description="""
    Adjust material debt when material arrives from supplier.
    
    **Business Logic**:
    - If actual_received_qty == qty_owed → Debt FULLY_SETTLED
    - If actual_received_qty < qty_owed → Debt PARTIAL_SETTLED (remaining still owed)
    - If actual_received_qty > qty_owed → EXCESS_RECEIVED (excess added back to inventory)
    
    **Required Permission**: warehouse.write_debt
    
    **Next Steps**:
    - System records settlement in material_debt_settlement table
    - For excess: automatically add back to warehouse inventory
    - For shortfall: continue waiting for material
    """
)
async def adjust_material_debt(
    debt_id: int,
    request: MaterialDebtAdjustRequest,
    current_user: User = Depends(require_permission(ModuleName.WAREHOUSE, Permission.UPDATE)),
    db: Session = Depends(get_db)
):
    """Adjust material debt when material arrives"""
    try:
        service = MaterialDebtService(db)
        result = await service.adjust_material_debt(
            debt_id=debt_id,
            actual_received_qty=request.actual_received_qty,
            adjustment_notes=request.adjustment_notes,
            recorded_by_id=current_user.id,
            received_date=request.received_date
        )
        logger.info(f"Material debt {debt_id} adjusted by {current_user.username}")
        return result
        
    except BOMAllocationError as e:
        logger.error(f"Material debt adjustment failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in adjust_material_debt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust material debt"
        )


@router.get(
    "/outstanding",
    response_model=OutstandingDebtsResponse,
    summary="Get Outstanding Material Debts",
    description="""
    Get list of all outstanding material debts not yet fully settled
    
    **Required Permission**: warehouse.view_debt
    
    **Query Parameters**:
    - `only_pending_approval`: If true, only show debts waiting approval
    
    **Use Cases**:
    1. PPIC: Check total outstanding before creating new MOs
    2. Warehouse: Monitor material expected arrivals
    3. Finance: Track liability for balance sheet
    4. Manager: Overview of all active debts
    
    **Business Rules**:
    - If total debt > threshold (Rp 50M) → block new PO creation
    - This is checked before Purchasing creates new PO
    """
)
async def get_outstanding_debts(
    only_pending_approval: bool = False,
    current_user: User = Depends(require_permission(ModuleName.WAREHOUSE, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """Get list of outstanding debts"""
    try:
        service = MaterialDebtService(db)
        result = await service.get_outstanding_debts(
            only_pending_approval=only_pending_approval
        )
        return result
        
    except BOMAllocationError as e:
        logger.error(f"Failed to get outstanding debts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_outstanding_debts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get outstanding debts"
        )


@router.get(
    "/{debt_id}",
    response_model=MaterialDebtDetailResponse,
    summary="Get Material Debt Details",
    description="""
    Get detailed information about a material debt including settlement history
    
    **Required Permission**: warehouse.view_debt
    
    **Query Parameters**:
    - `only_pending_approval`: If true, only show debts waiting approval
    
    **Use Cases**:
    1. PPIC: Check total outstanding before creating new MOs
    2. Warehouse: Monitor material expected arrivals
    3. Finance: Track liability for balance sheet
    4. Manager: Overview of all active debts
    
    **Business Rules**:
    - If total debt > threshold (Rp 50M) → block new PO creation
    - This is checked before Purchasing creates new PO
    """
)
async def get_outstanding_debts(
    only_pending_approval: bool = False,
    current_user: User = Depends(require_permission(ModuleName.WAREHOUSE, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """Get list of outstanding debts"""
    try:
        service = MaterialDebtService(db)
        result = await service.get_outstanding_debts(
            only_pending_approval=only_pending_approval
        )
        return result
        
    except BOMAllocationError as e:
        logger.error(f"Failed to get outstanding debts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Unexpected error in get_outstanding_debts: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get outstanding debts"
        )


@router.get(
    "/check-threshold",
    summary="Check Debt Threshold",
    description="""
    Check if total outstanding debt exceeds threshold (Rp 50M)
    
    **Purpose**: Block new PO creation if debt is too high
    
    **Response**:
    ```json
    {
        "threshold_exceeded": false,
        "current_debt_value": 45000000,
        "threshold_value": 50000000,
        "message": "Can create new PO (debt below threshold)"
    }
    ```
    """
)
async def check_debt_threshold(
    current_user: User = Depends(require_permission(ModuleName.WAREHOUSE, Permission.VIEW)),
    db: Session = Depends(get_db)
):
    """Check if debt threshold exceeded"""
    try:
        service = MaterialDebtService(db)
        threshold_exceeded = service.check_debt_threshold()
        
        return {
            "threshold_exceeded": threshold_exceeded,
            "message": "Cannot create new PO (debt exceeds threshold)" if threshold_exceeded 
                       else "Can create new PO (debt below threshold)"
        }
        
    except Exception as e:
        logger.error(f"Failed to check debt threshold: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check debt threshold"
        )
