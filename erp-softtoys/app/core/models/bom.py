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


class BOMHeader(Base):
    """BOM Header Table
    Gap Fix: Added revision_date, revised_by, revision_reason for audit trail.
    """

    __tablename__ = "bom_headers"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    bom_type = Column(Enum(BOMType), nullable=False)  # Manufacturing, Kit/Phantom
    qty_output = Column(DECIMAL(10, 2), default=1.0)  # Usually 1.0 for 1 Pcs
    is_active = Column(Boolean, default=True, index=True)
    revision = Column(String(10), default="Rev 1.0")

    # NEW: Audit Trail (Gap Fix #4)
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
        return f"<BOMHeader(product_id={self.product_id}, revision={self.revision})>"


class BOMDetail(Base):
    """BOM Detail Table - Line items for each BOM."""

    __tablename__ = "bom_details"

    id = Column(Integer, primary_key=True, index=True)
    bom_header_id = Column(Integer, ForeignKey("bom_headers.id"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Material/WIP
    qty_needed = Column(DECIMAL(10, 2), nullable=False)  # Quantity per 1 unit output
    wastage_percent = Column(DECIMAL(5, 2), default=0)  # Estimated waste (e.g., 5%)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    header = relationship("BOMHeader", back_populates="details")
    component = relationship("Product", foreign_keys=[component_id])

    def __repr__(self):
        return f"<BOMDetail(component_id={self.component_id}, qty_needed={self.qty_needed})>"
