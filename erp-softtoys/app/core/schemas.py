"""
Pydantic schemas for API requests/responses
Data validation and serialization
"""

from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum
from app.core.models.users import UserRole  # Import from database models


# ==================== AUTH SCHEMAS ====================

# UserRole enum imported from models.users


class UserCreate(BaseModel):
    """Create user request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1, max_length=100)
    roles: List[UserRole] = [UserRole.OPERATOR_CUT]


class UserLogin(BaseModel):
    """User login request"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    """User response"""
    id: int
    username: str
    email: str
    full_name: str
    roles: List[UserRole]
    is_active: bool
    created_at: datetime


# ==================== PRODUCT SCHEMAS ====================

class ProductType(str, Enum):
    """Product type enum"""
    RAW_MATERIAL = "Raw Material"
    WIP = "WIP"
    FINISH_GOOD = "Finish Good"
    SERVICE = "Service"


class UOM(str, Enum):
    """Unit of measurement"""
    PCS = "Pcs"
    METER = "Meter"
    YARD = "Yard"
    KG = "Kg"
    ROLL = "Roll"


class CategoryCreate(BaseModel):
    """Create category request"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    """Category response"""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime


class ProductCreate(BaseModel):
    """Create product request"""
    code: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    type: ProductType
    uom: UOM
    category_id: Optional[int] = None
    parent_article_id: Optional[int] = None
    min_stock: Decimal = Field(default=0, decimal_places=2)


class ProductResponse(BaseModel):
    """Product response"""
    id: int
    code: str
    name: str
    type: ProductType
    uom: UOM
    category_id: Optional[int]
    parent_article_id: Optional[int]
    min_stock: Decimal
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== MANUFACTURING SCHEMAS ====================

class RoutingType(str, Enum):
    """Production route type"""
    ROUTE_1_FULL = "Route 1"  # Full process with embroidery
    ROUTE_2_DIRECT = "Route 2"  # Direct sewing without embroidery
    ROUTE_3_SUBCON = "Route 3"  # Subcon external vendor


class MOStatus(str, Enum):
    """Manufacturing order status"""
    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CANCELLED = "Cancelled"


class ManufacturingOrderCreate(BaseModel):
    """Create manufacturing order request"""
    so_line_id: int = Field(..., description="Sales order line ID")
    product_id: int = Field(..., description="WIP/FG product ID")
    qty_planned: Decimal = Field(..., gt=0)
    routing_type: RoutingType
    batch_number: str = Field(..., min_length=1, max_length=50)


class ManufacturingOrderResponse(BaseModel):
    """Manufacturing order response"""
    id: int
    so_line_id: int
    product_id: int
    qty_planned: Decimal
    qty_produced: Decimal
    routing_type: RoutingType
    batch_number: str
    state: MOStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== WAREHOUSE SCHEMAS ====================

class TransferDept(str, Enum):
    """Department enum"""
    CUTTING = "Cutting"
    EMBROIDERY = "Embroidery"
    SEWING = "Sewing"
    FINISHING = "Finishing"
    PACKING = "Packing"
    SUBCON = "Subcon"
    FINISH_GOOD = "Finish Good"


class TransferStatus(str, Enum):
    """Transfer status"""
    INITIATED = "Initiated"
    BLOCKED = "Blocked"
    LOCKED = "Locked"
    ACCEPTED = "Accepted"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class StockTransferCreate(BaseModel):
    """Create stock transfer request"""
    from_dept: TransferDept
    to_dept: TransferDept
    product_id: int
    qty: Decimal = Field(..., gt=0)
    batch_number: str
    reference_doc: str
    lot_id: Optional[int] = None


class StockTransferResponse(BaseModel):
    """Stock transfer response"""
    id: int
    from_dept: TransferDept
    to_dept: TransferDept
    product_id: int
    qty_sent: Decimal
    qty_received: Optional[Decimal]
    status: TransferStatus
    is_line_clear: bool
    timestamp_start: datetime
    timestamp_accept: Optional[datetime]
    timestamp_end: Optional[datetime]
    
    class Config:
        from_attributes = True


class StockCheckResponse(BaseModel):
    """Stock check response"""
    product_id: int
    location: str
    qty_on_hand: Decimal
    qty_reserved: Decimal
    qty_available: Decimal
    updated_at: datetime


# ==================== QC SCHEMAS ====================

class TestType(str, Enum):
    """QC test type"""
    DROP_TEST = "Drop Test"
    STABILITY_10 = "Stability 10"
    STABILITY_27 = "Stability 27"
    SEAM_STRENGTH = "Seam Strength"


class TestResult(str, Enum):
    """Test result"""
    PASS = "Pass"
    FAIL = "Fail"


class QCTestCreate(BaseModel):
    """Create QC lab test request"""
    batch_number: str
    test_type: TestType
    measured_value: Optional[Decimal] = None
    measured_unit: Optional[str] = None
    iso_standard: str = "ISO 8124"
    test_location: str
    notes: Optional[str] = None


class QCTestResponse(BaseModel):
    """QC test response"""
    id: int
    batch_number: str
    test_type: TestType
    test_result: TestResult
    measured_value: Optional[Decimal]
    measured_unit: Optional[str]
    iso_standard: str
    inspector_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# ==================== ERROR SCHEMAS ====================

class ErrorResponse(BaseModel):
    """Error response schema"""
    status_code: int
    message: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ValidationError(BaseModel):
    """Validation error response"""
    status_code: int = 422
    message: str = "Validation error"
    errors: List[dict]
