"""
Audit Trail System
Comprehensive logging of all system activities for ISO/IKEA compliance
"""
from sqlalchemy import Column, BigInteger, String, Text, DateTime, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum as py_enum
from app.core.database import Base


class AuditAction(str, py_enum.Enum):
    """Types of audited actions"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    TRANSFER = "TRANSFER"
    EXPORT = "EXPORT"
    IMPORT = "IMPORT"


class AuditModule(str, py_enum.Enum):
    """System modules"""
    AUTH = "Authentication"
    PPIC = "PPIC"
    CUTTING = "Cutting"
    EMBROIDERY = "Embroidery"
    SEWING = "Sewing"
    FINISHING = "Finishing"
    PACKING = "Packing"
    QUALITY = "Quality Control"
    WAREHOUSE = "Warehouse"
    KANBAN = "E-Kanban"
    REPORTS = "Reports"
    ADMIN = "Administration"


class AuditLog(Base):
    """
    Audit Trail Log
    
    Tracks all significant system activities for compliance and security.
    Required for ISO 9001 and IKEA IWAY standards.
    
    **Retention**: Keep audit logs for minimum 5 years (regulatory requirement)
    """
    __tablename__ = "audit_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # When & Who
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    username = Column(String(100), nullable=True)  # Denormalized for quick access
    user_role = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    
    # What happened
    action = Column(JSON(AuditAction), nullable=False, index=True)
    module = Column(JSON(AuditModule), nullable=False, index=True)
    entity_type = Column(String(100), nullable=True, index=True)  # e.g., "ManufacturingOrder"
    entity_id = Column(BigInteger, nullable=True, index=True)  # ID of affected record
    
    # Details
    description = Column(Text, nullable=False)
    old_values = Column(JSON, nullable=True)  # Before change (for UPDATE)
    new_values = Column(JSON, nullable=True)  # After change (for CREATE/UPDATE)
    
    # Additional context
    session_id = Column(String(255), nullable=True)
    request_method = Column(String(10), nullable=True)  # GET, POST, PUT, DELETE
    request_path = Column(String(500), nullable=True)
    response_status = Column(BigInteger, nullable=True)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_audit_timestamp_user', 'timestamp', 'user_id'),
        Index('idx_audit_module_action', 'module', 'action'),
        Index('idx_audit_entity', 'entity_type', 'entity_id'),
    )
    
    def __repr__(self):
        return f"<AuditLog {self.action.value} by {self.username} at {self.timestamp}>"


class UserActivityLog(Base):
    """
    User Activity Log (Lightweight tracking)
    
    Tracks user presence and session activity.
    Different from AuditLog - this is for monitoring active users and sessions.
    """
    __tablename__ = "user_activity_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # "login", "page_view", "action"
    activity_details = Column(Text, nullable=True)
    
    # Session tracking
    session_id = Column(String(255), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    # Timing
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    duration_seconds = Column(BigInteger, nullable=True)  # For timed activities
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_activity_user_time', 'user_id', 'timestamp'),
    )
    
    def __repr__(self):
        return f"<UserActivityLog {self.activity_type} by user {self.user_id}>"


class SecurityLog(Base):
    """
    Security Event Log
    
    Tracks security-related events: failed logins, unauthorized access, etc.
    """
    __tablename__ = "security_logs"
    
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    
    # When & Where
    timestamp = Column(DateTime, default=datetime.now, nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    
    # What happened
    event_type = Column(String(50), nullable=False, index=True)  # "failed_login", "blocked_ip", etc.
    severity = Column(String(20), nullable=False, index=True)  # "info", "warning", "critical"
    
    # Details
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True)
    username_attempted = Column(String(100), nullable=True)
    description = Column(Text, nullable=False)
    user_agent = Column(String(500), nullable=True)
    
    # Response
    action_taken = Column(String(100), nullable=True)  # "account_locked", "ip_blocked", etc.
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id])
    
    __table_args__ = (
        Index('idx_security_time_severity', 'timestamp', 'severity'),
    )
    
    def __repr__(self):
        return f"<SecurityLog {self.event_type} at {self.timestamp}>"
