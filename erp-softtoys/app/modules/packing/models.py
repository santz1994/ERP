"""
Packing Module Models & Schemas
Final stage: Sort by destination/week → Package into cartons → Generate shipping marks
"""

from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List
from datetime import datetime
from enum import Enum


class PackingStatus(str, Enum):
    """Packing work order status"""
    PENDING = "Pending"
    READY_TO_PACK = "Ready to Pack"
    SORTING = "Sorting by Destination"
    PACKAGING = "Packaging into Cartons"
    SHIPPING_MARK = "Shipping Mark Generation"
    COMPLETED = "Completed"


class SortByDestinationRequest(BaseModel):
    """Request to sort items by destination/week"""
    work_order_id: int = Field(..., description="FG work order ID")
    qty_sorted: Decimal = Field(..., description="Qty sorted")
    destination: str = Field(..., description="Country destination code (e.g., US, DE, JP)")
    week_number: Optional[int] = Field(None, description="Delivery week")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "qty_sorted": 92.00,
                "destination": "US",
                "week_number": 6
            }
        }


class PackageIntoCartonRequest(BaseModel):
    """Request to package items into cartons"""
    work_order_id: int = Field(..., description="FG work order ID")
    qty_packaged: Decimal = Field(..., description="Qty packed")
    pcs_per_carton: int = Field(..., description="Pieces per carton (typically 12, 24, 36)")
    num_cartons: int = Field(..., description="Number of cartons")
    notes: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "qty_packaged": 92.00,
                "pcs_per_carton": 12,
                "num_cartons": 8,
                "notes": "Extra foam padding added"
            }
        }


class GenerateShippingMarkRequest(BaseModel):
    """Request to generate shipping mark for carton"""
    work_order_id: int = Field(..., description="FG work order ID")
    carton_number: int = Field(..., description="Carton sequence number")
    fg_code: str = Field(..., description="IKEA article code")
    qty_in_carton: int = Field(..., description="Pieces in this carton")
    destination: str = Field(..., description="Destination country")
    week_number: int = Field(..., description="Delivery week")
    
    class Config:
        schema_extra = {
            "example": {
                "work_order_id": 1,
                "carton_number": 1,
                "fg_code": "BLAHAJ-100",
                "qty_in_carton": 12,
                "destination": "US",
                "week_number": 6
            }
        }


class ShippingMarkResponse(BaseModel):
    """Response: Generated shipping mark data"""
    shipping_mark_id: str  # Unique identifier
    barcode: Optional[str]
    carton_label: str
    fg_code: str
    qty: int
    destination: str
    week: int
    po_number: Optional[str]
    batch_number: str
    generated_at: datetime
    qr_code_url: Optional[str]


class PackingWorkOrderResponse(BaseModel):
    """Response: Current packing work order status"""
    id: int
    mo_id: int
    fg_product_id: int
    status: PackingStatus
    input_qty: Decimal
    sorted_qty: Optional[Decimal]
    packaged_qty: Optional[Decimal]
    num_cartons: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CartonManifest(BaseModel):
    """Manifest for shipped cartons"""
    work_order_id: int
    total_cartons: int
    total_pcs: Decimal
    destination: str
    week_number: int
    shipment_date: datetime
    carton_details: List[ShippingMarkResponse]
