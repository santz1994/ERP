"""PO Delete / Correction Request Models — Approval Workflow."""
import enum
from sqlalchemy import Column, Integer, ForeignKey, String, TEXT, DateTime, Enum, func
from sqlalchemy.orm import relationship
from app.core.database import Base


class PORequestStatus(str, enum.Enum):
    PENDING  = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class PODeleteRequest(Base):
    """Approval request when non-admin wants to delete (cancel) a PO.

    Flow:
        - Non-admin   → creates request (status=Pending)
        - Manager/Admin → approves (PO deleted) or rejects
        - System Admin (Admin/Superadmin/Developer) → skips this table, deletes directly
    """
    __tablename__ = "po_delete_requests"

    id           = Column(Integer, primary_key=True, index=True)
    po_id        = Column(Integer, ForeignKey("purchase_orders.id", ondelete="SET NULL"), nullable=True, index=True)
    po_number    = Column(String(100), nullable=False)          # kept even after PO deleted
    request_reason = Column(TEXT, nullable=False)
    status       = Column(Enum(PORequestStatus), default=PORequestStatus.PENDING, nullable=False, index=True)

    requested_by    = Column(Integer, ForeignKey("users.id"), nullable=False)
    requested_at    = Column(DateTime(timezone=True), server_default=func.now())

    responded_by    = Column(Integer, ForeignKey("users.id"), nullable=True)
    responded_at    = Column(DateTime(timezone=True), nullable=True)
    response_note   = Column(TEXT, nullable=True)

    # Relationships
    requester      = relationship("User", foreign_keys=[requested_by])
    responder      = relationship("User", foreign_keys=[responded_by])
    purchase_order = relationship("PurchaseOrder", foreign_keys=[po_id])
