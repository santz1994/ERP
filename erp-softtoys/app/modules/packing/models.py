"""Packing Module Models & Schemas
Final stage: Sort by destination/week → Package into cartons → Generate shipping marks
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


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
    week_number: int | None = Field(None, description="Delivery week")

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
    notes: str | None = None

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
    barcode: str | None
    carton_label: str
    fg_code: str
    qty: int
    destination: str
    week: int
    po_number: str | None
    batch_number: str
    generated_at: datetime
    qr_code_url: str | None


class PackingWorkOrderResponse(BaseModel):
    """Response: Current packing work order status"""

    id: int
    mo_id: int
    fg_product_id: int
    status: PackingStatus
    input_qty: Decimal
    sorted_qty: Decimal | None
    packaged_qty: Decimal | None
    num_cartons: int | None
    started_at: datetime | None
    completed_at: datetime | None

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
    carton_details: list[ShippingMarkResponse]
