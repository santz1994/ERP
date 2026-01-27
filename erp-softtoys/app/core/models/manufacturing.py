"""Manufacturing Order & Work Order Models."""

import enum

from datetime import datetime, date
from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, Integer, String, func, Date, Boolean
from sqlalchemy.orm import relationship

from app.core.database import Base


class RoutingType(str, enum.Enum):
    """Production routing types - 3 routes."""

    ROUTE1 = "Route 1"  # Full: Cutting → Embroidery → Sewing → Finishing → Packing
    ROUTE2 = "Route 2"  # Direct: Cutting → Sewing → Finishing → Packing
    ROUTE3 = "Route 3"  # Subcon: Cutting → Subcon → Finishing → Packing


class MOState(str, enum.Enum):
    """Manufacturing Order state."""

    DRAFT = "Draft"
    IN_PROGRESS = "In Progress"
    DONE = "Done"
    CANCELLED = "Cancelled"


class Department(str, enum.Enum):
    """Production departments."""

    CUTTING = "Cutting"
    EMBROIDERY = "Embroidery"
    SUBCON = "Subcon"
    SEWING = "Sewing"
    FINISHING = "Finishing"
    PACKING = "Packing"


class SPKStatus(str, enum.Enum):
    """SPK (Surat Perintah Kerja) production status."""
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class SPK(Base):
    """SPK - Surat Perintah Kerja (Production Work Order)
    Per-department production order derived from Manufacturing Order
    Tracks daily production input, modifications, and material debt.
    """
    __tablename__ = "spks"

    id = Column(Integer, primary_key=True, index=True)
    mo_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False, index=True)
    department = Column(Enum(Department), nullable=False, index=True)
    
    # Original quantity tracking
    original_qty = Column(Integer, default=0, nullable=False)
    modified_qty = Column(Integer)
    target_qty = Column(Integer, nullable=False)  # Current target for production
    produced_qty = Column(Integer, default=0)
    
    # Modification tracking
    modification_reason = Column(String(255))
    modified_by_id = Column(Integer, ForeignKey("users.id"))
    modified_at = Column(DateTime)
    
    # Status & dates
    production_status = Column(String(50), default="NOT_STARTED", index=True)
    start_date = Column(Date)
    target_completion_date = Column(Date)
    completion_date = Column(Date)
    allow_negative_inventory = Column(Boolean, default=False)
    
    # Negative inventory approval
    negative_approval_status = Column(String(50))  # PENDING, APPROVED, REJECTED
    negative_approved_by_id = Column(Integer, ForeignKey("users.id"))
    negative_approved_at = Column(DateTime)
    
    # Audit
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", foreign_keys=[mo_id])
    daily_production = relationship("SPKDailyProduction", back_populates="spk")
    production_completion = relationship("SPKProductionCompletion", back_populates="spk")
    modifications = relationship("SPKModification", back_populates="spk")
    material_debts = relationship("MaterialDebt", back_populates="spk")
    created_by = relationship("User", foreign_keys=[created_by_id])
    modified_by = relationship("User", foreign_keys=[modified_by_id])
    negative_approved_by = relationship("User", foreign_keys=[negative_approved_by_id])


class WorkOrderStatus(str, enum.Enum):
    """Work Order execution status."""

    PENDING = "Pending"
    RUNNING = "Running"
    FINISHED = "Finished"


class ManufacturingOrder(Base):
    """Manufacturing Order (SPK Induk)
    Master production order that spans multiple departments.
    """

    __tablename__ = "manufacturing_orders"

    id = Column(Integer, primary_key=True, index=True)
    so_line_id = Column(Integer, ForeignKey("sales_order_lines.id"), nullable=True)  # Link to sales order
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Article to produce

    # Quantity tracking
    qty_planned = Column(DECIMAL(10, 2), nullable=False)  # Target from BOM
    qty_produced = Column(DECIMAL(10, 2), default=0)  # Actual output

    # Routing
    routing_type = Column(Enum(RoutingType), nullable=False, index=True)  # Route 1, 2, or 3
    batch_number = Column(String(50), unique=True, nullable=False, index=True)  # Traceability

    # Status
    state = Column(Enum(MOState), default=MOState.DRAFT, index=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="manufacturing_orders")
    work_orders = relationship("WorkOrder", back_populates="manufacturing_order", cascade="all, delete-orphan")
    transfer_logs = relationship("TransferLog", back_populates="manufacturing_order")

    def __repr__(self):
        return f"<ManufacturingOrder(batch={self.batch_number}, routing={self.routing_type.value})>"


class WorkOrder(Base):
    """Work Order (SPK per Department)
    Individual work instructions for each department/process.
    """

    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    mo_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Department & process
    department = Column(Enum(Department), nullable=False, index=True)

    # Execution status
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING, index=True)

    # Timing
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    # Material tracking
    input_qty = Column(DECIMAL(10, 2), nullable=False)  # Material received
    output_qty = Column(DECIMAL(10, 2), nullable=True)  # CRITICAL: Can be Surplus/Shortage
    reject_qty = Column(DECIMAL(10, 2), default=0)  # Defective units

    # Labor tracking
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="work_orders")
    product = relationship("Product", back_populates="work_orders")
    material_consumptions = relationship("MaterialConsumption", back_populates="work_order", cascade="all, delete-orphan")
    qc_inspections = relationship("QCInspection", back_populates="work_order")

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, dept={self.department.value}, status={self.status.value})>"


class MaterialConsumption(Base):
    """Material Consumption Tracking
    Records actual material used in each work order.
    """

    __tablename__ = "mo_material_consumption"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Material used

    # Quantity
    qty_planned = Column(DECIMAL(10, 2), nullable=False)  # Target by BOM
    qty_actual = Column(DECIMAL(10, 2), nullable=True)  # Real consumption (operator input)

    # Lot tracking
    lot_id = Column(Integer, ForeignKey("stock_lots.id"), nullable=True)  # Which batch/roll

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    work_order = relationship("WorkOrder", back_populates="material_consumptions")
    product = relationship("Product", foreign_keys=[product_id])

    def __repr__(self):
        return f"<MaterialConsumption(wo_id={self.work_order_id}, product_id={self.product_id})>"
