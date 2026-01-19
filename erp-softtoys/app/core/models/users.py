"""
User & Authentication Models
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, func
from datetime import datetime
import enum
from app.core.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "Admin"
    PPIC_MANAGER = "PPIC Manager"
    PPIC_ADMIN = "PPIC Admin"
    SPV_CUTTING = "SPV Cutting"
    SPV_SEWING = "SPV Sewing"
    SPV_FINISHING = "SPV Finishing"
    OPERATOR_CUT = "Operator Cutting"
    OPERATOR_EMBRO = "Operator Embroidery"
    OPERATOR_SEW = "Operator Sewing"
    OPERATOR_FINISH = "Operator Finishing"
    OPERATOR_PACK = "Operator Packing"
    QC_INSPECTOR = "QC Inspector"
    QC_LAB = "QC Lab"
    WAREHOUSE_ADMIN = "Warehouse Admin"
    WAREHOUSE_OP = "Warehouse Operator"
    PURCHASING = "Purchasing"
    SECURITY = "Security"


class User(Base):
    """
    Users with role-based access control
    16 roles: Admin, PPIC Manager, Supervisors (5), Operators (5), QC (2), Warehouse (2), Purchasing, Security
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    
    # Profile
    full_name = Column(String(100), nullable=False)
    
    # Role-based access (16 roles)
    role = Column(Enum(UserRole), nullable=False, index=True)
    department = Column(String(50), nullable=True)  # Which dept they work in: Cutting, Sewing, Finishing, etc.
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # Audit & Security
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_password_change = Column(DateTime(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0)  # Track failed attempts
    locked_until = Column(DateTime(timezone=True), nullable=True)  # Account lockout time
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role.value}, dept={self.department})>"
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role"""
        return self.role.value == role_name
    
    def is_supervisor(self) -> bool:
        """Check if user is supervisor"""
        return "SPV" in self.role.value
    
    def is_operator(self) -> bool:
        """Check if user is operator"""
        return "Operator" in self.role.value
    
    def is_qc(self) -> bool:
        """Check if user is QC"""
        return "QC" in self.role.value
    
    def is_warehouse(self) -> bool:
        """Check if user is warehouse staff"""
        return "Warehouse" in self.role.value
