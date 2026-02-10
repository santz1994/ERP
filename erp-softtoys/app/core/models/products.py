"""Products & Category Models."""

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


class ProductType(str, enum.Enum):
    """Product types as per Database Scheme."""

    RAW_MATERIAL = "Raw Material"
    WIP = "WIP"
    FINISH_GOOD = "Finish Good"
    SERVICE = "Service"


class UOM(str, enum.Enum):
    """Unit of Measurement."""

    PCS = "Pcs"
    METER = "Meter"
    YARD = "Yard"
    KG = "Kg"
    ROLL = "Roll"
    CM = "Cm"


class PartnerType(str, enum.Enum):
    """Partner types."""

    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    SUBCON = "Subcon"


class Partner(Base):
    """Partners - Customers, Suppliers, Subcontractors."""

    __tablename__ = "partners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(PartnerType), nullable=False)
    address = Column(TEXT, nullable=True)
    contact_person = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Partner(name={self.name}, type={self.type.value})>"


class Category(Base):
    """Product Categories."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(TEXT, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    products = relationship("Product", back_populates="category")


class Product(Base):
    """Master Product Table
    Gap Fix: Added parent_article_id for parent-child relationship.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    type = Column(Enum(ProductType), nullable=False, index=True)  # Raw Material, WIP, Finish Good, Service
    uom = Column(Enum(UOM), nullable=False)  # Satuan: Pcs, Meter, Yard, Kg, Roll, cm
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)

    # NEW: Parent-Child Article Relationship (Gap Fix #1)
    parent_article_id = Column(Integer, ForeignKey("products.id"), nullable=True)

    # Stock Management
    min_stock = Column(DECIMAL(10, 2), default=0)  # Safety Stock

    # 🆕 PALLET SYSTEM (Added: 2026-02-10)
    # Fixed packing specifications for Finish Goods
    pcs_per_carton = Column(
        Integer,
        nullable=True,
        comment="Fixed pieces per carton (e.g., 60 for AFTONSPARV). NULL for non-FG."
    )
    cartons_per_pallet = Column(
        Integer,
        nullable=True,
        comment="Fixed cartons per pallet (typically 8). NULL for non-FG."
    )
    # NOTE: pcs_per_pallet is computed in database as GENERATED column
    # Access via: product.pcs_per_carton * product.cartons_per_pallet

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    category = relationship("Category", back_populates="products")
    parent_article = relationship("Product", remote_side=[id], backref="child_articles")

    bom_headers = relationship("BOMHeader", back_populates="product")
    stock_quants = relationship("StockQuant", back_populates="product")
    stock_moves_from = relationship("StockMove", foreign_keys="StockMove.product_id", back_populates="product")
    work_orders = relationship("WorkOrder", foreign_keys="WorkOrder.product_id", back_populates="product")
    manufacturing_orders = relationship("ManufacturingOrder", back_populates="product")

    @property
    def pcs_per_pallet(self) -> int:
        """Computed: pieces per pallet (pcs_per_carton × cartons_per_pallet).
        Returns 0 if either field is None.
        """
        if self.pcs_per_carton and self.cartons_per_pallet:
            return self.pcs_per_carton * self.cartons_per_pallet
        return 0

    def __repr__(self):
        return f"<Product(code={self.code}, type={self.type.value})>"
