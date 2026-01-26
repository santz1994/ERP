"""BOM (Bill of Materials) Models."""

import enum

from sqlalchemy import (
    DECIMAL,
    TEXT,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class BOMType(str, enum.Enum):
    """BOM types."""

    MANUFACTURING = "Manufacturing"
    KIT_PHANTOM = "Kit/Phantom"


class BOMVariantType(str, enum.Enum):
    """Material variant types - for multi-material support."""
    
    PRIMARY = "Primary"
    ALTERNATIVE = "Alternative"
    OPTIONAL = "Optional"


class BOMHeader(Base):
    """BOM Header Table
    Gap Fix: Added revision_date, revised_by, revision_reason for audit trail.
    Session 24: Added support for multi-material components with variants.
    """

    __tablename__ = "bom_headers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    bom_type = Column(Enum(BOMType), nullable=False)  # Manufacturing, Kit/Phantom
    qty_output = Column(DECIMAL(10, 2), default=1.0)  # Usually 1.0 for 1 Pcs
    is_active = Column(Boolean, default=True, index=True)
    revision = Column(String(10), default="Rev 1.0")

    # NEW: Multi-material support tracking
    supports_multi_material = Column(Boolean, default=False)  # Enable variant support
    default_variant_selection = Column(String(100), default="primary")  # How to select variant

    # Audit Trail
    revision_date = Column(DateTime(timezone=True), server_default=func.now())
    revised_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    revision_reason = Column(TEXT, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="bom_headers")
    details = relationship("BOMDetail", back_populates="header", cascade="all, delete-orphan")
    revised_by_user = relationship("User", foreign_keys=[revised_by])

    def __repr__(self):
        return f"<BOMHeader(product_id={self.product_id}, revision={self.revision}, multi_material={self.supports_multi_material})>"


class BOMDetail(Base):
    """BOM Detail Table - Line items for each BOM.
    
    Session 24: Supports single or multiple materials per line via MaterialVariants.
    """

    __tablename__ = "bom_details"

    id = Column(Integer, primary_key=True, index=True)
    bom_header_id = Column(Integer, ForeignKey("bom_headers.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Primary material/WIP
    qty_needed = Column(DECIMAL(10, 2), nullable=False)  # Quantity per 1 unit output
    wastage_percent = Column(DECIMAL(5, 2), default=0)  # Estimated waste (e.g., 5%)
    
    # NEW: Multi-material support
    has_variants = Column(Boolean, default=False)  # This line has alternative materials
    variant_selection_mode = Column(String(50), default="primary")  # primary, any, weighted

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    header = relationship("BOMHeader", back_populates="details")
    component = relationship("Product", foreign_keys=[component_id])
    variants = relationship("BOMVariant", back_populates="detail", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<BOMDetail(component_id={self.component_id}, qty_needed={self.qty_needed}, has_variants={self.has_variants})>"


class BOMVariant(Base):
    """BOM Variant Table - Session 24 NEW
    
    Supports multiple material options per BOM detail line.
    Enables:
    - Alternative materials (e.g., different suppliers)
    - Quantity adjustments (e.g., 100pcs vs 50pcs of alternative)
    - Weighted selection for smart procurement
    """

    __tablename__ = "bom_variants"

    id = Column(Integer, primary_key=True, index=True)
    bom_detail_id = Column(Integer, ForeignKey("bom_details.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Variant classification
    variant_type = Column(Enum(BOMVariantType), default=BOMVariantType.PRIMARY)
    sequence = Column(Integer, default=1)  # Order of preference
    
    # Quantity override
    qty_variance = Column(DECIMAL(10, 2), nullable=True)  # Override qty_needed if specified
    qty_variance_percent = Column(DECIMAL(5, 2), nullable=True)  # Or use as percentage modifier
    
    # Selection weighting
    weight = Column(DECIMAL(5, 2), default=1.0)  # For weighted random selection
    selection_probability = Column(DECIMAL(5, 2), default=0)  # Calculated: 0-100%
    
    # Supplier/vendor info
    preferred_vendor_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Vendor reference
    vendor_lead_time_days = Column(Integer, default=0)
    cost_variance = Column(DECIMAL(10, 2), default=0)  # Cost difference vs primary
    
    # Status
    is_active = Column(Boolean, default=True)
    approval_status = Column(String(50), default="pending")  # pending, approved, rejected
    
    notes = Column(TEXT, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    detail = relationship("BOMDetail", back_populates="variants")
    material = relationship("Product", foreign_keys=[material_id])
    preferred_vendor = relationship("User", foreign_keys=[preferred_vendor_id])

    def __repr__(self):
        return f"<BOMVariant(material_id={self.material_id}, type={self.variant_type}, sequence={self.sequence})>"
