"""E-Kanban System for Accessory Requests
Digital kanban system for managing accessory/material requests between departments.
"""
import enum as py_enum
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class KanbanStatus(str, py_enum.Enum):
    """Kanban card status."""

    PENDING = "Pending"
    APPROVED = "Approved"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class KanbanPriority(str, py_enum.Enum):
    """Kanban priority levels."""

    LOW = "Low"
    NORMAL = "Normal"
    HIGH = "High"
    URGENT = "Urgent"


class KanbanCard(Base):
    """E-Kanban Card for Accessory/Material Requests.

    Digital kanban system for pull-based inventory replenishment.
    When department needs materials, they create kanban card instead of
    manually calling warehouse.

    Example Use Cases:
    - Packing dept needs carton boxes → Create kanban card
    - Sewing needs labels → Create kanban card
    - Finishing needs dacron filling → Create kanban card
    """

    __tablename__ = "kanban_cards"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    card_number = Column(String(50), unique=True, nullable=False, index=True)

    # Request Information
    requested_by_dept = Column(String(50), nullable=False, index=True)
    requested_by_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False)
    requested_at = Column(DateTime, default=datetime.now, nullable=False)

    # Material Information
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    qty_requested = Column(Integer, nullable=False)

    # Priority & Urgency
    priority = Column(Enum(KanbanPriority), default=KanbanPriority.NORMAL, nullable=False)
    needed_by = Column(DateTime, nullable=True)  # When material is needed

    # Status & Approval
    status = Column(Enum(KanbanStatus), default=KanbanStatus.PENDING, nullable=False, index=True)
    approved_by_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)

    # Fulfillment
    qty_fulfilled = Column(Integer, default=0, nullable=False)
    fulfilled_by_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)

    # Work Order Reference (optional)
    work_order_id = Column(BigInteger, ForeignKey("work_orders.id"), nullable=True)

    # Notes & Reason
    request_reason = Column(Text, nullable=True)
    fulfillment_notes = Column(Text, nullable=True)

    # Auto-replenishment flag (for recurring materials)
    is_auto_replenish = Column(Boolean, default=False)
    reorder_point = Column(Integer, nullable=True)  # Trigger new kanban when stock hits this

    # Cancellation
    cancelled_by_user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    requested_by = relationship("User", foreign_keys=[requested_by_user_id])
    approved_by = relationship("User", foreign_keys=[approved_by_user_id])
    fulfilled_by = relationship("User", foreign_keys=[fulfilled_by_user_id])
    cancelled_by = relationship("User", foreign_keys=[cancelled_by_user_id])
    work_order = relationship("WorkOrder", foreign_keys=[work_order_id])

    def __repr__(self):
        return f"<KanbanCard {self.card_number} - {self.status.value}>"


class KanbanBoard(Base):
    """E-Kanban Board Configuration.

    Defines kanban lanes, limits, and rules per department
    """

    __tablename__ = "kanban_boards"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    department = Column(String(50), unique=True, nullable=False)

    # WIP Limits (Work In Progress limits per status)
    max_pending = Column(Integer, default=10)
    max_in_progress = Column(Integer, default=5)

    # Auto-approval settings
    enable_auto_approve = Column(Boolean, default=False)
    auto_approve_threshold = Column(Integer, nullable=True)  # Auto-approve if qty <= threshold

    # Notification settings
    notify_on_new_card = Column(Boolean, default=True)
    notify_on_approval = Column(Boolean, default=True)
    notify_on_fulfillment = Column(Boolean, default=True)

    # Active status
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<KanbanBoard {self.department}>"


class KanbanRule(Base):
    """E-Kanban Automatic Replenishment Rules.

    Defines automatic triggers for creating kanban cards
    when stock levels reach reorder points
    """

    __tablename__ = "kanban_rules"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # Product & Location
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False)
    department = Column(String(50), nullable=False)

    # Trigger Conditions
    reorder_point = Column(Integer, nullable=False)  # Create kanban when stock <= this
    order_quantity = Column(Integer, nullable=False)  # How much to request

    # Priority
    default_priority = Column(Enum(KanbanPriority), default=KanbanPriority.NORMAL)

    # Lead Time
    lead_time_days = Column(Integer, default=1)  # Expected time to fulfill

    # Active status
    is_active = Column(Boolean, default=True)

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<KanbanRule {self.product_id} @ {self.reorder_point}>"
