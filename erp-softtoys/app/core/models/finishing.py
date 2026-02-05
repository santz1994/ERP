"""Warehouse Finishing 2-Stage Models - Phase 2A

Models for tracking the two-stage finishing process:
1. Stage 1: Stuffing (Skin → Stuffed Body)
2. Stage 2: Closing (Stuffed Body → Finished Doll)

Author: IT Developer Expert
Date: 5 February 2026
"""

from decimal import Decimal
from datetime import datetime, date
from enum import Enum
from sqlalchemy import (
    DECIMAL,
    Column,
    DateTime,
    Integer,
    ForeignKey,
    Date,
    String,
    TEXT,
    Boolean,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class FinishingStage(int, Enum):
    """Finishing production stages"""

    STAGE_1_STUFFING = 1  # Input: Skin, Output: Stuffed Body
    STAGE_2_CLOSING = 2  # Input: Stuffed Body, Output: Finished Doll


class WarehouseFinishingStock(Base):
    """Warehouse Finishing Stock
    
    Tracks inventory at each finishing stage (Stuffing or Closing)
    Maintains good and defective quantities separately
    """

    __tablename__ = "warehouse_finishing_stocks"

    id = Column(Integer, primary_key=True, index=True)
    stage = Column(
        Integer,
        nullable=False,
        index=True,
        comment="1=Stuffing, 2=Closing"
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
        comment="WIP Product: Skin, Stuffed Body, or Finished Doll"
    )

    # Quantity tracking
    good_qty = Column(
        DECIMAL(10, 2),
        default=0,
        nullable=False,
        comment="Good pieces in stock"
    )
    defect_qty = Column(
        DECIMAL(10, 2),
        default=0,
        nullable=False,
        comment="Defective pieces in stock"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])

    @property
    def total_qty(self) -> Decimal:
        """Total quantity (good + defect)"""
        return self.good_qty + self.defect_qty

    def __repr__(self):
        return f"<WarehouseFinishingStock(stage={self.stage}, product_id={self.product_id}, total={self.total_qty})>"


class FinishingMaterialConsumption(Base):
    """Finishing Material Consumption
    
    Tracks material consumption during finishing:
    - Stage 1: Filling (kapas) consumption
    - Stage 2: Thread consumption
    """

    __tablename__ = "finishing_material_consumptions"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(
        Integer,
        ForeignKey("spks.id"),
        nullable=False,
        index=True,
        comment="Link to Finishing SPK"
    )
    stage = Column(
        Integer,
        nullable=False,
        index=True,
        comment="1=Stuffing, 2=Closing"
    )
    material_id = Column(
        Integer,
        ForeignKey("products.id"),
        nullable=False,
        index=True,
        comment="Material consumed (filling, thread, etc)"
    )

    # Quantities
    qty_planned = Column(
        DECIMAL(12, 3),
        nullable=False,
        comment="Planned consumption from BOM"
    )
    qty_actual = Column(
        DECIMAL(12, 3),
        nullable=True,
        comment="Actual consumption (operator input)"
    )

    # Unit of Measure
    uom = Column(
        String(10),
        nullable=False,
        default="KG",
        comment="KG, METER, GRAM, PCS"
    )

    # Lot tracking
    lot_id = Column(
        Integer,
        ForeignKey("stock_lots.id"),
        nullable=True,
        comment="Which batch/roll used"
    )

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    spk = relationship("SPK", foreign_keys=[spk_id])
    material = relationship("Product", foreign_keys=[material_id])
    lot = relationship("StockLot", foreign_keys=[lot_id])

    def __repr__(self):
        return f"<FinishingMaterialConsumption(spk_id={self.spk_id}, stage={self.stage}, qty_planned={self.qty_planned})>"


class FinishingInputOutput(Base):
    """Finishing Daily Input/Output
    
    Records daily input and output for each finishing stage
    Tracks yield rate, defects, and rework
    """

    __tablename__ = "finishing_inputs_outputs"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(
        Integer,
        ForeignKey("spks.id"),
        nullable=False,
        index=True,
        comment="Link to Finishing SPK"
    )
    stage = Column(
        Integer,
        nullable=False,
        index=True,
        comment="1=Stuffing, 2=Closing"
    )
    production_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="Production date"
    )

    # Daily tracking
    input_qty = Column(
        DECIMAL(10, 2),
        nullable=False,
        comment="Pieces received for processing"
    )
    good_qty = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0,
        comment="Good output produced"
    )
    defect_qty = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0,
        comment="Defective output"
    )
    rework_qty = Column(
        DECIMAL(10, 2),
        nullable=False,
        default=0,
        comment="Units sent to rework"
    )

    # Metrics
    yield_rate = Column(
        DECIMAL(5, 2),
        nullable=True,
        comment="% of good output (good_qty / input_qty * 100)"
    )

    # Operator
    operator_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        comment="Operator who performed the work"
    )

    # Notes
    notes = Column(TEXT, nullable=True, comment="Quality issues, problems")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    spk = relationship("SPK", foreign_keys=[spk_id])
    operator = relationship("User", foreign_keys=[operator_id])

    @property
    def produced_qty(self) -> Decimal:
        """Total produced (good + defect)"""
        return self.good_qty + self.defect_qty

    @property
    def loss_qty(self) -> Decimal:
        """Loss quantity (input - produced)"""
        return self.input_qty - self.produced_qty

    def __repr__(self):
        return f"<FinishingInputOutput(spk_id={self.spk_id}, stage={self.stage}, yield={self.yield_rate}%)>"
