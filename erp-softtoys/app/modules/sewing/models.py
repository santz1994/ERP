"""
Sewing Module Models & Schemas
Handles material input validation, sewing process, QC, and transfer to Finishing
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SewingStatus(str, Enum):
    """Sewing work order status"""
    PENDING = "Pending"
    MATERIAL_CHECK = "Material Check"
    ASSEMBLY = "Assembly"
    LABELING = "Labeling"
    STIK = "Stik Balik"
    QC_INSPECTION = "QC Inspection"
    READY_TRANSFER = "Ready Transfer"
    COMPLETED = "Completed"


class SewingQCResult(str, Enum):
    """QC inspection result for sewing"""
    PASS = "Pass"
    REWORK = "Rework"
    SCRAP = "Scrap"


class AcceptTransferRequest(BaseModel):
    """Request to accept transfer from Cutting/Embroidery"""
    transfer_slip_number: str = Field(..., description="Transfer slip barcode number")
    received_qty: Decimal = Field(..., description="Actual qty received")
    notes: Optional[str] = Field(None, description="Receiving notes")
    
    class Config:
        schema_extra = {
            "example": {
                "transfer_slip_number": "TSLIP-BATCH-001-123",
                "received_qty": 95.00,
                "notes": "All pieces intact"
            }
        }


class ValidateInputRequest(BaseModel):
    """Request to validate material input vs BOM requirements"""
    work_order_id: int = Field(..., description="Work order ID")
    received_qty: Decimal = Field(..., description="Material qty received")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "received_qty": 95.00
            }
        }


class ProcessSewingStepRequest(BaseModel):
    """Request to record sewing process step"""
    work_order_id: int = Field(..., description="Work order ID")
    step_number: int = Field(..., description="1=Assembly, 2=Labeling, 3=Stik")
    qty_processed: Decimal = Field(..., description="Qty completed in this step")
    notes: Optional[str] = Field(None, description="Process notes")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "step_number": 1,
                "qty_processed": 95.00,
                "notes": "Assembly complete - high quality"
            }
        }


class InlineQCRequest(BaseModel):
    """Request to record inline QC inspection result"""
    work_order_id: int = Field(..., description="Work order ID")
    inspector_id: int = Field(..., description="QC inspector user ID")
    pass_qty: Optional[Decimal] = Field(default=0, description="Qty passing QC")
    rework_qty: Optional[Decimal] = Field(default=0, description="Qty needing rework")
    scrap_qty: Optional[Decimal] = Field(default=0, description="Qty rejected/scrap")
    defect_reason: Optional[str] = Field(None, description="Defect description if any")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "inspector_id": 15,
                "pass_qty": 92.00,
                "rework_qty": 3.00,
                "scrap_qty": 0.00,
                "defect_reason": "Loose threads on 3 units"
            }
        }


class SegregationCheckRequest(BaseModel):
    """Request to verify product segregation before transfer"""
    work_order_id: int = Field(..., description="Work order ID")
    destination_dept: str = Field(default="Finishing", description="Destination department")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "destination_dept": "Finishing"
            }
        }


class TransferToFinishingRequest(BaseModel):
    """Request to create transfer from Sewing to Finishing"""
    work_order_id: int = Field(..., description="Work order ID")
    transfer_qty: Decimal = Field(..., description="Quantity to transfer")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "transfer_qty": 92.00
            }
        }


class SewingWorkOrderResponse(BaseModel):
    """Response: Current sewing work order status"""
    id: int
    mo_id: int
    product_id: int
    status: SewingStatus
    input_qty: Decimal
    assembly_qty: Optional[Decimal]
    label_qty: Optional[Decimal]
    stik_qty: Optional[Decimal]
    pass_qty: Optional[Decimal]
    rework_qty: Optional[Decimal]
    scrap_qty: Optional[Decimal]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "mo_id": 1,
                "product_id": 10,
                "status": "Ready Transfer",
                "input_qty": 95.00,
                "assembly_qty": 95.00,
                "label_qty": 95.00,
                "stik_qty": 95.00,
                "pass_qty": 92.00,
                "rework_qty": 3.00,
                "scrap_qty": 0.00,
                "started_at": "2026-01-19T13:00:00",
                "completed_at": "2026-01-19T16:30:00"
            }
        }


class SegregationValidationResponse(BaseModel):
    """Response: Segregation check (destination consistency)"""
    work_order_id: int
    current_destination: Optional[str]
    pending_destination: str
    destinations_match: bool
    segregation_status: str  # "CLEAR" or "ALARM - Destination mismatch"
    requires_jeda: bool
    jeda_duration_minutes: Optional[int]
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "current_destination": "USA",
                "pending_destination": "USA",
                "destinations_match": True,
                "segregation_status": "CLEAR",
                "requires_jeda": False,
                "jeda_duration_minutes": None
            }
        }


class SewingProcessTrack(BaseModel):
    """Track sewing process progress through 3 stages"""
    work_order_id: int
    stage_1_assembly: Optional[datetime] = Field(None, description="Assembly completion time")
    stage_2_labeling: Optional[datetime] = Field(None, description="Labeling completion time")
    stage_3_stik: Optional[datetime] = Field(None, description="Stik completion time")
    qc_result: Optional[SewingQCResult] = None
    transfer_ready: bool = False
    timestamp: datetime
