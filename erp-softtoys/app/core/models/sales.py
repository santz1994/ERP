"""
Sales Order Models
For tracking customer orders from IKEA
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, DECIMAL, Date, func
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class SOStatus(str, enum.Enum):
    """Sales Order Status"""
    DRAFT = "Draft"
    CONFIRMED = "Confirmed"
    PRODUCTION = "Production"
    DONE = "Done"
    CANCELLED = "Cancelled"


class SalesOrder(Base):
    """
    Sales Orders - Orders from IKEA customers
    """
    __tablename__ = "sales_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    po_number_buyer = Column(String(100), unique=True, nullable=False, index=True)  # IKEA PO number
    buyer_id = Column(Integer, ForeignKey("partners.id"), nullable=True)  # Link to IKEA partner
    
    # Order dates
    order_date = Column(Date, nullable=False, index=True)
    delivery_week = Column(Integer, nullable=False)  # e.g., week 22
    
    # Destination
    destination = Column(String(50), nullable=False, index=True)  # Country code (DE, US, JP, etc.)
    
    # Status tracking
    status = Column(Enum(SOStatus), default=SOStatus.DRAFT, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    lines = relationship("SalesOrderLine", back_populates="sales_order", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<SalesOrder(po={self.po_number_buyer}, status={self.status.value})>"


class SalesOrderLine(Base):
    """
    Sales Order Line Items - Individual articles in an order
    """
    __tablename__ = "sales_order_lines"
    
    id = Column(Integer, primary_key=True, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False, index=True)
    
    # Product references
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)  # Finish Good article
    
    # Quantities
    qty_ordered = Column(DECIMAL(10, 2), nullable=False)  # Ordered quantity
    qty_produced = Column(DECIMAL(10, 2), default=0)  # Already produced
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    sales_order = relationship("SalesOrder", back_populates="lines")
    product = relationship("Product")
    
    def __repr__(self):
        return f"<SalesOrderLine(qty={self.qty_ordered})>"
