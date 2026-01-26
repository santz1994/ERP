"""
Database Models for Daily Production Input Tracking
Created: January 26, 2026
Purpose: SQLAlchemy ORM models for new tables

Tables:
- SPKDailyProduction: Daily production entries per SPK
- SPKProductionCompletion: SPK completion milestone
- SPKModification: Audit trail for SPK edits
- MaterialDebt: Negative inventory tracking
- MaterialDebtSettlement: Settlement records for material debt
"""

from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Date, DateTime, Boolean, ForeignKey, CheckConstraint, UniqueConstraint, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# ============================================================================
# MODEL 1: SPKDailyProduction
# ============================================================================
class SPKDailyProduction(Base):
    """
    Track daily production input for each SPK
    - production_date: Which date was this input for?
    - input_qty: How many units produced on this date?
    - cumulative_qty: Total units from day 1 until this date
    - status: DRAFT (being entered) → CONFIRMED (finalized)
    """
    __tablename__ = "spk_daily_production"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id", ondelete="CASCADE"), nullable=False, index=True)
    production_date = Column(Date, nullable=False, index=True)
    input_qty = Column(Integer, default=0, nullable=False)
    cumulative_qty = Column(Integer)  # Running total
    input_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(50), default="DRAFT")  # DRAFT, CONFIRMED, COMPLETED
    notes = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    spk = relationship("SPK", back_populates="daily_production")
    input_by = relationship("User", foreign_keys=[input_by_id])

    # Constraints
    __table_args__ = (
        CheckConstraint('input_qty >= 0', name='ck_daily_prod_qty_positive'),
        UniqueConstraint('spk_id', 'production_date', name='uk_spk_date'),
    )


# ============================================================================
# MODEL 2: SPKProductionCompletion
# ============================================================================
class SPKProductionCompletion(Base):
    """
    Record when SPK production is completed (target qty reached)
    - completed_date: When was target reached?
    - actual_qty: Final production quantity
    - confirmed_by_id: Who confirmed completion?
    - is_completed: Final completion flag
    """
    __tablename__ = "spk_production_completion"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id", ondelete="CASCADE"), nullable=False, index=True)
    target_qty = Column(Integer, nullable=False)
    actual_qty = Column(Integer, nullable=False)
    completed_date = Column(Date, nullable=False, index=True)
    confirmed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmation_notes = Column(String(255))
    confirmed_at = Column(DateTime, nullable=False)
    is_completed = Column(Boolean, default=False)

    # Relationships
    spk = relationship("SPK", back_populates="production_completion")
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_id])


# ============================================================================
# MODEL 3: SPKModification (Audit Trail)
# ============================================================================
class SPKModification(Base):
    """
    Audit trail for all SPK edits
    - field_name: Which field was modified? (qty, start_date, due_date, etc)
    - old_value: Previous value
    - new_value: New value
    - modification_reason: Why was it changed?
    """
    __tablename__ = "spk_modifications"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id", ondelete="CASCADE"), nullable=False, index=True)
    field_name = Column(String(50), nullable=False)  # 'qty', 'start_date', 'allow_negative', etc
    old_value = Column(String(255))
    new_value = Column(String(255))
    modified_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    modification_reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    spk = relationship("SPK", back_populates="modifications")
    modified_by = relationship("User", foreign_keys=[modified_by_id])


# ============================================================================
# MODEL 4: MaterialDebt (Negative Inventory)
# ============================================================================
class MaterialDebt(Base):
    """
    Track material debt when production starts without materials
    - qty_owed: How much material is owed?
    - qty_settled: How much has been received/settled so far?
    - approval_status: Has debt been approved? PENDING → APPROVED → SETTLED
    """
    __tablename__ = "material_debt"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id", ondelete="CASCADE"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("materials.id"), nullable=False)
    qty_owed = Column(Integer, nullable=False)  # Amount owed
    qty_settled = Column(Integer, default=0)    # Amount received
    approval_status = Column(String(50), default="PENDING")  # PENDING, APPROVED, REJECTED, SETTLED
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id"))  # Who approved?
    approved_at = Column(DateTime)
    approval_reason = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    spk = relationship("SPK", back_populates="material_debts")
    material = relationship("Material", foreign_keys=[material_id])
    created_by = relationship("User", foreign_keys=[created_by_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    settlements = relationship("MaterialDebtSettlement", back_populates="material_debt")

    # Constraints
    __table_args__ = (
        CheckConstraint('qty_owed > 0', name='ck_debt_qty_positive'),
        CheckConstraint('qty_settled >= 0', name='ck_settled_qty_positive'),
    )


# ============================================================================
# MODEL 5: MaterialDebtSettlement
# ============================================================================
class MaterialDebtSettlement(Base):
    """
    Record when material arrives to settle debt
    - qty_settled: How much material received in this shipment?
    - settlement_date: When was material received?
    - received_by_id: Who received the material?
    - settled_by_id: Who confirmed the settlement?
    """
    __tablename__ = "material_debt_settlement"

    id = Column(Integer, primary_key=True, index=True)
    material_debt_id = Column(Integer, ForeignKey("material_debt.id", ondelete="CASCADE"), nullable=False, index=True)
    qty_settled = Column(Integer, nullable=False)  # Amount settled in this record
    settlement_date = Column(Date, nullable=False, index=True)
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    settled_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    settlement_notes = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    material_debt = relationship("MaterialDebt", back_populates="settlements")
    received_by = relationship("User", foreign_keys=[received_by_id])
    settled_by = relationship("User", foreign_keys=[settled_by_id])

    # Constraints
    __table_args__ = (
        CheckConstraint('qty_settled > 0', name='ck_settlement_qty_positive'),
    )


# ============================================================================
# ENHANCEMENT: Update existing SPK model
# ============================================================================
# Add these relationships to existing SPK class:
# daily_production = relationship("SPKDailyProduction", back_populates="spk")
# production_completion = relationship("SPKProductionCompletion", back_populates="spk")
# modifications = relationship("SPKModification", back_populates="spk")
# material_debts = relationship("MaterialDebt", back_populates="spk")

# Add these columns to existing SPK class:
# original_qty = Column(Integer, default=0)
# modified_qty = Column(Integer)
# modification_reason = Column(String(255))
# modified_by_id = Column(Integer, ForeignKey("users.id"))
# modified_at = Column(DateTime)
# allow_negative_inventory = Column(Boolean, default=False)
# negative_approval_status = Column(String(50))
# negative_approved_by_id = Column(Integer, ForeignKey("users.id"))
# negative_approved_at = Column(DateTime)
# production_status = Column(String(50), default="NOT_STARTED")
# completion_date = Column(Date)
# daily_progress_start_date = Column(Date)
