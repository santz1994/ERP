"""
Finishing Module Models & Schemas
Handles stuffing, closing, QC (metal detector), and conversion to FG code
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FinishingStatus(str, Enum):
    """Finishing work order status"""
    PENDING = "Pending"
    LINE_CLEARANCE_CHECK = "Line Clearance Check"
    STUFFING = "Stuffing"
    CLOSING = "Closing"
    METAL_DETECT = "Metal Detector"
    QC_CHECK = "QC Check"
    CONVERSION = "Conversion to FG"
    READY_PACKING = "Ready for Packing"
    COMPLETED = "Completed"


class AcceptWIPRequest(BaseModel):
    """Request to accept WIP SEW transfer"""
    transfer_slip_number: str = Field(..., description="Transfer slip from Sewing")
    received_qty: Decimal = Field(..., description="Qty received")
    notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "transfer_slip_number": "TSLIP-BATCH-001-456",
                "received_qty": 92.00
            }
        }


class StuffingRequest(BaseModel):
    """Request to perform stuffing operation"""
    work_order_id: int = Field(..., description="Work order ID")
    operator_id: int = Field(..., description="Operator performing stuffing")
    stuffing_material: str = Field(default="Dacron", description="Filling material type")
    qty_stuffed: Decimal = Field(..., description="Qty completed")
    notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "operator_id": 20,
                "stuffing_material": "Dacron",
                "qty_stuffed": 92.00
            }
        }


class ClosingAndGroomingRequest(BaseModel):
    """Request to perform closing and grooming"""
    work_order_id: int = Field(..., description="Work order ID")
    operator_id: int = Field(..., description="Operator")
    qty_closed: Decimal = Field(..., description="Qty with closing completed")
    quality_notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "operator_id": 20,
                "qty_closed": 92.00,
                "quality_notes": "All seams strong, symmetry OK"
            }
        }


class MetalDetectorTestRequest(BaseModel):
    """Request to perform critical metal detector test"""
    work_order_id: int = Field(..., description="Work order ID")
    inspector_id: int = Field(..., description="QC inspector")
    pass_qty: Decimal = Field(..., description="Qty passing metal test")
    fail_qty: Decimal = Field(default=0, description="Qty with metal detected")
    notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "inspector_id": 15,
                "pass_qty": 92.00,
                "fail_qty": 0.00,
                "notes": "All units clear - no metal detected"
            }
        }


class ConversionRequest(BaseModel):
    """Request to convert WIP code to FG (Finish Good) code"""
    work_order_id: int = Field(..., description="Work order ID")
    wip_code: str = Field(..., description="Current WIP code")
    fg_code: str = Field(..., description="Target FG code (IKEA article)")
    qty_converted: Decimal = Field(..., description="Qty converted")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "wip_code": "WIP-FIN-SHARK-001",
                "fg_code": "BLAHAJ-100",
                "qty_converted": 92.00
            }
        }


class FinishingWorkOrderResponse(BaseModel):
    """Response: Current finishing work order status"""
    id: int
    mo_id: int
    wip_product_id: int
    fg_product_id: Optional[int]
    status: FinishingStatus
    input_qty: Decimal
    stuffed_qty: Optional[Decimal]
    closed_qty: Optional[Decimal]
    metal_test_pass: Optional[Decimal]
    metal_test_fail: Optional[Decimal]
    converted_qty: Optional[Decimal]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MetalDetectorAlertResponse(BaseModel):
    """Alert when metal detected in product"""
    work_order_id: int
    unit_index: int
    metal_location: str
    severity: str  # "Critical" or "Warning"
    action: str  # "Reject" or "Investigate"
    timestamp: datetime


class ConversionLogEntry(BaseModel):
    """Log for WIP to FG conversion"""
    work_order_id: int
    wip_code: str
    fg_code: str
    qty_converted: Decimal
    conversion_rate: str
    timestamp: datetime
