"""
Exception & Alert Models
NEW TABLES - Gap Fixes
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, func, TEXT
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class AlertType(str, enum.Enum):
    """Alert classification"""
    LINE_CLEARANCE_BLOCK = "Line Clearance Block"
    SEGREGASI_ALARM = "Segregasi Alarm"
    QC_FAIL = "QC Fail"
    SHORTAGE = "Shortage"
    DUPLICATE_SCAN = "Duplicate Scan"
    SCANNER_OFFLINE = "Scanner Offline"


class AlertSeverity(str, enum.Enum):
    """Alert severity level"""
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


class AlertStatus(str, enum.Enum):
    """Alert lifecycle status"""
    PENDING = "Pending"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"
    OVERRIDDEN = "Overridden"


class ClearanceMethod(str, enum.Enum):
    """Methods for clearing segregasi alerts"""
    PHYSICAL_GAP = "Physical Gap"  # 5-meter separation
    LINE_STOP = "Line Stop"  # Stopped conveyor line
    MANUAL_INSPECTION = "Manual Inspection"  # Operator verified


class AlertLog(Base):
    """
    Alert Log - All alerts/blocks triggered in system
    NEW TABLE - Gap Fix #2 for escalation tracking
    """
    __tablename__ = "alert_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Alert info
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False, index=True)
    
    # Context
    triggered_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    triggered_by = Column(Integer, ForeignKey("users.id"), nullable=True)  # System or user
    triggered_in_workflow_id = Column(Integer, nullable=True)  # Flowchart ID where alert occurred
    
    # Escalation
    escalated_to = Column(Integer, ForeignKey("users.id"), nullable=True)  # Who escalated to
    escalation_level = Column(Integer, default=1)  # 1=First, 2=Manager, 3=Director
    
    # Resolution
    status = Column(Enum(AlertStatus), default=AlertStatus.PENDING, index=True)
    resolution_time = Column(DateTime(timezone=True), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Details
    message = Column(String(500), nullable=False)
    notes = Column(TEXT, nullable=True)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    triggered_user = relationship("User", foreign_keys=[triggered_by])
    escalated_user = relationship("User", foreign_keys=[escalated_to])
    resolved_user = relationship("User", foreign_keys=[resolved_by])
    
    def __repr__(self):
        return f"<AlertLog(type={self.alert_type.value}, severity={self.severity.value})>"


class SegregasiAcknowledgement(Base):
    """
    Segregasi Acknowledgement Log
    NEW TABLE - Gap Fix #2 for manual line clearance tracking
    Records operator confirmation that segregasi has been cleared
    """
    __tablename__ = "segregasi_acknowledgement"
    
    id = Column(Integer, primary_key=True, index=True)
    transfer_log_id = Column(Integer, ForeignKey("transfer_logs.id"), nullable=False, index=True)
    
    # Acknowledgement
    acknowledged_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Method of clearance
    clearance_method = Column(Enum(ClearanceMethod), nullable=False)
    
    # Evidence
    proof_photo_url = Column(String(500), nullable=True)  # Photo showing cleared line
    clearance_notes = Column(TEXT, nullable=True)  # Operator comments
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    transfer_log = relationship("TransferLog", foreign_keys=[transfer_log_id])
    acknowledged_user = relationship("User", foreign_keys=[acknowledged_by])
    
    def __repr__(self):
        return f"<SegregasiAcknowledgement(transfer={self.transfer_log_id}, method={self.clearance_method.value})>"
