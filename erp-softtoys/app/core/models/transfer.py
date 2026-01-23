"""Transfer & Line Occupancy Models (QT-09 Gold Standard)
"""

import enum

from sqlalchemy import DECIMAL, Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TransferStatus(str, enum.Enum):
    """Transfer status - Handshake Protocol"""

    INITIATED = "Initiated"  # Transfer created, waiting for line clearance
    BLOCKED = "Blocked"  # Line not ready
    LOCKED = "Locked"  # Stock locked, waiting for ACCEPT
    ACCEPTED = "Accepted"  # Receiving dept scanned ACCEPT
    COMPLETED = "Completed"  # Stock qty transferred
    CANCELLED = "Cancelled"


class LineStatus(str, enum.Enum):
    """Line occupancy status"""

    CLEAR = "Clear"  # Line ready for new article
    OCCUPIED = "Occupied"  # Line processing article
    PAUSED = "Paused"  # Line paused for clearance


class TransferDept(str, enum.Enum):
    """Departments that can send/receive transfers (Gap Fix #3)"""

    CUTTING = "Cutting"
    EMBROIDERY = "Embroidery"
    SEWING = "Sewing"
    FINISHING = "Finishing"
    PACKING = "Packing"
    SUBCON = "Subcon"
    FINISHGOOD = "FinishGood"


class TransferLog(Base):
    """Transfer Log - Records all inter-departmental transfers
    Implements Handshake Digital protocol (QT-09)
    Gap Fix: Expanded from_dept & to_dept enums
    """

    __tablename__ = "transfer_logs"

    id = Column(Integer, primary_key=True, index=True)
    mo_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False, index=True)

    # Departments (Gap Fix #3: Added Embroidery)
    from_dept = Column(Enum(TransferDept), nullable=False, index=True)
    to_dept = Column(Enum(TransferDept), nullable=False, index=True)

    # Article being transferred
    article_code = Column(String(50), nullable=False, index=True)
    batch_id = Column(String(50), nullable=False)
    week_number = Column(Integer, nullable=True)
    destination = Column(String(50), nullable=True)  # Country destination

    # Quantity tracking
    qty_sent = Column(DECIMAL(10, 2), nullable=False)
    qty_received = Column(DECIMAL(10, 2), nullable=True)  # Null until ACCEPT

    # Line Clearance Validation (QT-09 Cek 1-2)
    is_line_clear = Column(Boolean, default=False)  # Verified line is empty
    line_checked_at = Column(DateTime(timezone=True), nullable=True)
    line_checked_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Handshake Digital Protocol (QT-09 Cek 3)
    status = Column(Enum(TransferStatus), default=TransferStatus.INITIATED, index=True)
    timestamp_start = Column(DateTime(timezone=True), server_default=func.now())
    timestamp_accept = Column(DateTime(timezone=True), nullable=True)  # When receiving dept scanned ACCEPT
    timestamp_end = Column(DateTime(timezone=True), nullable=True)  # When qty transferred
    accepted_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who scanned ACCEPT

    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="transfer_logs")
    line_checked_user = relationship("User", foreign_keys=[line_checked_by])
    accept_user = relationship("User", foreign_keys=[accepted_by])

    def __repr__(self):
        return f"<TransferLog({self.from_dept.value}→{self.to_dept.value}, qty={self.qty_sent})>"


class LineOccupancy(Base):
    """Line Occupancy Tracking (Real-time Status)
    NEW TABLE - Gap Fix #2
    Tracks which article is currently on each line and when it will be clear
    """

    __tablename__ = "line_occupancy"

    id = Column(Integer, primary_key=True, index=True)

    # Line identification
    dept_name = Column(Enum(TransferDept), nullable=False, index=True)
    line_number = Column(Integer, nullable=True)  # Optional: line ID within dept

    # Current occupancy
    current_article_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    current_batch_id = Column(String(50), nullable=True, index=True)
    current_destination = Column(String(50), nullable=True)  # For segregasi check
    current_week = Column(Integer, nullable=True)

    # Status
    occupancy_status = Column(Enum(LineStatus), default=LineStatus.CLEAR, index=True)

    # Locking information
    locked_at = Column(DateTime(timezone=True), nullable=True)
    locked_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    expected_clear_time = Column(DateTime(timezone=True), nullable=True)  # ETA when line will be free

    # Audit
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    current_article = relationship("Product", foreign_keys=[current_article_id])
    locked_by_user = relationship("User", foreign_keys=[locked_by])

    def __repr__(self):
        return f"<LineOccupancy({self.dept_name.value} Line {self.line_number}, status={self.occupancy_status.value})>"
