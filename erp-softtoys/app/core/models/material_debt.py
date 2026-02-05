"""Material Debt Tracking Models - Phase 2C

Tracks negative stock situations (material used before PO received)
Critical for financial risk management and production continuity

Author: IT Developer Expert
Date: 5 February 2026
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    Column,
    Integer,
    String,
    DECIMAL,
    DateTime,
    ForeignKey,
    Enum as SQLEnum,
    TEXT,
    func,
    Boolean,
)
from sqlalchemy.orm import relationship
from enum import Enum

from app.core.database import Base


class MaterialDebtStatus(str, Enum):
    """Material debt lifecycle states"""

    ACTIVE = "ACTIVE"  # Debt currently outstanding
    PARTIAL_PAID = "PARTIAL_PAID"  # Some materials received
    FULLY_PAID = "FULLY_PAID"  # All debt settled
    WRITTEN_OFF = "WRITTEN_OFF"  # Debt cancelled/written off


class MaterialDebt(Base):
    """Tracks material used before stock available (negative stock)

    Business Logic:
    - Created when stock goes negative (production issues material
      before PO received)
    - Tracks total debt quantity and current balance
    - Settles automatically when GRN received
    - Critical for production risk analysis

    Example Scenario:
        1. Stock: 0 YD of IKHR504 fabric
        2. SPK needs 50 YD → Debt created (-50 YD)
        3. PO arrives with 100 YD → Debt settled, Stock = 50 YD
    """

    __tablename__ = "material_debts"

    id = Column(Integer, primary_key=True, index=True)

    # Material tracking
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
        comment="Material in debt",
    )
    uom = Column(
        String(10), nullable=False, comment="Unit: YARD, KG, PCS, etc."
    )

    # Debt quantities
    total_debt_qty = Column(
        DECIMAL(15, 3),
        nullable=False,
        comment="Total debt incurred (absolute value)",
    )
    settled_qty = Column(
        DECIMAL(15, 3),
        default=0,
        nullable=False,
        comment="Quantity already settled",
    )
    balance_qty = Column(
        DECIMAL(15, 3),
        nullable=False,
        comment="Remaining debt (total - settled)",
    )

    # Status tracking
    status = Column(
        SQLEnum(MaterialDebtStatus),
        default=MaterialDebtStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Reference information
    spk_id = Column(
        Integer,
        ForeignKey("work_orders.id"),
        nullable=True,
        comment="SPK that caused debt",
    )
    reference_doc = Column(
        String(100),
        nullable=False,
        comment="SPK number or transaction ref",
    )

    # Financial tracking
    estimated_cost = Column(
        DECIMAL(15, 2),
        nullable=True,
        comment="Estimated material cost (debt × avg price)",
    )
    rush_order_cost = Column(
        DECIMAL(15, 2),
        default=0,
        comment="Additional cost for rush PO",
    )
    total_cost_impact = Column(
        DECIMAL(15, 2),
        nullable=True,
        comment="Total financial impact (estimated + rush)",
    )

    # Risk assessment
    risk_level = Column(
        String(20),
        default="MEDIUM",
        comment="LOW/MEDIUM/HIGH/CRITICAL",
    )
    impact_notes = Column(
        TEXT, nullable=True, comment="Production impact description"
    )

    # Resolution tracking
    created_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="User who recorded debt",
    )
    resolved_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="User who settled debt",
    )
    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When debt fully settled",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    product = relationship("Product", back_populates="material_debts")
    spk = relationship("WorkOrder", foreign_keys=[spk_id])
    created_by = relationship(
        "User", foreign_keys=[created_by_id], backref="debts_created"
    )
    resolved_by = relationship(
        "User", foreign_keys=[resolved_by_id], backref="debts_resolved"
    )
    settlements = relationship(
        "MaterialDebtSettlement",
        back_populates="debt",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return (
            f"<MaterialDebt(product_id={self.product_id}, "
            f"balance={self.balance_qty} {self.uom}, "
            f"status={self.status.value})>"
        )


class MaterialDebtSettlement(Base):
    """Tracks individual debt payments (GRN applications)

    Business Logic:
    - Created each time GRN received for debt material
    - Applies received qty to outstanding debt
    - Maintains audit trail of debt resolution
    - Links PO → GRN → Debt Settlement

    Example:
        Debt: 50 YD
        Settlement 1: PO#123 arrives, 30 YD applied → Balance 20 YD
        Settlement 2: PO#124 arrives, 20 YD applied → Balance 0 YD
    """

    __tablename__ = "material_debt_settlements"

    id = Column(Integer, primary_key=True, index=True)

    # Debt reference
    debt_id = Column(
        Integer,
        ForeignKey("material_debts.id"),
        nullable=False,
        index=True,
        comment="Debt being settled",
    )

    # Settlement details
    settlement_qty = Column(
        DECIMAL(15, 3),
        nullable=False,
        comment="Quantity applied to debt",
    )
    settlement_cost = Column(
        DECIMAL(15, 2),
        nullable=True,
        comment="Actual cost of settled qty",
    )

    # Source tracking
    po_id = Column(
        Integer,
        ForeignKey("purchase_orders.id"),
        nullable=True,
        comment="PO that settled debt",
    )
    po_line_id = Column(
        Integer,
        ForeignKey("purchase_order_lines.id"),
        nullable=True,
        comment="Specific PO line",
    )
    grn_number = Column(
        String(50), nullable=True, comment="GRN reference number"
    )

    # Settlement metadata
    settlement_date = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="When settlement applied",
    )
    settled_by_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="User who processed settlement",
    )
    notes = Column(TEXT, nullable=True, comment="Settlement notes")

    # Auto settlement flag
    auto_settled = Column(
        Boolean,
        default=False,
        comment="True if auto-applied from GRN",
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # Relationships
    debt = relationship("MaterialDebt", back_populates="settlements")
    po = relationship("PurchaseOrder", foreign_keys=[po_id])
    po_line = relationship("PurchaseOrderLine", foreign_keys=[po_line_id])
    settled_by = relationship(
        "User", foreign_keys=[settled_by_id], backref="settlements_made"
    )

    def __repr__(self):
        return (
            f"<MaterialDebtSettlement(debt_id={self.debt_id}, "
            f"qty={self.settlement_qty}, "
            f"po_id={self.po_id})>"
        )
