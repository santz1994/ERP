"""Pydantic schemas for API requests/responses
Data validation and serialization.
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, EmailStr, Field

from app.core.models.users import UserRole  # Import from database models

# ==================== AUTH SCHEMAS ====================

# UserRole enum imported from models.users


class UserCreate(BaseModel):
    """Create user request."""

    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    roles: list[UserRole] = [UserRole.OPERATOR_CUT]


class UserLogin(BaseModel):
    """User login request."""

    username: str = Field(..., min_length=1, max_length=50, description="Username must not be empty")
    password: str = Field(..., min_length=1, description="Password must not be empty")


class TokenResponse(BaseModel):
    """Token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response."""

    id: int
    username: str
    email: str
    full_name: str
    role: str  # Single role as string
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response with tokens and user data."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


# ==================== PRODUCT SCHEMAS ====================

class ProductType(str, Enum):
    """Product type enum."""

    RAW_MATERIAL = "Raw Material"
    WIP = "WIP"
    FINISH_GOOD = "Finish Good"
    SERVICE = "Service"


class UOM(str, Enum):
    """Unit of measurement."""

    PCS = "Pcs"
    METER = "Meter"
    YARD = "Yard"
    KG = "Kg"
    ROLL = "Roll"


class CategoryCreate(BaseModel):
    """Create category request."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class CategoryResponse(BaseModel):
    """Category response."""

    id: int
    name: str
    description: str | None
    created_at: datetime


class ProductCreate(BaseModel):
    """Create product request."""

    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    type: ProductType
    uom: UOM
    category_id: int | None = None
    parent_article_id: int | None = None
    min_stock: Decimal = Field(default=0, decimal_places=2)
    
    # 🆕 PALLET SYSTEM (Added: 2026-02-10)
    pcs_per_carton: int | None = Field(None, gt=0, description="Fixed pieces per carton for Finish Goods")
    cartons_per_pallet: int | None = Field(None, gt=0, description="Fixed cartons per pallet for Finish Goods")


class ProductResponse(BaseModel):
    """Product response."""

    id: int
    code: str
    name: str
    type: ProductType
    uom: UOM
    category_id: int | None
    parent_article_id: int | None
    min_stock: Decimal
    created_at: datetime
    
    # 🆕 PALLET SYSTEM (Added: 2026-02-10)
    pcs_per_carton: int | None = None
    cartons_per_pallet: int | None = None
    pcs_per_pallet: int | None = Field(None, description="Computed: pcs_per_carton × cartons_per_pallet")

    class Config:
        from_attributes = True


# ==================== MANUFACTURING SCHEMAS ====================

class RoutingType(str, Enum):
    """Production route type."""

    ROUTE_1_FULL = "Route 1"  # Full process with embroidery
    ROUTE_2_DIRECT = "Route 2"  # Direct sewing without embroidery
    ROUTE_3_SUBCON = "Route 3"  # Subcon external vendor


class MOStatus(str, Enum):
    """Manufacturing order status."""

    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CANCELLED = "Cancelled"


class ManufacturingOrderCreate(BaseModel):
    """Create manufacturing order request with Dual Trigger System support."""

    so_line_id: int | None = Field(None, description="Sales order line ID (optional)")
    product_id: int = Field(..., description="WIP/FG product ID")
    qty_planned: Decimal = Field(..., gt=0, description="Planned production quantity")
    routing_type: RoutingType = Field(..., description="Production routing (Route 1/2/3)")
    batch_number: str = Field(..., min_length=1, max_length=50, description="Batch number for traceability")
    
    # Dual Trigger System (NEW)
    po_fabric_id: int | None = Field(None, description="PO for fabric materials (TRIGGER 1)")
    po_label_id: int | None = Field(None, description="PO for labels/tags (TRIGGER 2)")
    trigger_mode: str = Field("PARTIAL", description="Production release mode: PARTIAL or RELEASED")
    
    # IKEA Compliance (NEW)
    production_week: str | None = Field(None, description="IKEA week format (e.g., 05-2026)")
    destination_country: str | None = Field(None, description="Shipping destination")
    planned_production_date: date | None = Field(None, description="Planned production start date")
    target_shipment_date: date | None = Field(None, description="Target shipment date")


class ManufacturingOrderResponse(BaseModel):
    """Manufacturing order response with dual trigger info."""

    id: int
    so_line_id: int | None
    product_id: int
    qty_planned: Decimal
    qty_produced: Decimal
    routing_type: RoutingType
    batch_number: str
    state: MOStatus
    
    # Dual Trigger System
    po_fabric_id: int | None = None
    po_label_id: int | None = None
    trigger_mode: str = "PARTIAL"
    
    # IKEA Compliance
    production_week: str | None = None
    destination_country: str | None = None
    planned_production_date: date | None = None
    target_shipment_date: date | None = None
    
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== WAREHOUSE SCHEMAS ====================

class TransferDept(str, Enum):
    """Department enum."""

    CUTTING = "Cutting"
    EMBROIDERY = "Embroidery"
    SEWING = "Sewing"
    FINISHING = "Finishing"
    PACKING = "Packing"
    SUBCON = "Subcon"
    FINISH_GOOD = "Finish Good"


class TransferStatus(str, Enum):
    """Transfer status."""

    INITIATED = "Initiated"
    BLOCKED = "Blocked"
    LOCKED = "Locked"
    ACCEPTED = "Accepted"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class StockTransferCreate(BaseModel):
    """Create stock transfer request."""

    from_dept: TransferDept
    to_dept: TransferDept
    product_id: int
    qty: Decimal = Field(..., gt=0)
    batch_number: str
    reference_doc: str
    lot_id: int | None = None


class StockTransferResponse(BaseModel):
    """Stock transfer response."""

    id: int
    from_dept: TransferDept
    to_dept: TransferDept
    product_id: int
    qty_sent: Decimal
    qty_received: Decimal | None
    status: TransferStatus
    is_line_clear: bool
    timestamp_start: datetime
    timestamp_accept: datetime | None
    timestamp_end: datetime | None

    class Config:
        from_attributes = True


class StockCheckResponse(BaseModel):
    """Stock check response."""

    product_id: int
    location: str
    qty_on_hand: Decimal
    qty_reserved: Decimal
    qty_available: Decimal
    updated_at: datetime


# ==================== QC SCHEMAS ====================

class TestType(str, Enum):
    """QC test type."""

    DROP_TEST = "Drop Test"
    STABILITY_10 = "Stability 10"
    STABILITY_27 = "Stability 27"
    SEAM_STRENGTH = "Seam Strength"


class TestResult(str, Enum):
    """Test result."""

    PASS = "Pass"
    FAIL = "Fail"


class QCTestCreate(BaseModel):
    """Create QC lab test request."""

    batch_number: str
    test_type: TestType
    measured_value: Decimal | None = None
    measured_unit: str | None = None
    iso_standard: str = "ISO 8124"
    test_location: str
    notes: str | None = None


class QCTestResponse(BaseModel):
    """QC test response."""

    id: int
    batch_number: str
    test_type: TestType
    test_result: TestResult
    measured_value: Decimal | None
    measured_unit: str | None
    iso_standard: str
    inspector_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== ERROR SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Error response schema."""

    status_code: int
    message: str
    detail: str | None = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error response."""

    status_code: int = 422
    message: str = "Validation error"
    errors: list[dict]


# ==================== WAREHOUSE SCHEMAS ====================

class StockUpdateCreate(BaseModel):
    """Stock update request - validates types strictly."""

    item_id: int = Field(..., gt=0, description="Product/Item ID must be positive")
    quantity: Decimal = Field(..., gt=0, description="Quantity must be positive")
    operation: str = Field(..., description="Operation type: add or subtract")
    location_id: int = Field(default=1, gt=0, description="Warehouse location ID")
    reason: str = Field(default="Stock adjustment", max_length=255, description="Reason for adjustment")

    class Config:
        from_attributes = True


class MaterialRequestCreate(BaseModel):
    """Create material request - for manual material addition with approval."""

    product_id: int = Field(..., gt=0, description="Product ID")
    location_id: int = Field(..., gt=0, description="Warehouse location ID")
    qty_requested: Decimal = Field(..., gt=0, description="Quantity requested")
    uom: str = Field(..., max_length=10, description="Unit of measure (Pcs, Meter, Kg, Roll)")
    purpose: str = Field(..., max_length=500, description="Purpose/reason for material request")

    class Config:
        from_attributes = True


class MaterialRequestResponse(BaseModel):
    """Material request response."""

    id: int
    product_id: int
    location_id: int
    qty_requested: Decimal
    uom: str
    purpose: str
    status: str
    requested_by_id: int
    requested_at: datetime
    approved_by_id: int | None
    approved_at: datetime | None
    received_by_id: int | None
    received_at: datetime | None

    class Config:
        from_attributes = True


class MaterialRequestApprovalCreate(BaseModel):
    """Approve or reject material request."""

    approved: bool = Field(..., description="True to approve, False to reject")
    rejection_reason: str | None = Field(None, max_length=500, description="Reason if rejecting")

    class Config:
        from_attributes = True


# ==================== BOM SCHEMAS - Session 24 ====================

class BOMVariantCreate(BaseModel):
    """Create BOM variant (alternative material)."""
    
    material_id: int = Field(..., description="Alternative material product ID")
    variant_type: str = Field(default="Alternative", description="Primary, Alternative, Optional")
    sequence: int = Field(default=1, description="Order of preference")
    qty_variance: Decimal | None = Field(None, description="Override quantity if specified")
    qty_variance_percent: Decimal | None = Field(None, description="Or use as percentage modifier")
    weight: Decimal = Field(default=1.0, description="Weight for selection probability")
    preferred_vendor_id: int | None = None
    vendor_lead_time_days: int = Field(default=0)
    cost_variance: Decimal = Field(default=0, description="Cost difference vs primary")
    notes: str | None = Field(None, max_length=500)


class BOMVariantResponse(BaseModel):
    """BOM variant response."""
    
    id: int
    bom_detail_id: int
    material_id: int
    variant_type: str
    sequence: int
    qty_variance: Decimal | None
    qty_variance_percent: Decimal | None
    weight: Decimal
    selection_probability: Decimal
    preferred_vendor_id: int | None
    vendor_lead_time_days: int
    cost_variance: Decimal
    is_active: bool
    approval_status: str
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class BOMDetailCreate(BaseModel):
    """Create BOM detail line."""
    
    component_id: int = Field(..., description="Primary material product ID")
    qty_needed: Decimal = Field(..., description="Quantity per 1 unit output")
    wastage_percent: Decimal = Field(default=0, description="Estimated waste percentage")
    has_variants: bool = Field(default=False, description="Support alternative materials")
    variant_selection_mode: str = Field(default="primary", description="primary, any, weighted")


class BOMDetailResponse(BaseModel):
    """BOM detail response."""
    
    id: int
    bom_header_id: int
    component_id: int
    qty_needed: Decimal
    wastage_percent: Decimal
    has_variants: bool
    variant_selection_mode: str
    variants: list[BOMVariantResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BOMHeaderCreate(BaseModel):
    """Create BOM header."""
    
    product_id: int = Field(..., description="Product that this BOM is for")
    bom_type: str = Field(..., description="Manufacturing or Kit/Phantom")
    qty_output: Decimal = Field(default=1.0, description="Output quantity (usually 1)")
    supports_multi_material: bool = Field(default=False, description="Enable multi-material support")
    revision: str = Field(default="Rev 1.0")


class BOMHeaderResponse(BaseModel):
    """BOM header response."""
    
    id: int
    product_id: int
    bom_type: str
    qty_output: Decimal
    is_active: bool
    revision: str
    supports_multi_material: bool
    default_variant_selection: str
    details: list[BOMDetailResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BOMUpdateMultiMaterial(BaseModel):
    """Update BOM to enable/disable multi-material support."""
    
    supports_multi_material: bool = Field(..., description="Enable or disable variant support")
    default_variant_selection: str = Field(default="primary", description="How to select variant")
    revision_reason: str | None = Field(None, max_length=500, description="Reason for change")
