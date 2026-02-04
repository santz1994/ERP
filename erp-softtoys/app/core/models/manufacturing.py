"""Manufacturing Order & Work Order Models."""

import enum

from datetime import datetime, date
from sqlalchemy import DECIMAL, Column, DateTime, Enum, ForeignKey, Integer, String, func, Date, Boolean, TEXT
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
    
    FLEXIBLE TARGET SYSTEM (NEW):
    - original_qty: Base quantity from MO
    - buffer_percentage: Department-specific buffer (+10% Cutting, +6.7% Sewing, etc.)
    - target_qty: Adjusted target (original × buffer)
    - good_qty: Good output produced
    - defect_qty: Rejected/defect output
    - rework_qty: Units sent for rework
    - produced_qty: Total produced (good + defect)
    
    DATE TRACKING:
    - planned_start_date: Production scheduled start
    - actual_start_date: When production actually began
    - production_date_stamp: Date for traceability tracking
    """
    __tablename__ = "spks"

    id = Column(Integer, primary_key=True, index=True)
    mo_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False, index=True)
    department = Column(Enum(Department), nullable=False, index=True)
    
    # ========================================================================
    # FLEXIBLE TARGET SYSTEM - Buffer Allocation per Department
    # ========================================================================
    original_qty = Column(Integer, default=0, nullable=False, comment="Base quantity from MO")
    buffer_percentage = Column(DECIMAL(5, 2), default=0, nullable=False, 
                              comment="Department buffer % (10% Cutting, 6.7% Sewing, etc.)")
    target_qty = Column(Integer, nullable=False, comment="Target with buffer (original × buffer)")
    
    # Production output tracking
    good_qty = Column(Integer, default=0, nullable=False, comment="Good output produced")
    defect_qty = Column(Integer, default=0, nullable=False, comment="Defect/reject output")
    rework_qty = Column(Integer, default=0, nullable=False, comment="Sent to rework")
    produced_qty = Column(Integer, default=0, nullable=False, comment="Total produced (good + defect)")
    
    # Legacy fields (deprecated - use good_qty/defect_qty instead)
    modified_qty = Column(Integer, comment="DEPRECATED: Use target_qty instead")
    
    # ========================================================================
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
    
    # ========================================================================
    # DATE TRACKING - Production Planning & Traceability
    # ========================================================================
    planned_start_date = Column(Date, nullable=True, comment="Production scheduled start date")
    actual_start_date = Column(Date, nullable=True, comment="Actual production start date")
    production_date_stamp = Column(Date, nullable=True, comment="Production date stamp for traceability")
    
    # ========================================================================
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
    
    FLOW: PO Purchasing → MO → BOM Explosion → SPK/WO
    
    DUAL TRIGGER SYSTEM (NEW):
    - PARTIAL mode: PO Fabric only → Cutting & Embroidery can start
    - RELEASED mode: PO Fabric + PO Label → All departments can start
    - Lead time reduction: -3 to -5 days
    
    IKEA COMPLIANCE:
    - traceability_code: Unique code for product recall (batch + date)
    - label_production_date: Date printed on physical product label
    - production_week: IKEA week format (WW-YYYY) - inherited from PO
    - destination_country: Shipping destination - inherited from PO
    """

    __tablename__ = "manufacturing_orders"

    id = Column(Integer, primary_key=True, index=True)
    
    # ========================================================================
    # DUAL TRIGGER SYSTEM - PO Fabric + PO Label
    # ========================================================================
    po_fabric_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True,
                         comment="PO for fabric materials (TRIGGER 1: enables Cutting/Embroidery)")
    po_label_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True,
                        comment="PO for labels/tags (TRIGGER 2: enables all departments)")
    trigger_mode = Column(String(20), nullable=False, default="PARTIAL", index=True,
                         comment="Production release mode: PARTIAL (fabric only) or RELEASED (fabric+label)")
    
    # Legacy PO field (deprecated - use po_fabric_id instead)
    po_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True, index=True)  # Link to PO Purchasing
    so_line_id = Column(Integer, ForeignKey("sales_order_lines.id"), nullable=True)  # Link to sales order (legacy)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Article to produce

    # Quantity tracking
    qty_planned = Column(DECIMAL(10, 2), nullable=False)  # Target from BOM
    qty_produced = Column(DECIMAL(10, 2), default=0)  # Actual output

    # Routing
    routing_type = Column(Enum(RoutingType), nullable=False, index=True)  # Route 1, 2, or 3
    batch_number = Column(String(50), unique=True, nullable=False, index=True)  # Traceability

    # Status
    state = Column(Enum(MOState), default=MOState.DRAFT, index=True)

    # ========================================================================
    # IKEA COMPLIANCE - Production Date Tracking & Traceability
    # ========================================================================
    
    # Production planning dates (set by management/PPIC)
    planned_production_date = Column(Date, nullable=True, index=True,
                                    comment="Target date when production should start (set by PPIC)")
    target_shipment_date = Column(Date, nullable=True,
                                  comment="Target date for shipment to customer/IKEA")
    
    # Actual production dates (auto-updated from work orders)
    actual_production_start_date = Column(Date, nullable=True,
                                         comment="Actual date when production started (first WO began)")
    actual_production_end_date = Column(Date, nullable=True,
                                       comment="Actual date when production completed (last WO finished)")
    
    # IKEA traceability requirements
    label_production_date = Column(Date, nullable=True, index=True,
                                   comment="Date printed on product label (IKEA traceability requirement)")
    production_week = Column(String(10), nullable=True, index=True,
                            comment="Production week in IKEA format (e.g., 05-2026)")
    destination_country = Column(String(50), nullable=True, index=True,
                                comment="Shipping destination country")
    traceability_code = Column(String(50), nullable=True, unique=True, index=True,
                              comment="Unique traceability code (batch + date) for product recall")
    
    # ========================================================================
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
    
    FLEXIBLE OUTPUT TRACKING (NEW):
    - output_qty: Primary field for good output (backward compatible)
    - good_qty: Computed property alias for output_qty
    - defect_qty: Computed property alias for reject_qty
    - Supports both new (output/reject) and legacy (good/defect) naming
    
    DATE TRACKING:
    - planned_start_date: When this WO should start (from production schedule)
    - actual_start_date: When production actually began
    - planned_completion_date: Target completion date
    - actual_completion_date: When work was actually finished
    - production_date_stamp: Date for this department's output (traceability)
    """

    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    mo_id = Column(Integer, ForeignKey("manufacturing_orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # WIP Routing fields (NEW)
    wo_number = Column(String(100), nullable=True)  # Work Order number
    sequence = Column(Integer, nullable=True)  # Order in production flow
    input_wip_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Input WIP
    output_wip_product_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Output WIP
    target_qty = Column(DECIMAL(10, 2), nullable=True)  # Target quantity with buffer
    notes = Column(TEXT, nullable=True)  # Additional notes

    # Department & process
    department = Column(Enum(Department), nullable=False, index=True)

    # Execution status
    status = Column(Enum(WorkOrderStatus), default=WorkOrderStatus.PENDING, index=True)

    # ========================================================================
    # DATE TRACKING - Department-Level Production Dates
    # ========================================================================
    
    # Planned dates (from production schedule)
    planned_start_date = Column(Date, nullable=True, index=True,
                               comment="Planned date when this WO should start")
    planned_completion_date = Column(Date, nullable=True,
                                    comment="Planned date when this WO should complete")
    
    # Actual dates (from operators)
    actual_start_date = Column(Date, nullable=True, index=True,
                              comment="Actual date when this WO started production")
    actual_completion_date = Column(Date, nullable=True,
                                   comment="Actual date when this WO was completed")
    
    # Traceability date stamp
    production_date_stamp = Column(Date, nullable=True,
                                  comment="Date stamp for this department output (for traceability)")
    
    # ========================================================================
    # Timing (legacy - datetime tracking)
    start_time = Column(DateTime(timezone=True), nullable=True)
    end_time = Column(DateTime(timezone=True), nullable=True)

    # ========================================================================
    # MATERIAL TRACKING - Primary Fields
    # ========================================================================
    input_qty = Column(DECIMAL(10, 2), nullable=False, comment="Material received as input")
    output_qty = Column(DECIMAL(10, 2), nullable=True, comment="Good output produced")
    reject_qty = Column(DECIMAL(10, 2), default=0, comment="Defective/rejected units")

    # Labor tracking
    worker_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # ========================================================================
    # COMPUTED PROPERTIES - Backward Compatibility Aliases
    # ========================================================================
    @property
    def good_qty(self):
        """Alias for output_qty (backward compatibility)."""
        return self.output_qty
    
    @property
    def defect_qty(self):
        """Alias for reject_qty (backward compatibility)."""
        return self.reject_qty
    
    @property
    def actual_qty(self):
        """Alias for output_qty (backward compatibility)."""
        return self.output_qty

    # Relationships
    manufacturing_order = relationship("ManufacturingOrder", back_populates="work_orders")
    product = relationship("Product", foreign_keys=[product_id], back_populates="work_orders")
    material_consumptions = relationship("MaterialConsumption", back_populates="work_order", cascade="all, delete-orphan")
    allocated_materials = relationship("SPKMaterialAllocation", back_populates="work_order", cascade="all, delete-orphan")
    qc_inspections = relationship("QCInspection", back_populates="work_order")

    def __repr__(self):
        return f"<WorkOrder(id={self.id}, dept={self.department.value}, status={self.status.value})>"


class SPKMaterialAllocation(Base):
    """
    SPK Material Allocation - Week 4 Implementation
    Tracks material allocation and consumption per Work Order
    
    Features:
    - Soft reservation (is_reserved=True, is_consumed=False)
    - Hard consumption (is_consumed=True)
    - Material debt support (negative inventory)
    """
    
    __tablename__ = "spk_material_allocations"
    
    id = Column(Integer, primary_key=True, index=True)
    wo_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Quantities
    qty_allocated = Column(DECIMAL(12, 3), nullable=False, comment="Allocated quantity (soft reservation)")
    qty_consumed = Column(DECIMAL(12, 3), nullable=False, default=0, comment="Actually consumed quantity")
    
    # Unit of Measure (stored as string enum)
    uom = Column(String(20), nullable=True, comment="Unit of measurement (Pcs, Meter, Yard, Kg, etc)")
    
    # Status flags
    is_reserved = Column(Boolean, nullable=False, default=True, comment="Is material reserved?")
    is_consumed = Column(Boolean, nullable=False, default=False, comment="Is material consumed?")
    
    # Timestamps
    allocated_at = Column(DateTime, nullable=True, comment="When allocated")
    consumed_at = Column(DateTime, nullable=True, comment="When consumed")
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="allocated_materials")
    material = relationship("Product", foreign_keys=[material_id])
    
    def __repr__(self):
        return f"<SPKMaterialAllocation(wo_id={self.wo_id}, material_id={self.material_id}, allocated={self.qty_allocated})>"


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
