"""Pallet System Schemas
Business requirement: Fixed packing specifications to enforce pallet multiples
"""

from datetime import datetime
from pydantic import BaseModel, Field, validator
from typing import Optional


# ============================================================================
# PALLET SPECIFICATIONS
# ============================================================================

class PalletSpecsResponse(BaseModel):
    """Pallet specifications for a product (Finish Good).
    
    Example response:
    {
        "product_id": 1,
        "product_code": "AFTONSPARV",
        "product_name": "AFTONSPARV Bear 30cm",
        "pcs_per_carton": 60,
        "cartons_per_pallet": 8,
        "pcs_per_pallet": 480
    }
    """
    product_id: int
    product_code: str
    product_name: str
    pcs_per_carton: Optional[int] = None
    cartons_per_pallet: Optional[int] = None
    pcs_per_pallet: Optional[int] = Field(None, description="Computed: pcs_per_carton × cartons_per_pallet")

    class Config:
        from_attributes = True


# ============================================================================
# PO PALLET CALCULATION
# ============================================================================

class POPalletCalculationRequest(BaseModel):
    """Request to calculate PO quantities based on pallet target.
    
    Example request:
    {
        "article_id": 1,
        "target_pallets": 5
    }
    
    Returns calculated quantities for validation before PO creation.
    """
    article_id: int = Field(..., description="Article (Finish Good) ID")
    target_pallets: int = Field(..., gt=0, description="Number of pallets to produce")


class POPalletCalculationResponse(BaseModel):
    """Response with calculated PO quantities.
    
    Example response:
    {
        "article_id": 1,
        "article_code": "AFTONSPARV",
        "target_pallets": 5,
        "expected_cartons": 40,
        "calculated_pcs": 2400,
        "pallet_specs": {...}
    }
    """
    article_id: int
    article_code: str
    article_name: str
    target_pallets: int
    expected_cartons: int = Field(..., description="target_pallets × cartons_per_pallet")
    calculated_pcs: int = Field(..., description="target_pallets × pcs_per_pallet")
    pallet_specs: PalletSpecsResponse


# ============================================================================
# PO PALLET VALIDATION
# ============================================================================

class POPalletValidationRequest(BaseModel):
    """Request to validate if PO quantity is pallet multiple.
    
    Example request:
    {
        "article_id": 1,
        "quantity_pcs": 2400
    }
    
    Returns validation result with recommendations.
    """
    article_id: int = Field(..., description="Article (Finish Good) ID")
    quantity_pcs: int = Field(..., gt=0, description="Proposed PO quantity in pieces")


class POPalletValidationResponse(BaseModel):
    """Response with validation result.
    
    Example response (valid):
    {
        "is_valid": true,
        "is_pallet_multiple": true,
        "quantity_pcs": 2400,
        "pallets": 5,
        "cartons": 40,
        "remainder_pcs": 0,
        "message": "✅ Valid pallet multiple",
        "recommendation": null
    }
    
    Example response (invalid):
    {
        "is_valid": false,
        "is_pallet_multiple": false,
        "quantity_pcs": 2500,
        "pallets": 5,
        "cartons": 41,
        "remainder_pcs": 100,
        "message": "⚠️ Not a complete pallet multiple",
        "recommendation": "Adjust to 2400 pcs (5 pallets) or 2880 pcs (6 pallets)"
    }
    """
    is_valid: bool
    is_pallet_multiple: bool
    quantity_pcs: int
    pallets: int = Field(..., description="Number of complete pallets")
    cartons: int = Field(..., description="Total cartons (including partial)")
    remainder_pcs: int = Field(..., description="Pieces left after forming complete pallets")
    message: str
    recommendation: Optional[str] = None
    pallet_specs: PalletSpecsResponse


# ============================================================================
# PACKING PALLET TRACKING
# ============================================================================

class PackingPalletUpdateRequest(BaseModel):
    """Request to update packing progress with pallet tracking.
    
    Example request:
    {
        "work_order_id": 123,
        "cartons_packed": 40,
        "validate_complete_pallets": true
    }
    
    System auto-calculates pallets_formed and validates.
    """
    work_order_id: int
    cartons_packed: int = Field(..., ge=0, description="Number of cartons packed")
    validate_complete_pallets: bool = Field(
        True,
        description="If True, system blocks partial pallets"
    )


class PackingPalletUpdateResponse(BaseModel):
    """Response after updating packing progress.
    
    Example response (valid):
    {
        "work_order_id": 123,
        "cartons_packed": 40,
        "pallets_formed": 5,
        "packing_validated": true,
        "message": "✅ Packed 40 cartons → 5 complete pallets"
    }
    
    Example response (invalid):
    {
        "work_order_id": 123,
        "cartons_packed": 41,
        "pallets_formed": 5,
        "packing_validated": false,
        "message": "⚠️ Partial pallet detected: 41 cartons = 5 pallets + 1 carton loose",
        "error": "Cannot form complete pallets. Expected multiple of 8 cartons."
    }
    """
    work_order_id: int
    cartons_packed: int
    pallets_formed: int
    packing_validated: bool
    message: str
    error: Optional[str] = None


# ============================================================================
# FG WAREHOUSE PALLET RECEIVING
# ============================================================================

class FGPalletReceiveRequest(BaseModel):
    """Request to receive pallet in FG warehouse.
    
    Example request:
    {
        "pallet_barcode": "PLT-2026-00001",
        "location_id": 5,
        "received_by_user_id": 10
    }
    
    System validates pallet content before receiving.
    """
    pallet_barcode: str = Field(..., min_length=5, max_length=50,
                                description="Pallet barcode (e.g., PLT-2026-00001)")
    location_id: int = Field(..., description="FG warehouse location ID")
    received_by_user_id: Optional[int] = Field(None, description="User ID who received pallet")


class FGPalletReceiveResponse(BaseModel):
    """Response after receiving pallet.
    
    Example response:
    {
        "pallet_barcode": "PLT-2026-00001",
        "status": "RECEIVED",
        "product_code": "AFTONSPARV",
        "product_name": "AFTONSPARV Bear 30cm",
        "carton_count": 8,
        "total_pcs": 480,
        "location_name": "FG Warehouse Zone A",
        "received_at": "2026-02-10T14:30:00+07:00",
        "message": "✅ Received 1 pallet (8 cartons / 480 pcs)"
    }
    """
    pallet_barcode: str
    status: str
    product_code: str
    product_name: str
    carton_count: int
    total_pcs: int
    location_name: str
    received_at: datetime
    message: str


# ============================================================================
# FG STOCK DISPLAY (PALLET/CARTON/PCS FORMAT)
# ============================================================================

class FGStockPalletDisplay(BaseModel):
    """FG stock displayed in "PLT / CTN / PCS" format.
    
    Example response:
    {
        "product_id": 1,
        "product_code": "AFTONSPARV",
        "product_name": "AFTONSPARV Bear 30cm",
        "location_id": 5,
        "location_name": "FG Warehouse Zone A",
        "total_pcs": 2460,
        "pallets": 5,
        "remaining_cartons": 1,
        "loose_pcs": 0,
        "display_format": "5 PLT / 1 CTN / 0 PCS"
    }
    
    Breakdown:
    - 2460 pcs total
    - 2460 ÷ 480 (pcs/pallet) = 5 pallets + 60 pcs remainder
    - 60 pcs ÷ 60 (pcs/carton) = 1 carton + 0 loose pcs
    - Display: "5 PLT / 1 CTN / 0 PCS"
    """
    product_id: int
    product_code: str
    product_name: str
    location_id: int
    location_name: str
    total_pcs: int
    pallets: int = Field(..., description="Number of complete pallets")
    remaining_cartons: int = Field(..., description="Cartons after forming complete pallets")
    loose_pcs: int = Field(..., description="Loose pieces after forming complete cartons")
    display_format: str = Field(..., description="Formatted as 'X PLT / Y CTN / Z PCS'")

    class Config:
        from_attributes = True


# ============================================================================
# PALLET BARCODE MANAGEMENT
# ============================================================================

class PalletBarcodeCreate(BaseModel):
    """Create new pallet barcode after packing.
    
    Example request:
    {
        "product_id": 1,
        "work_order_id": 123,
        "carton_count": 8,
        "total_pcs": 480
    }
    
    System auto-generates barcode and validates content.
    """
    product_id: int
    work_order_id: Optional[int] = None
    carton_count: int = Field(..., gt=0, description="Number of cartons on pallet")
    total_pcs: int = Field(..., gt=0, description="Total pieces on pallet")

    @validator('total_pcs')
    def validate_pallet_content(cls, v, values):
        """Validate total_pcs matches carton_count × pcs_per_carton.
        Note: Full validation requires product lookup in service layer.
        """
        if v <= 0:
            raise ValueError("total_pcs must be positive")
        return v


class PalletBarcodeResponse(BaseModel):
    """Pallet barcode detail response.
    
    Example response:
    {
        "id": 1,
        "barcode": "PLT-2026-00001",
        "product_id": 1,
        "product_code": "AFTONSPARV",
        "product_name": "AFTONSPARV Bear 30cm",
        "work_order_id": 123,
        "carton_count": 8,
        "total_pcs": 480,
        "status": "PACKED",
        "location_id": null,
        "created_at": "2026-02-10T10:00:00+07:00",
        "received_at": null,
        "shipped_at": null
    }
    """
    id: int
    barcode: str
    product_id: int
    product_code: str
    product_name: str
    work_order_id: Optional[int]
    carton_count: int
    total_pcs: int
    status: str
    location_id: Optional[int]
    location_name: Optional[str]
    created_at: datetime
    received_at: Optional[datetime]
    shipped_at: Optional[datetime]

    class Config:
        from_attributes = True
