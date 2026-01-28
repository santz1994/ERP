"""
Approval Workflow Models - Database schema for multi-level approvals

Tables:
- approval_requests: Main approval request tracking
- approval_steps: Individual approval steps (SPV → Manager → Director)
"""

from datetime import datetime
from uuid import uuid4
from sqlalchemy import (
    Column, DateTime, String, Integer, UUID, JSON, ForeignKey, 
    Text, Index, Boolean, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ApprovalEntityType(str, enum.Enum):
    """Entity types that can be approved"""
    SPK_CREATE = "SPK_CREATE"
    SPK_EDIT_QUANTITY = "SPK_EDIT_QUANTITY"
    SPK_EDIT_DEADLINE = "SPK_EDIT_DEADLINE"
    MO_EDIT = "MO_EDIT"
    MATERIAL_DEBT = "MATERIAL_DEBT"
    STOCK_ADJUSTMENT = "STOCK_ADJUSTMENT"


class ApprovalRequestStatus(str, enum.Enum):
    """Status of approval request"""
    PENDING = "PENDING"
    SPV_APPROVED = "SPV_APPROVED"
    MANAGER_APPROVED = "MANAGER_APPROVED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CANCELLED = "CANCELLED"


class ApprovalStepStatus(str, enum.Enum):
    """Status of individual approval step"""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalRequest(Base):
    """Main approval request table"""
    __tablename__ = "approval_requests"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Entity Information
    entity_type = Column(SQLEnum(ApprovalEntityType), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Submitter Information
    submitted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Request Details
    changes = Column(JSON, nullable=False)  # JSON of proposed changes
    reason = Column(Text, nullable=False)
    
    # Approval Flow
    status = Column(SQLEnum(ApprovalRequestStatus), default=ApprovalRequestStatus.PENDING, nullable=False)
    current_step = Column(Integer, default=0)  # Which step in approval chain (0=SPV, 1=Manager, 2=Director)
    approval_chain = Column(JSON, nullable=False)  # ["SPV", "MANAGER"] or ["MANAGER"]
    
    # Approval History (JSON array of approvals with timestamps)
    approvals = Column(JSON)
    
    # Rejection Info
    rejection_reason = Column(Text)
    rejected_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rejected_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    approval_steps = relationship("ApprovalStep", back_populates="approval_request", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index("idx_approval_requests_entity", "entity_type", "entity_id"),
        Index("idx_approval_requests_status", "status"),
        Index("idx_approval_requests_created", "created_at"),
        Index("idx_approval_requests_submitted", "submitted_by"),
    )


class ApprovalStep(Base):
    """Individual approval steps (SPV, Manager, Director)"""
    __tablename__ = "approval_steps"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    
    # Foreign Key
    approval_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("approval_requests.id"),
        nullable=False,
        index=True
    )
    
    # Step Information
    step_number = Column(Integer, nullable=False)  # 1=SPV, 2=Manager, 3=Director
    approver_role = Column(String(50), nullable=False)  # SPV, MANAGER, DIRECTOR
    status = Column(SQLEnum(ApprovalStepStatus), default=ApprovalStepStatus.PENDING, nullable=False)
    
    # Approval Information
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    notes = Column(Text)  # Approver notes
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    approval_request = relationship("ApprovalRequest", back_populates="approval_steps")
    
    # Indexes
    __table_args__ = (
        Index("idx_approval_steps_request", "approval_request_id"),
        Index("idx_approval_steps_status", "status"),
    )
