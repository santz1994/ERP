"""Production Models - SPK Material Allocation & SPK Editing"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Enum, 
    Numeric, JSON, Boolean, Text, func, Date
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class AllocationStatus(str, enum.Enum):
    """SPK Material Allocation Status"""
    FULLY_ALLOCATED = "FULLY_ALLOCATED"
    PARTIALLY_ALLOCATED = "PARTIALLY_ALLOCATED"
    FAILED = "FAILED"
    SHORTAGE = "SHORTAGE"


class SPKMaterialAllocationStatus(str, enum.Enum):
    """Material Allocation Status"""
    PENDING = "PENDING"
    ALLOCATED = "ALLOCATED"
    DEBT_CREATED = "DEBT_CREATED"
    FAILED = "FAILED"


class SPKEditType(str, enum.Enum):
    """Types of SPK edits"""
    EDIT_QUANTITY = "EDIT_QUANTITY"
    EDIT_DEADLINE = "EDIT_DEADLINE"
    EDIT_NOTES = "EDIT_NOTES"
    EDIT_ARTICLE = "EDIT_ARTICLE"
    EDIT_MULTIPLE = "EDIT_MULTIPLE"


class SPKEditStatus(str, enum.Enum):
    """SPK Edit Status"""
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"
    CANCELLED = "CANCELLED"


# DEPRECATED: Use SPKMaterialAllocation from manufacturing.py instead
# This class kept for backward compatibility only
class SPKMaterialAllocationOLD(Base):
    """Track material allocation for SPK - Feature #1 (DEPRECATED)"""
    __tablename__ = "spk_material_allocation_old"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)  # Foreign key to products table
    qty_allocated = Column(Numeric(10, 2), nullable=False)
    qty_from_stock = Column(Numeric(10, 2), nullable=False, default=0)
    qty_from_debt = Column(Numeric(10, 2), nullable=False, default=0)
    wastage_qty = Column(Numeric(10, 2), nullable=False, default=0)
    wastage_percentage = Column(Numeric(5, 2), nullable=False, default=0)
    allocation_status = Column(Enum(SPKMaterialAllocationStatus), default=SPKMaterialAllocationStatus.PENDING)
    material_shortage = Column(Boolean, default=False)
    shortage_qty = Column(Numeric(10, 2), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SPKMaterialAllocation(spk_id={self.spk_id}, material_id={self.material_id}, qty={self.qty_allocated})>"


class SPKEdit(Base):
    """Track SPK edits with approval workflow - Feature #7"""
    __tablename__ = "spk_edit_history"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id"), nullable=False, index=True)
    edit_type = Column(Enum(SPKEditType), nullable=False)
    status = Column(Enum(SPKEditStatus), default=SPKEditStatus.PENDING_APPROVAL)
    
    # Changes tracking
    old_values = Column(JSON, nullable=False)
    new_values = Column(JSON, nullable=False)
    
    # Requestor info
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    request_reason = Column(Text, nullable=True)
    requested_at = Column(DateTime, server_default=func.now())
    
    # Approval info
    approval_request_id = Column(Integer, nullable=True)  # Link to approval_requests table
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)
    
    # Rejection info
    rejected_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    rejected_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Application info
    applied_at = Column(DateTime, nullable=True)
    applied_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Cancellation info
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Material reallocation (if qty changed)
    material_reallocation_details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<SPKEdit(spk_id={self.spk_id}, type={self.edit_type}, status={self.status})>"
