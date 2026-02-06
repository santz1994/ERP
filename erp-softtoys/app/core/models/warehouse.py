"""Warehouse & Stock Management Models."""

import enum

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class LocationType(str, enum.Enum):
    """Warehouse location types."""

    VIEW = "View"  # Goods on display
    INTERNAL = "Internal"  # Internal warehouse
    CUSTOMER = "Customer"
    SUPPLIER = "Supplier"
    PRODUCTION = "Production"  # Factory floor
    INVENTORY_LOSS = "Inventory Loss"  # Write-off


class StockMoveStatus(str, enum.Enum):
    """Stock movement status."""

    DRAFT = "Draft"
    DONE = "Done"


class MaterialRequestStatus(str, enum.Enum):
    """Manual material request status."""

    PENDING = "Pending"
    APPROVED = "Approved"
    REJECTED = "Rejected"
    COMPLETED = "Completed"


class POStatus(str, enum.Enum):
    """Purchase Order Status."""

    DRAFT = "Draft"
    SENT = "Sent"
    RECEIVED = "Received"
    DONE = "Done"


class POType(str, enum.Enum):
    """Purchase Order Type - PO Reference System."""

    KAIN = "KAIN"  # Fabric PO - TRIGGER 1 (enables cutting/embroidery)
    LABEL = "LABEL"  # Label PO - TRIGGER 2 (full production release + week/destination)
    ACCESSORIES = "ACCESSORIES"  # Accessories PO (optional reference)


class PurchaseOrder(Base):
    """Purchase Orders - Orders placed with suppliers
    Tracks material procurement with parent-child reference chain.
    
    PO Reference System:
    - PO KAIN (Master) → TRIGGER 1 for cutting/embroidery (MO PARTIAL)
    - PO LABEL (Child) → TRIGGER 2 for full production (MO RELEASED)
    - PO ACCESSORIES (Child) → Optional reference to PO KAIN
    
    Business Rules:
    1. PO LABEL must reference PO KAIN (parent-child relationship)
    2. PO LABEL must have week & destination
    3. PO KAIN cannot self-reference
    4. PO KAIN/LABEL must have article_id
    """

    __tablename__ = "purchase_orders"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("partners.id"), nullable=False, index=True)

    # Order dates
    order_date = Column(Date, nullable=False)
    expected_date = Column(Date, nullable=False)

    # Status
    status = Column(Enum(POStatus), default=POStatus.DRAFT, nullable=False, index=True)

    # Tracking
    po_number = Column(String(100), unique=True, nullable=False, index=True)

    # 🆕 PO REFERENCE SYSTEM FIELDS (Added: 2026-02-06)
    
    # PO Type (KAIN/LABEL/ACCESSORIES)
    po_type = Column(
        Enum(POType), 
        nullable=False, 
        index=True,
        comment="PO Type: KAIN (Fabric-TRIGGER 1), LABEL (TRIGGER 2), ACCESSORIES"
    )
    
    # Parent-child relationship
    source_po_kain_id = Column(
        Integer,
        ForeignKey("purchase_orders.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Reference to parent PO KAIN (required for PO LABEL/ACC)"
    )
    
    # Article/Product reference
    article_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
        comment="Article/Product reference (required for PO KAIN/LABEL)"
    )
    
    article_qty = Column(
        Integer,
        nullable=True,
        comment="Article quantity (pcs)"
    )
    
    # PO LABEL specific fields (TRIGGER 2)
    week = Column(
        String(20),
        nullable=True,
        index=True,
        comment="Production week (e.g., W5, W12) - required for PO LABEL"
    )
    
    destination = Column(
        String(100),
        nullable=True,
        comment="Delivery destination - required for PO LABEL"
    )
    
    # Manufacturing Order link
    linked_mo_id = Column(
        Integer,
        ForeignKey("manufacturing_orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="Linked Manufacturing Order (MO) for production tracking"
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    stock_lots = relationship("StockLot", foreign_keys="StockLot.purchase_order_id")
    
    # Supplier relationship (FK: supplier_id)
    supplier = relationship(
        "Partner",
        foreign_keys=[supplier_id],
        doc="Supplier/Vendor for this purchase order"
    )
    
    # 🆕 PO REFERENCE SYSTEM RELATIONSHIPS
    
    # Parent-child relationship (self-referencing)
    source_po_kain = relationship(
        "PurchaseOrder",
        remote_side=[id],
        foreign_keys=[source_po_kain_id],
        backref="related_po_children",
        doc="Parent PO KAIN reference (for PO LABEL/ACC)"
    )
    
    # Article reference
    article = relationship(
        "Product",
        foreign_keys=[article_id],
        doc="Article/Product associated with this PO"
    )
    
    # Manufacturing Order link
    linked_mo = relationship(
        "ManufacturingOrder",
        foreign_keys=[linked_mo_id],
        doc="Manufacturing Order linked to this PO (especially PO KAIN)"
    )

    def __repr__(self):
        return f"<PurchaseOrder(po={self.po_number}, type={self.po_type.value if self.po_type else 'N/A'}, status={self.status.value})>"


class Location(Base):
    """Warehouse Locations & Production Lines
    Stores all physical locations where inventory can be held.
    """

    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # e.g., "Rak A1", "Line Sewing"
    type = Column(Enum(LocationType), nullable=False, index=True)

    # Additional info
    capacity = Column(DECIMAL(10, 2), nullable=True)  # Optional: storage capacity

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

    # Relationships
    stock_quants = relationship("StockQuant", back_populates="location")
    stock_moves_from = relationship("StockMove", foreign_keys="StockMove.location_id_from", back_populates="from_location")
    stock_moves_to = relationship("StockMove", foreign_keys="StockMove.location_id_to", back_populates="to_location")

    def __repr__(self):
        return f"<Location(name={self.name}, type={self.type.value})>"


class StockMove(Base):
    """Stock Movements
    Tracks all inventory movements between locations (FIFO).
    """

    __tablename__ = "stock_moves"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    # Quantity & UOM
    qty = Column(DECIMAL(10, 2), nullable=False)
    uom = Column(String(10), nullable=False)  # Pcs, Meter, Kg, Roll, etc.

    # Locations
    location_id_from = Column(Integer, ForeignKey("locations.id"), nullable=False)
    location_id_to = Column(Integer, ForeignKey("locations.id"), nullable=False)

    # Reference
    reference_doc = Column(String(100), nullable=False)  # SPK number, PO number, etc.

    # Status
    state = Column(Enum(StockMoveStatus), default=StockMoveStatus.DRAFT, index=True)

    # Lot/Batch tracking
    lot_id = Column(Integer, ForeignKey("stock_lots.id"), nullable=True)

    # Audit
    date = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    from_location = relationship("Location", foreign_keys=[location_id_from], back_populates="stock_moves_from")
    to_location = relationship("Location", foreign_keys=[location_id_to], back_populates="stock_moves_to")

    def __repr__(self):
        return f"<StockMove({self.qty} {self.uom} from {self.location_id_from} to {self.location_id_to})>"


class StockQuant(Base):
    """Stock Quantities
    Current inventory balance by product, location, and lot (FIFO support).
    """

    __tablename__ = "stock_quants"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)
    lot_id = Column(Integer, ForeignKey("stock_lots.id"), nullable=True)  # Batch/Roll number

    # Quantities
    qty_on_hand = Column(DECIMAL(10, 2), default=0)  # Physical inventory
    qty_reserved = Column(DECIMAL(10, 2), default=0)  # Reserved by SPK (not yet taken)

    # Audit
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="stock_quants")
    location = relationship("Location", back_populates="stock_quants")

    def get_available_qty(self) -> float:
        """Calculate available qty = on_hand - reserved."""
        return float(self.qty_on_hand - self.qty_reserved)

    def __repr__(self):
        return f"<StockQuant(product={self.product_id}, loc={self.location_id}, qty={self.qty_on_hand})>"


class StockLot(Base):
    """Stock Lots/Batches
    Tracks batches/rolls of material for traceability (FIFO).
    """

    __tablename__ = "stock_lots"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    lot_number = Column(String(50), unique=True, nullable=False, index=True)  # Roll number

    # Quantity
    qty_initial = Column(DECIMAL(10, 2), nullable=False)
    qty_remaining = Column(DECIMAL(10, 2), nullable=False)

    # Received from
    supplier_id = Column(Integer, ForeignKey("partners.id"), nullable=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)

    # Dates
    received_date = Column(DateTime(timezone=True), nullable=False)
    expiry_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    material_consumptions = relationship("MaterialConsumption", foreign_keys="MaterialConsumption.lot_id")

    def __repr__(self):
        return f"<StockLot(lot={self.lot_number}, qty={self.qty_remaining})>"


class MaterialRequest(Base):
    """Manual Material Requests
    Tracks requests for additional materials with approval workflow.
    Requires SPV or Manager warehouse approval.
    """

    __tablename__ = "material_requests"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=False, index=True)

    # Quantity requested
    qty_requested = Column(DECIMAL(10, 2), nullable=False)
    uom = Column(String(10), nullable=False)  # Pcs, Meter, Kg, Roll, etc.

    # Requester info
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())

    # Approval info
    approved_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(String(500), nullable=True)

    # Status
    status = Column(Enum(MaterialRequestStatus), default=MaterialRequestStatus.PENDING, nullable=False, index=True)

    # Purpose/notes
    purpose = Column(String(500), nullable=False)  # Why this material is needed

    # Completed by (after approval)
    received_by_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    received_at = Column(DateTime(timezone=True), nullable=True)

    # Tracking
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    location = relationship("Location", foreign_keys=[location_id])
    requester = relationship("User", foreign_keys=[requested_by_id])
    approver = relationship("User", foreign_keys=[approved_by_id])
    receiver = relationship("User", foreign_keys=[received_by_id])

    def __repr__(self):
        return f"<MaterialRequest(product={self.product_id}, qty={self.qty_requested}, status={self.status.value})>"
