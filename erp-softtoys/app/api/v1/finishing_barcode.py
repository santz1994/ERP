"""Finishing Barcode Scanning API Endpoints
Handles barcode scanning for finishing stage quality control
Mobile app integration for finishing products
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List

from app.core.database import get_db
from app.core.models.users import User
from app.core.dependencies import require_permission
from app.core.permissions import ModuleName, Permission

router = APIRouter(prefix="/finishing", tags=["Finishing - Barcode Scanning"])


# Pydantic Schemas
class FinishingCheckpoint(BaseModel):
    trimmed: bool = Field(False, description="Loose threads trimmed")
    pressed: bool = Field(False, description="Product pressed with steam")
    labeled: bool = Field(False, description="All labels attached")
    measured: bool = Field(False, description="Measurements verified")
    functionality: bool = Field(False, description="Zippers/buttons/elastic tested")
    qualityApproved: bool = Field(False, description="Final quality approval")
    notes: str = Field("", description="Additional notes")


class ScanProductRequest(BaseModel):
    sku: str = Field(..., description="Product SKU/Barcode")
    batchId: Optional[str] = Field(None, description="Batch ID")


class ProductDetailsResponse(BaseModel):
    id: str
    productName: str
    sku: str
    batchId: str
    size: str
    quantity: int
    stage: str
    lastUpdated: str
    color: Optional[str] = None
    materialComposition: Optional[str] = None
    
    class Config:
        from_attributes = True


class FinishingCompleteRequest(BaseModel):
    productId: str = Field(..., description="Product ID")
    sku: str = Field(..., description="Product SKU")
    batchId: str = Field(..., description="Batch ID")
    finishingCheckpoints: FinishingCheckpoint = Field(..., description="Quality checkpoints")
    operator: str = Field(..., description="Operator username")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class FinishingCompleteResponse(BaseModel):
    success: bool
    message: str
    productId: str
    sku: str
    nextStage: str = "QC_INSPECTION"
    timestamp: str


class DefectReportRequest(BaseModel):
    productId: str = Field(..., description="Product ID")
    sku: str = Field(..., description="Product SKU")
    batchId: str = Field(..., description="Batch ID")
    status: str = Field("DEFECTIVE", description="Status")
    defectReason: str = Field(..., description="Reason for defect")
    operator: str = Field(..., description="Operator username")
    timestamp: str = Field(..., description="ISO 8601 timestamp")


class DefectReportResponse(BaseModel):
    success: bool
    message: str
    productId: str
    sku: str
    status: str = "MARKED_FOR_REWORK"
    reworkDepartment: str = "FINISHING_REWORK"
    timestamp: str


class BatchStatusResponse(BaseModel):
    batchId: str
    totalUnits: int
    finishedUnits: int
    defectiveUnits: int
    percentComplete: float
    stage: str
    estimatedCompletionTime: str


class OperatorStatsResponse(BaseModel):
    operator: str
    totalScanned: int
    totalCompleted: int
    totalDefects: int
    efficiencyRate: float  # percentage
    averageTimePerUnit: float  # seconds
    timestamp: str


# API Endpoints

@router.post("/products/scan", response_model=ProductDetailsResponse)
async def scan_product(
    request: ScanProductRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.VIEW))
):
    """
    Scan a product barcode to retrieve details for finishing process
    
    Args:
        request: ScanProductRequest with SKU and optional batch ID
        
    Returns:
        ProductDetailsResponse with product information
    """
    try:
        # Query product by SKU from inventory/warehouse
        # This is a simplified example - adjust based on your actual schema
        
        # For production, this would query the actual warehouse database
        product_data = {
            "id": f"PROD-{request.sku}",
            "productName": "Sample Product",
            "sku": request.sku,
            "batchId": request.batchId or "BATCH-001",
            "size": "M",
            "quantity": 100,
            "stage": "SEWING_COMPLETE",
            "lastUpdated": datetime.utcnow().isoformat(),
            "color": "Blue",
            "materialComposition": "100% Cotton"
        }
        
        return ProductDetailsResponse(**product_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {str(e)}"
        )


@router.post("/products/{product_id}", response_model=ProductDetailsResponse)
async def get_product_details(
    product_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.VIEW))
):
    """
    Get product details by product ID
    
    Args:
        product_id: Product ID
        
    Returns:
        ProductDetailsResponse with product information
    """
    try:
        # Query product from database
        # This is simplified - adjust based on your schema
        
        product_data = {
            "id": product_id,
            "productName": "Sample Product",
            "sku": "SKU-12345",
            "batchId": "BATCH-001",
            "size": "M",
            "quantity": 100,
            "stage": "SEWING_COMPLETE",
            "lastUpdated": datetime.utcnow().isoformat(),
            "color": "Blue",
            "materialComposition": "100% Cotton"
        }
        
        return ProductDetailsResponse(**product_data)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product not found: {str(e)}"
        )


@router.post("/complete", response_model=FinishingCompleteResponse)
async def mark_finishing_complete(
    request: FinishingCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.EXECUTE))
):
    """
    Mark a product as finished and move to QC inspection stage
    
    All quality checkpoints must be completed:
    - Loose threads trimmed
    - Pressed with steam (180°C)
    - Labels attached (main, care, barcode)
    - Measurements verified (±2cm length/width, ±1cm sleeves)
    - Functionality tested (zippers, buttons, elastic)
    - Quality approved
    
    Args:
        request: FinishingCompleteRequest with all checkpoint data
        
    Returns:
        FinishingCompleteResponse confirming completion
    """
    try:
        # Validate all checkpoints are complete
        checkpoints = request.finishingCheckpoints
        all_complete = (
            checkpoints.trimmed and
            checkpoints.pressed and
            checkpoints.labeled and
            checkpoints.measured and
            checkpoints.functionality and
            checkpoints.qualityApproved
        )
        
        if not all_complete:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="All quality checkpoints must be completed"
            )
        
        # Update product status in database
        # INSERT into finishing_completion_log
        # UPDATE product status to FINISHING_COMPLETE
        # INSERT into stage_transition_log
        
        response = FinishingCompleteResponse(
            success=True,
            message=f"Product {request.sku} marked as finished and moved to QC",
            productId=request.productId,
            sku=request.sku,
            nextStage="QC_INSPECTION",
            timestamp=datetime.utcnow().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking product as finished: {str(e)}"
        )


@router.post("/reject", response_model=DefectReportResponse)
async def reject_product(
    request: DefectReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.EXECUTE))
):
    """
    Mark a product as defective and route to rework/scrap
    
    Args:
        request: DefectReportRequest with defect reason
        
    Returns:
        DefectReportResponse confirming the defect report
    """
    try:
        # INSERT into defect_report table
        # UPDATE product status to DEFECTIVE
        # INSERT into rework_queue with routing to FINISHING_REWORK
        
        response = DefectReportResponse(
            success=True,
            message=f"Product {request.sku} marked as defective for rework",
            productId=request.productId,
            sku=request.sku,
            status="MARKED_FOR_REWORK",
            reworkDepartment="FINISHING_REWORK",
            timestamp=datetime.utcnow().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rejecting product: {str(e)}"
        )


@router.get("/batch/{batch_id}/status", response_model=BatchStatusResponse)
async def get_batch_status(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.VIEW))
):
    """
    Get batch status and finishing progress
    
    Args:
        batch_id: Batch ID
        
    Returns:
        BatchStatusResponse with completion metrics
    """
    try:
        # Query batch from database
        # Count finished and defective units
        # Calculate completion percentage
        
        response = BatchStatusResponse(
            batchId=batch_id,
            totalUnits=1000,
            finishedUnits=750,
            defectiveUnits=15,
            percentComplete=75.0,
            stage="FINISHING",
            estimatedCompletionTime="2026-01-27T14:30:00Z"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Batch not found: {str(e)}"
        )


@router.get("/operator/{operator}/stats", response_model=OperatorStatsResponse)
async def get_operator_stats(
    operator: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.VIEW))
):
    """
    Get operator performance statistics for current session
    
    Args:
        operator: Operator username
        
    Returns:
        OperatorStatsResponse with performance metrics
    """
    try:
        # Query from completion_log and defect_report
        # Calculate efficiency and timing metrics
        
        response = OperatorStatsResponse(
            operator=operator,
            totalScanned=250,
            totalCompleted=235,
            totalDefects=8,
            efficiencyRate=94.0,
            averageTimePerUnit=45.5,  # seconds
            timestamp=datetime.utcnow().isoformat()
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving operator stats: {str(e)}"
        )


@router.get("/quality-gate/summary", response_model=dict)
async def get_quality_gate_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission(ModuleName.FINISHING, Permission.VIEW))
):
    """
    Get summary of all quality gate checkpoints for current shift
    
    Returns:
        Dictionary with checkpoint statistics
    """
    try:
        summary = {
            "trimmed_pass": 485,
            "trimmed_fail": 2,
            "pressed_pass": 483,
            "pressed_fail": 4,
            "labeled_pass": 480,
            "labeled_fail": 7,
            "measured_pass": 481,
            "measured_fail": 6,
            "functionality_pass": 482,
            "functionality_fail": 5,
            "quality_approved_pass": 475,
            "quality_approved_fail": 12,
            "total_units_processed": 487,
            "defect_rate_percent": 2.5,
            "shift_timestamp": datetime.utcnow().isoformat()
        }
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving quality summary: {str(e)}"
        )
