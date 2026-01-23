"""Cutting Module Models & Schemas
Handles SPK execution, material allocation, and output tracking
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class CuttingStatus(str, Enum):
    """Cutting work order status"""

    PENDING = "Pending"
    SPREADING = "Spreading"
    CUTTING = "Cutting"
    QC_CHECK = "QC Check"
    SHORTAGE_HANDLING = "Shortage Handling"
    SURPLUS_HANDLING = "Surplus Handling"
    READY_TRANSFER = "Ready Transfer"
    COMPLETED = "Completed"


class MaterialIssueRequest(BaseModel):
    """Request to issue material from warehouse to cutting line"""

    work_order_id: int = Field(..., description="Work order ID")
    product_id: int = Field(..., description="Material product ID")
    qty_requested: Decimal = Field(..., description="Quantity to withdraw")

    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "product_id": 5,
                "qty_requested": 100.00
            }
        }


class StartCuttingRequest(BaseModel):
    """Request to start cutting operation"""

    work_order_id: int = Field(..., description="Work order ID")
    operator_id: int = Field(..., description="Operator performing cut")

    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "operator_id": 10
            }
        }


class CompleteCuttingRequest(BaseModel):
    """Request to complete cutting and record output"""

    work_order_id: int = Field(..., description="Work order ID")
    actual_output: Decimal = Field(..., description="Actual pieces cut")
    reject_qty: Decimal = Field(default=0, description="Defective pieces")
    notes: str | None = Field(None, description="Additional notes")

    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "actual_output": 95.00,
                "reject_qty": 5.00,
                "notes": "Normal waste"
            }
        }


class ShortageHandlingRequest(BaseModel):
    """Request additional material due to shortage"""

    work_order_id: int = Field(..., description="Work order ID")
    shortage_qty: Decimal = Field(..., description="Additional qty needed")
    reason: str = Field(..., description="Reason for shortage")

    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "shortage_qty": 10.00,
                "reason": "Material damage during spreading"
            }
        }


class LineTransferRequest(BaseModel):
    """Request to transfer cutting output to sewing/embroidery"""

    work_order_id: int = Field(..., description="Work order ID")
    destination_dept: str = Field(..., description="Destination: Sewing or Embroidery")
    transfer_qty: Decimal = Field(..., description="Quantity to transfer")

    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "destination_dept": "Sewing",
                "transfer_qty": 95.00
            }
        }


class CuttingWorkOrderResponse(BaseModel):
    """Response: Current cutting work order status"""

    id: int
    mo_id: int
    product_id: int
    status: CuttingStatus
    input_qty: Decimal
    output_qty: Decimal | None
    reject_qty: Decimal
    started_at: datetime | None
    completed_at: datetime | None

    class Config:
        from_attributes = True
        schema_extra = {
            "example": {
                "id": 1,
                "mo_id": 1,
                "product_id": 5,
                "status": "Ready Transfer",
                "input_qty": 100.00,
                "output_qty": 95.00,
                "reject_qty": 5.00,
                "started_at": "2026-01-19T10:00:00",
                "completed_at": "2026-01-19T12:30:00"
            }
        }


class MaterialShortageAlert(BaseModel):
    """Alert when material shortage detected"""

    work_order_id: int
    product_id: int
    target_qty: Decimal
    actual_available: Decimal
    shortage_qty: Decimal
    timestamp: datetime


class SurplusHandlingLog(BaseModel):
    """Log for surplus material handling"""

    work_order_id: int
    surplus_qty: Decimal
    action: str  # "Auto-revise SPK" or "Hold for next batch"
    affected_orders: list[int]  # SPK orders affected by revision
    timestamp: datetime


class LineClearanceCheckResponse(BaseModel):
    """Response: Line clearance status check"""

    work_order_id: int
    destination_dept: str
    current_line_status: str  # "Clear", "Occupied", "Paused"
    last_article: str | None
    can_transfer: bool
    blocking_reason: str | None

    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "destination_dept": "Sewing",
                "current_line_status": "Clear",
                "last_article": "WIP-SEW-PREV-123",
                "can_transfer": True,
                "blocking_reason": None
            }
        }
