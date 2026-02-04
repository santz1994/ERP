"""
Approval Workflow Models
Feature #2: Multi-level Approval System

Tables:
- approval_requests: Main approval request tracking
- approval_steps: Individual step tracking per approval chain

Author: IT Developer Senior
Date: 4 Februari 2026
"""

from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from uuid import uuid4

from app.core.database import Base


class ApprovalRequest(Base):
    """
    Main approval request table
    
    Tracks approval requests for various entities:
    - SPK_CREATE
    - SPK_EDIT_QUANTITY
    - SPK_EDIT_DEADLINE
    - MO_EDIT
    - MATERIAL_DEBT
    - STOCK_ADJUSTMENT
    """
    __tablename__ = "approval_requests"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Entity being approved
    entity_type = Column(String(50), nullable=False, index=True)
    entity_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    
    # Submission details
    submitted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    changes = Column(JSON, nullable=False)  # What's being changed
    reason = Column(Text, nullable=False)  # Why the change
    
    # Approval workflow state
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    # Status values: PENDING, SPV_APPROVED, MANAGER_APPROVED, APPROVED, REJECTED, REVERTED
    
    current_step = Column(Integer, default=0, nullable=False)  # 0=SPV, 1=Manager, 2=Director
    approval_chain = Column(JSON, nullable=False)  # ["SPV", "MANAGER"] or ["SPV", "MANAGER", "DIRECTOR"]
    approvals = Column(JSON)  # Array of approval steps with timestamps
    # Format: [{"step": 0, "approver_id": int, "approved_at": "timestamp", "notes": "text"}, ...]
    
    # Rejection tracking
    rejection_reason = Column(Text)
    rejected_by = Column(Integer, ForeignKey("users.id"))
    rejected_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submitter = relationship("User", foreign_keys=[submitted_by], backref="approval_requests_submitted")
    rejector = relationship("User", foreign_keys=[rejected_by], backref="approval_requests_rejected")
    steps = relationship("ApprovalStep", back_populates="approval_request", cascade="all, delete-orphan")

    # Indexes
    __table_args__ = (
        Index('idx_approval_requests_entity', 'entity_type', 'entity_id'),
        Index('idx_approval_requests_status', 'status'),
        Index('idx_approval_requests_created', 'created_at'),
    )

    def __repr__(self):
        return f"<ApprovalRequest {self.entity_type} {self.entity_id} - {self.status}>"


class ApprovalStep(Base):
    """
    Individual approval step tracking
    
    Each approval request has multiple steps (SPV → Manager → Director)
    This table tracks each step individually for detailed audit trail
    """
    __tablename__ = "approval_steps"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    approval_request_id = Column(PG_UUID(as_uuid=True), ForeignKey("approval_requests.id"), nullable=False, index=True)
    
    # Step details
    step_number = Column(Integer, nullable=False)  # 1=SPV, 2=Manager, 3=Director
    approver_role = Column(String(50), nullable=False)  # SPV, MANAGER, DIRECTOR
    status = Column(String(20), nullable=False, default="PENDING", index=True)
    # Status values: PENDING, APPROVED, REJECTED, SKIPPED
    
    # Approval action
    approved_by = Column(Integer, ForeignKey("users.id"))
    approved_at = Column(DateTime)
    notes = Column(Text)  # Approver can add notes
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    approval_request = relationship("ApprovalRequest", back_populates="steps")
    approver = relationship("User", foreign_keys=[approved_by], backref="approval_steps_approved")

    # Indexes
    __table_args__ = (
        Index('idx_approval_steps_request', 'approval_request_id'),
        Index('idx_approval_steps_status', 'status'),
    )

    def __repr__(self):
        return f"<ApprovalStep {self.step_number} - {self.approver_role} - {self.status}>"
