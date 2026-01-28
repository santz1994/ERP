"""
BOM API Endpoints
Feature #1: BOM Manufacturing Auto-Allocate
Route: /api/v1/production/bom

Endpoints:
- POST /create-with-auto-allocation - Create SPK with automatic material allocation
- GET /allocation-preview/{article_id} - Preview material allocation before SPK creation
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.core.auth import get_current_user
from app.services.bom_service import BOMService, BOMAllocationError
from app.core.logger import logger

router = APIRouter(prefix="/api/v1/production/bom", tags=["BOM - Material Allocation"])

# Initialize service
bom_service = BOMService()


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================

class MaterialAllocationItem(BaseModel):
    """Material allocation result item"""
    material_id: int
    material_name: str
    qty_needed: float
    qty_allocated: float
    warehouse_location: str
    status: str  # ALLOCATED, RESERVED, PENDING_DEBT
    spk_material_allocation_id: Optional[int] = None


class DebtItem(BaseModel):
    """Material debt item (shortage)"""
    material_id: int
    material_name: str
    qty_shortage: float
    material_debt_id: Optional[int] = None
    debt_status: str  # PENDING_APPROVAL


class AllocationSummary(BaseModel):
    """Allocation summary"""
    total_materials: int
    fully_allocated: int
    partially_allocated: int
    shortage_count: int


class SPKCreateWithAllocationRequest(BaseModel):
    """Request to create SPK with automatic material allocation"""
    mo_id: int = Field(..., description="Manufacturing Order ID")
    article_id: int = Field(..., description="Article/Product ID")
    quantity: int = Field(..., gt=0, description="Target quantity to produce")
    target_date: Optional[str] = Field(None, description="Target completion date (YYYY-MM-DD)")
    department: str = Field(..., description="Department (Cutting, Sewing, Finishing, Packing)")
    allow_negative_inventory: bool = Field(False, description="Allow negative inventory if material shortage")
    notes: Optional[str] = Field(None, description="Additional notes for SPK")


class SPKCreateWithAllocationResponse(BaseModel):
    """Response for SPK creation with allocation"""
    success: bool
    spk_id: int
    allocated_materials: List[MaterialAllocationItem]
    debt_materials: List[DebtItem]
    summary: AllocationSummary
    message: str


class AllocationPreviewResponse(BaseModel):
    """Response for allocation preview"""
    article_id: int
    quantity: int
    allocated_materials: List[MaterialAllocationItem]
    debt_materials: List[DebtItem]
    summary: AllocationSummary
    can_proceed: bool = Field(..., description="Whether all materials are available (or partial with debt approval)")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@router.post(
    "/create-with-auto-allocation",
    response_model=SPKCreateWithAllocationResponse,
    summary="Create SPK with Automatic Material Allocation",
    description="Create new SPK with automatic material allocation from warehouse based on BOM Manufacturing"
)
async def create_spk_with_auto_allocation(
    request: SPKCreateWithAllocationRequest,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Create SPK with automatic material allocation from warehouse
    
    Flow:
    1. Retrieve BOM Manufacturing for article
    2. Calculate material requirements
    3. Check warehouse stock
    4. Auto-allocate available material
    5. Create material debt for shortages (if allowed)
    6. Create SPK record
    
    Example:
    ```json
    POST /api/v1/production/bom/create-with-auto-allocation
    {
        "mo_id": 1,
        "article_id": 5,
        "quantity": 500,
        "target_date": "2026-02-05",
        "department": "Cutting",
        "allow_negative_inventory": false
    }
    ```
    
    Response:
    ```json
    {
        "success": true,
        "spk_id": 123,
        "allocated_materials": [
            {
                "material_id": 10,
                "material_name": "Cotton 100%",
                "qty_needed": 250.0,
                "qty_allocated": 250.0,
                "warehouse_location": "Primary",
                "status": "ALLOCATED",
                "spk_material_allocation_id": 456
            }
        ],
        "debt_materials": [],
        "summary": {
            "total_materials": 1,
            "fully_allocated": 1,
            "partially_allocated": 0,
            "shortage_count": 0
        },
        "message": "SPK created successfully with full material allocation"
    }
    ```
    """
    try:
        logger.info(
            f"Create SPK with auto-allocation: MO {request.mo_id}, "
            f"Article {request.article_id}, Qty {request.quantity}, "
            f"Department {request.department}, User {current_user.id}"
        )

        # Validate department
        valid_departments = ["Cutting", "Embroidery", "Sewing", "Finishing", "Packing"]
        if request.department not in valid_departments:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid department. Must be one of: {', '.join(valid_departments)}"
            )

        # TODO: Create SPK record first
        # For now, using placeholder SPK ID
        spk_id = 999  # Placeholder

        # Perform material allocation
        allocation_result = await bom_service.allocate_material_for_spk(
            spk_id=spk_id,
            mo_id=request.mo_id,
            article_id=request.article_id,
            quantity=request.quantity,
            department=request.department,
            user_id=current_user.id,
            session=session,
            allow_negative_inventory=request.allow_negative_inventory,
        )

        if not allocation_result["success"]:
            raise BOMAllocationError("Material allocation failed")

        # Determine message
        shortage_count = allocation_result["summary"]["shortage_count"]
        fully_allocated = allocation_result["summary"]["fully_allocated"]
        total = allocation_result["summary"]["total_materials"]

        if shortage_count == 0:
            message = f"✅ SPK created successfully with full material allocation ({fully_allocated}/{total} materials)"
        elif shortage_count < total:
            message = f"⚠️ SPK created with partial material allocation. {shortage_count} material(s) have debt pending approval"
        else:
            message = f"❌ SPK created but all materials require debt approval"

        logger.info(f"SPK {spk_id} created: {message}")

        return SPKCreateWithAllocationResponse(
            success=True,
            spk_id=spk_id,
            allocated_materials=[MaterialAllocationItem(**item) for item in allocation_result["allocated_materials"]],
            debt_materials=[DebtItem(**item) for item in allocation_result["debt_materials"]],
            summary=AllocationSummary(**allocation_result["summary"]),
            message=message,
        )

    except BOMAllocationError as e:
        logger.error(f"BOM allocation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Allocation error: {str(e)}")
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Validation error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error creating SPK: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/allocation-preview",
    response_model=AllocationPreviewResponse,
    summary="Preview Material Allocation",
    description="Preview material allocation for article without creating SPK"
)
async def get_allocation_preview(
    article_id: int = Query(..., description="Article ID"),
    quantity: int = Query(..., gt=0, description="Quantity to produce"),
    allow_negative: bool = Query(False, description="Allow negative inventory"),
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Preview material allocation without creating SPK
    
    Useful for:
    - Frontend to show user what materials will be allocated
    - Check if production can proceed immediately
    - Identify material shortages before SPK creation
    
    Example:
    ```
    GET /api/v1/production/bom/allocation-preview?article_id=5&quantity=500
    ```
    
    Response shows allocated materials and any shortages
    """
    try:
        logger.info(
            f"Preview allocation: Article {article_id}, Qty {quantity}, "
            f"Allow negative: {allow_negative}"
        )

        # Use temporary SPK ID for preview
        temp_spk_id = -1  # Negative ID indicates preview mode

        allocation_result = await bom_service.allocate_material_for_spk(
            spk_id=temp_spk_id,
            mo_id=0,  # Not needed for preview
            article_id=article_id,
            quantity=quantity,
            department="Cutting",  # Default for preview
            user_id=current_user.id,
            session=session,
            allow_negative_inventory=allow_negative,
        )

        shortage_count = allocation_result["summary"]["shortage_count"]
        total = allocation_result["summary"]["total_materials"]
        can_proceed = shortage_count == 0

        return AllocationPreviewResponse(
            article_id=article_id,
            quantity=quantity,
            allocated_materials=[MaterialAllocationItem(**item) for item in allocation_result["allocated_materials"]],
            debt_materials=[DebtItem(**item) for item in allocation_result["debt_materials"]],
            summary=AllocationSummary(**allocation_result["summary"]),
            can_proceed=can_proceed,
        )

    except Exception as e:
        logger.error(f"Error generating allocation preview: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating preview: {str(e)}")


@router.get(
    "/spk/{spk_id}/allocations",
    response_model=Dict[str, Any],
    summary="Get SPK Material Allocations",
    description="Get all material allocations for specific SPK"
)
async def get_spk_allocations(
    spk_id: int,
    current_user = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Get all material allocations for a specific SPK
    
    Shows what materials were allocated, their status, and any debts
    """
    try:
        logger.info(f"Fetching allocations for SPK {spk_id}")

        # TODO: Query database for allocations
        # For now return placeholder
        return {
            "spk_id": spk_id,
            "allocations": [],
            "summary": {
                "total": 0,
                "allocated": 0,
                "pending_debt": 0,
            }
        }

    except Exception as e:
        logger.error(f"Error fetching SPK allocations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching allocations: {str(e)}")
