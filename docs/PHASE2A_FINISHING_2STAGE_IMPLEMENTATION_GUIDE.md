# 🏭 PHASE 2A: WAREHOUSE FINISHING 2-STAGE - IMPLEMENTATION GUIDE

**Phase**: 2A (Weeks 6-7 of 12)  
**Complexity**: 🔴 CRITICAL  
**Impact**: 🟠 HIGH (affects production flow)  
**Dependency**: Phase 1 ✅ COMPLETE  
**Estimated Effort**: 3-4 days  
**Target Completion**: By end of Week 6

---

## 📋 OVERVIEW

Warehouse Finishing 2-Stage is a critical system for soft toy manufacturing. It tracks the filling process (Stuffing) and closing process (Closing) as separate production stages with separate inventory tracking.

### Current State (Without This System)
```
Sewing Output → Finished Goods Warehouse (incomplete - missing steps!)
```

### With This System
```
Sewing Output (Skin)
    ↓
Stage 1: Stuffing (Warehouse Finishing 1)
    ├─ Input: Skin from Sewing (50,000 pcs)
    ├─ Material: Filling (kapas) 500g/pcs
    ├─ Output: Stuffed Body (48,000 pcs - 96% yield)
    └─ Defect: 2,000 pcs (go to rework)
    ↓
Stage 2: Closing (Warehouse Finishing 2)
    ├─ Input: Stuffed Body (48,000 pcs)
    ├─ Material: Thread (0.5m/pcs)
    ├─ Output: Finished Doll (47,000 pcs - 97.9% final yield)
    └─ Defect: 1,000 pcs (go to rework)
    ↓
Finished Goods Stock
    └─ Ready for Packing
```

### Business Value
- **Visibility**: Track where products are in finishing process
- **Material Tracking**: Know exact filling consumption per piece
- **Yield Analysis**: Identify losses at each stage
- **Rework Trigger**: Auto-create rework tickets for defects
- **Demand-Driven**: Target based on Packing SPK needs

---

## 🗄️ DATABASE DESIGN

### New Tables (3 total)

#### 1. warehouse_finishing_stocks
Tracks inventory at each finishing stage

```sql
CREATE TABLE warehouse_finishing_stocks (
    id INTEGER PRIMARY KEY,
    stage INTEGER NOT NULL,  -- 1 (Stuffing) or 2 (Closing)
    product_id INTEGER FK,   -- WIP Product (Skin, Stuffed Body, Finished Doll)
    
    -- Quantity tracking
    good_qty DECIMAL(10,2),       -- Good pieces in stock
    defect_qty DECIMAL(10,2),     -- Defective pieces in stock
    total_qty DECIMAL(10,2),      -- good_qty + defect_qty
    
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    
    CONSTRAINT fk_product FOREIGN KEY (product_id) REFERENCES products(id),
    INDEX idx_stage (stage),
    INDEX idx_product (product_id)
);
```

#### 2. finishing_material_consumptions
Tracks material used in finishing (filling, thread)

```sql
CREATE TABLE finishing_material_consumptions (
    id INTEGER PRIMARY KEY,
    spk_id INTEGER FK,           -- Link to Finishing SPK
    stage INTEGER,               -- 1 (Stuffing) or 2 (Closing)
    material_id INTEGER FK,      -- Material consumed (filling, thread)
    
    -- Quantities
    qty_planned DECIMAL(12,3),   -- Planned consumption (from BOM)
    qty_actual DECIMAL(12,3),    -- Actual consumption (operator input)
    
    -- UOM
    uom VARCHAR(10),             -- KG, METER, GRAM
    
    -- Lot tracking
    lot_id INTEGER FK,           -- Which batch/roll used
    
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    
    CONSTRAINT fk_spk FOREIGN KEY (spk_id) REFERENCES spks(id),
    CONSTRAINT fk_material FOREIGN KEY (material_id) REFERENCES products(id),
    CONSTRAINT fk_lot FOREIGN KEY (lot_id) REFERENCES stock_lots(id),
    INDEX idx_spk (spk_id),
    INDEX idx_stage (stage),
    INDEX idx_material (material_id)
);
```

#### 3. finishing_inputs_outputs
Tracks daily input/output for each stage

```sql
CREATE TABLE finishing_inputs_outputs (
    id INTEGER PRIMARY KEY,
    spk_id INTEGER FK,           -- Link to Finishing SPK
    stage INTEGER,               -- 1 (Stuffing) or 2 (Closing)
    production_date DATE,        -- Production date
    
    -- Daily tracking
    input_qty DECIMAL(10,2),     -- Pieces received for processing
    good_qty DECIMAL(10,2),      -- Good output produced
    defect_qty DECIMAL(10,2),    -- Defective output
    rework_qty DECIMAL(10,2),    -- Sent to rework
    
    -- Metrics
    yield_rate DECIMAL(5,2),     -- % of good output (good/input * 100)
    
    -- Operator
    operator_id INTEGER FK,      -- Who performed the work
    
    -- Notes
    notes TEXT,                  -- Quality issues, problems
    
    -- Timestamps
    created_at DATETIME,
    updated_at DATETIME,
    
    CONSTRAINT fk_spk FOREIGN KEY (spk_id) REFERENCES spks(id),
    CONSTRAINT fk_operator FOREIGN KEY (operator_id) REFERENCES users(id),
    INDEX idx_spk (spk_id),
    INDEX idx_date (production_date),
    INDEX idx_stage (stage)
);
```

### WIP Products (in products table)
Three SKUs represent WIP stages:

```
Product Code: SEMI-SKIN-*
  ├─ Article Code: *-SKIN
  ├─ Name: "{Article} - Skin (WIP)"
  └─ Type: WIP

Product Code: SEMI-STUFFED-*
  ├─ Article Code: *-STUFFED
  ├─ Name: "{Article} - Stuffed Body (WIP)"
  └─ Type: WIP

Product Code: FINAL-FINISHED-*
  ├─ Article Code: *-FINISHED
  ├─ Name: "{Article} - Finished Doll (FG)"
  └─ Type: FINISHED_GOOD
```

---

## 📦 MODELS (Python/SQLAlchemy)

Create new file: `app/core/models/finishing.py`

```python
"""Warehouse Finishing 2-Stage Models"""

from decimal import Decimal
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Date
from sqlalchemy import DECIMAL, Enum as SQLEnum, TEXT, Boolean, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class FinishingStage(int, Enum):
    """Finishing stages"""
    STAGE_1_STUFFING = 1
    STAGE_2_CLOSING = 2


class WarehouseFinishingStock(Base):
    """Warehouse Finishing Stock - Inventory at each finishing stage"""
    
    __tablename__ = "warehouse_finishing_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    stage = Column(Integer, nullable=False, index=True, comment="1=Stuffing, 2=Closing")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Quantity tracking
    good_qty = Column(DECIMAL(10, 2), default=0, nullable=False)
    defect_qty = Column(DECIMAL(10, 2), default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    
    @property
    def total_qty(self) -> Decimal:
        """Total quantity in stock"""
        return self.good_qty + self.defect_qty


class FinishingMaterialConsumption(Base):
    """Material consumption in finishing (filling, thread)"""
    
    __tablename__ = "finishing_material_consumptions"
    
    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id"), nullable=False, index=True)
    stage = Column(Integer, nullable=False, index=True, comment="1=Stuffing, 2=Closing")
    material_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    # Quantities
    qty_planned = Column(DECIMAL(12, 3), nullable=False, comment="From BOM")
    qty_actual = Column(DECIMAL(12, 3), nullable=True, comment="Operator input")
    
    # UOM
    uom = Column(String(10), nullable=False, default="KG")  # KG, METER, GRAM, PCS
    
    # Lot tracking
    lot_id = Column(Integer, ForeignKey("stock_lots.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    spk = relationship("SPK", foreign_keys=[spk_id])
    material = relationship("Product", foreign_keys=[material_id])
    lot = relationship("StockLot", foreign_keys=[lot_id])


class FinishingInputOutput(Base):
    """Daily input/output tracking for finishing stages"""
    
    __tablename__ = "finishing_inputs_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("spks.id"), nullable=False, index=True)
    stage = Column(Integer, nullable=False, index=True, comment="1=Stuffing, 2=Closing")
    production_date = Column(Date, nullable=False, index=True)
    
    # Daily tracking
    input_qty = Column(DECIMAL(10, 2), nullable=False)
    good_qty = Column(DECIMAL(10, 2), nullable=False, default=0)
    defect_qty = Column(DECIMAL(10, 2), nullable=False, default=0)
    rework_qty = Column(DECIMAL(10, 2), nullable=False, default=0)
    
    # Metrics
    yield_rate = Column(DECIMAL(5, 2), nullable=True, comment="% good output")
    
    # Operator
    operator_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Notes
    notes = Column(TEXT, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    spk = relationship("SPK", foreign_keys=[spk_id])
    operator = relationship("User", foreign_keys=[operator_id])
    
    @property
    def produced_qty(self) -> Decimal:
        """Total produced (good + defect)"""
        return self.good_qty + self.defect_qty
    
    @property
    def loss_qty(self) -> Decimal:
        """Loss quantity (input - produced)"""
        return self.input_qty - self.produced_qty
```

---

## 🔧 SERVICES

Create new file: `app/modules/finishing/finishing_service.py`

```python
"""Warehouse Finishing Service - 2-Stage Processing"""

from decimal import Decimal
from datetime import date, datetime
from sqlalchemy.orm import Session

from app.core.models.manufacturing import SPK, Department
from app.core.models.finishing import (
    WarehouseFinishingStock,
    FinishingMaterialConsumption,
    FinishingInputOutput,
    FinishingStage
)
from app.shared.audit import log_audit


class FinishingService:
    """Business logic for warehouse finishing operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_stage1_spk(
        self,
        mo_id: int,
        target_qty: Decimal,
        buffer_pct: Decimal = Decimal('0'),
        user_id: int = None
    ) -> SPK:
        """Create Stage 1 (Stuffing) SPK for Warehouse Finishing
        
        Args:
            mo_id: Manufacturing Order ID
            target_qty: Base target quantity from Packing demand
            buffer_pct: Buffer percentage (default 0%)
            user_id: User creating SPK
        
        Returns:
            Created SPK for Stuffing stage
        """
        from app.core.models.manufacturing import ManufacturingOrder
        
        mo = self.db.query(ManufacturingOrder).filter_by(id=mo_id).first()
        if not mo:
            raise ValueError(f"MO {mo_id} not found")
        
        # Create SPK for Stuffing
        spk = SPK(
            mo_id=mo_id,
            department=Department.FINISHING,  # Using FINISHING for warehouse finishing
            original_qty=int(target_qty),
            buffer_percentage=buffer_pct,
            target_qty=int(target_qty * (1 + buffer_pct / 100)),
            production_status="NOT_STARTED",
            created_by_id=user_id,
            # Add finishing-specific tracking
            extra_metadata=f'{{"finishing_stage": 1, "stage_name": "Stuffing"}}'
        )
        
        self.db.add(spk)
        self.db.commit()
        
        if user_id:
            log_audit(self.db, user_id=user_id, action="CREATE_STAGE1_SPK",
                     entity_type="SPK", entity_id=spk.id,
                     changes={"stage": "Stuffing", "target_qty": int(target_qty)})
        
        return spk
    
    def create_stage2_spk(
        self,
        stage1_spk_id: int,
        target_qty: Decimal,
        user_id: int = None
    ) -> SPK:
        """Create Stage 2 (Closing) SPK based on Stage 1 output
        
        Args:
            stage1_spk_id: Stage 1 SPK ID (for linking)
            target_qty: Target for closing stage
            user_id: User creating SPK
        
        Returns:
            Created SPK for Closing stage
        """
        stage1_spk = self.db.query(SPK).filter_by(id=stage1_spk_id).first()
        if not stage1_spk:
            raise ValueError(f"Stage 1 SPK {stage1_spk_id} not found")
        
        # Create SPK for Closing
        spk = SPK(
            mo_id=stage1_spk.mo_id,
            department=Department.FINISHING,
            original_qty=int(target_qty),
            buffer_percentage=Decimal('0'),  # No buffer for closing
            target_qty=int(target_qty),
            production_status="NOT_STARTED",
            created_by_id=user_id,
            # Link to Stage 1
            extra_metadata=f'{{"finishing_stage": 2, "stage_name": "Closing", "prev_spk_id": {stage1_spk_id}}}'
        )
        
        self.db.add(spk)
        self.db.commit()
        
        if user_id:
            log_audit(self.db, user_id=user_id, action="CREATE_STAGE2_SPK",
                     entity_type="SPK", entity_id=spk.id,
                     changes={"stage": "Closing", "target_qty": int(target_qty),
                             "linked_to_stage1": stage1_spk_id})
        
        return spk
    
    def input_stage1_result(
        self,
        spk_id: int,
        input_qty: Decimal,
        good_qty: Decimal,
        defect_qty: Decimal,
        rework_qty: Decimal,
        filling_consumed: Decimal,
        operator_id: int,
        production_date: date = None,
        notes: str = None,
        user_id: int = None
    ) -> FinishingInputOutput:
        """Record Stage 1 (Stuffing) completion
        
        Args:
            spk_id: Stage 1 SPK ID
            input_qty: Pieces received for stuffing
            good_qty: Good stuffed bodies produced
            defect_qty: Defective output
            rework_qty: Units sent to rework
            filling_consumed: Filling (kapas) consumed in KG
            operator_id: Operator who did the work
            production_date: Date of production
            notes: Additional notes
            user_id: User recording the result
        
        Returns:
            Created FinishingInputOutput record
        """
        spk = self.db.query(SPK).filter_by(id=spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        if production_date is None:
            production_date = date.today()
        
        # Create input/output record
        io_record = FinishingInputOutput(
            spk_id=spk_id,
            stage=FinishingStage.STAGE_1_STUFFING,
            production_date=production_date,
            input_qty=input_qty,
            good_qty=good_qty,
            defect_qty=defect_qty,
            rework_qty=rework_qty,
            yield_rate=(good_qty / input_qty * 100) if input_qty > 0 else 0,
            operator_id=operator_id,
            notes=notes
        )
        
        self.db.add(io_record)
        
        # Update SPK status
        spk.produced_qty = good_qty + defect_qty
        spk.good_qty = good_qty
        spk.defect_qty = defect_qty
        spk.production_status = "COMPLETED"
        
        # Log filling consumption
        # (linking to material consumption in Phase 2B)
        
        self.db.commit()
        
        if user_id:
            log_audit(self.db, user_id=user_id, action="INPUT_STAGE1_RESULT",
                     entity_type="SPK", entity_id=spk_id,
                     changes={"good_qty": int(good_qty), "defect_qty": int(defect_qty),
                             "yield": float(io_record.yield_rate),
                             "filling_kg": float(filling_consumed)})
        
        return io_record
    
    def input_stage2_result(
        self,
        spk_id: int,
        input_qty: Decimal,
        good_qty: Decimal,
        defect_qty: Decimal,
        rework_qty: Decimal,
        thread_consumed: Decimal,
        operator_id: int,
        production_date: date = None,
        notes: str = None,
        user_id: int = None
    ) -> FinishingInputOutput:
        """Record Stage 2 (Closing) completion
        
        Args:
            spk_id: Stage 2 SPK ID
            input_qty: Stuffed bodies received for closing
            good_qty: Finished dolls produced
            defect_qty: Defective output
            rework_qty: Units sent to rework
            thread_consumed: Thread consumed in meters
            operator_id: Operator who did the work
            production_date: Date of production
            notes: Additional notes
            user_id: User recording the result
        
        Returns:
            Created FinishingInputOutput record
        """
        # Similar to Stage 1, but for closing stage
        spk = self.db.query(SPK).filter_by(id=spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        if production_date is None:
            production_date = date.today()
        
        io_record = FinishingInputOutput(
            spk_id=spk_id,
            stage=FinishingStage.STAGE_2_CLOSING,
            production_date=production_date,
            input_qty=input_qty,
            good_qty=good_qty,
            defect_qty=defect_qty,
            rework_qty=rework_qty,
            yield_rate=(good_qty / input_qty * 100) if input_qty > 0 else 0,
            operator_id=operator_id,
            notes=notes
        )
        
        self.db.add(io_record)
        
        # Update SPK status
        spk.produced_qty = good_qty + defect_qty
        spk.good_qty = good_qty
        spk.defect_qty = defect_qty
        spk.production_status = "COMPLETED"
        
        self.db.commit()
        
        if user_id:
            log_audit(self.db, user_id=user_id, action="INPUT_STAGE2_RESULT",
                     entity_type="SPK", entity_id=spk_id,
                     changes={"good_qty": int(good_qty), "defect_qty": int(defect_qty),
                             "yield": float(io_record.yield_rate),
                             "thread_m": float(thread_consumed)})
        
        return io_record
```

---

## 🔌 API ENDPOINTS

Create new file: `app/api/v1/finishing.py`

```python
"""Warehouse Finishing API Endpoints"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import date

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.modules.finishing.finishing_service import FinishingService

router = APIRouter(prefix="/api/v1/finishing", tags=["Finishing"])


@router.post("/stage1-spk")
def create_stage1_spk(
    mo_id: int,
    target_qty: int,
    buffer_pct: float = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create Stage 1 (Stuffing) SPK"""
    service = FinishingService(db)
    spk = service.create_stage1_spk(
        mo_id=mo_id,
        target_qty=Decimal(target_qty),
        buffer_pct=Decimal(buffer_pct),
        user_id=current_user.id
    )
    return {"id": spk.id, "stage": "Stuffing", "target_qty": spk.target_qty}


@router.post("/stage2-spk")
def create_stage2_spk(
    stage1_spk_id: int,
    target_qty: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create Stage 2 (Closing) SPK"""
    service = FinishingService(db)
    spk = service.create_stage2_spk(
        stage1_spk_id=stage1_spk_id,
        target_qty=Decimal(target_qty),
        user_id=current_user.id
    )
    return {"id": spk.id, "stage": "Closing", "target_qty": spk.target_qty}


@router.post("/stage1-input")
def input_stage1_result(
    spk_id: int,
    input_qty: int,
    good_qty: int,
    defect_qty: int,
    rework_qty: int,
    filling_kg: float,
    operator_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record Stage 1 (Stuffing) output"""
    service = FinishingService(db)
    record = service.input_stage1_result(
        spk_id=spk_id,
        input_qty=Decimal(input_qty),
        good_qty=Decimal(good_qty),
        defect_qty=Decimal(defect_qty),
        rework_qty=Decimal(rework_qty),
        filling_consumed=Decimal(filling_kg),
        operator_id=operator_id,
        notes=notes,
        user_id=current_user.id
    )
    return {
        "spk_id": spk_id,
        "stage": "Stuffing",
        "good_qty": int(record.good_qty),
        "defect_qty": int(record.defect_qty),
        "yield_rate": float(record.yield_rate)
    }


@router.post("/stage2-input")
def input_stage2_result(
    spk_id: int,
    input_qty: int,
    good_qty: int,
    defect_qty: int,
    rework_qty: int,
    thread_m: float,
    operator_id: int,
    notes: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Record Stage 2 (Closing) output"""
    service = FinishingService(db)
    record = service.input_stage2_result(
        spk_id=spk_id,
        input_qty=Decimal(input_qty),
        good_qty=Decimal(good_qty),
        defect_qty=Decimal(defect_qty),
        rework_qty=Decimal(rework_qty),
        thread_consumed=Decimal(thread_m),
        operator_id=operator_id,
        notes=notes,
        user_id=current_user.id
    )
    return {
        "spk_id": spk_id,
        "stage": "Closing",
        "good_qty": int(record.good_qty),
        "defect_qty": int(record.defect_qty),
        "yield_rate": float(record.yield_rate)
    }
```

---

## 💾 DATABASE MIGRATION

Create new file: `alembic/versions/011_warehouse_finishing_2stage.py`

```python
"""Create warehouse finishing 2-stage tables - Phase 2A

Revision ID: 011
Revises: 010
Create Date: 2026-02-05

This migration creates the infrastructure for the 2-stage finishing process:
1. Stage 1: Stuffing (Input: Skin, Output: Stuffed Body)
2. Stage 2: Closing (Input: Stuffed Body, Output: Finished Doll)
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    # Create warehouse_finishing_stocks table
    op.create_table(
        'warehouse_finishing_stocks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.Integer(), nullable=False, comment='1=Stuffing, 2=Closing'),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('good_qty', sa.Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('defect_qty', sa.Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_stage', 'warehouse_finishing_stocks', ['stage'])
    op.create_index('idx_product', 'warehouse_finishing_stocks', ['product_id'])
    
    # Create finishing_material_consumptions table
    op.create_table(
        'finishing_material_consumptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spk_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.Integer(), nullable=False, comment='1=Stuffing, 2=Closing'),
        sa.Column('material_id', sa.Integer(), nullable=False),
        sa.Column('qty_planned', sa.Numeric(12, 3), nullable=False),
        sa.Column('qty_actual', sa.Numeric(12, 3)),
        sa.Column('uom', sa.String(10), server_default='KG', nullable=False),
        sa.Column('lot_id', sa.Integer()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['spk_id'], ['spks.id'], ),
        sa.ForeignKeyConstraint(['material_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['lot_id'], ['stock_lots.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_spk', 'finishing_material_consumptions', ['spk_id'])
    op.create_index('idx_stage', 'finishing_material_consumptions', ['stage'])
    op.create_index('idx_material', 'finishing_material_consumptions', ['material_id'])
    
    # Create finishing_inputs_outputs table
    op.create_table(
        'finishing_inputs_outputs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('spk_id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.Integer(), nullable=False, comment='1=Stuffing, 2=Closing'),
        sa.Column('production_date', sa.Date(), nullable=False),
        sa.Column('input_qty', sa.Numeric(10, 2), nullable=False),
        sa.Column('good_qty', sa.Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('defect_qty', sa.Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('rework_qty', sa.Numeric(10, 2), server_default='0', nullable=False),
        sa.Column('yield_rate', sa.Numeric(5, 2)),
        sa.Column('operator_id', sa.Integer()),
        sa.Column('notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.ForeignKeyConstraint(['spk_id'], ['spks.id'], ),
        sa.ForeignKeyConstraint(['operator_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_spk', 'finishing_inputs_outputs', ['spk_id'])
    op.create_index('idx_date', 'finishing_inputs_outputs', ['production_date'])
    op.create_index('idx_stage', 'finishing_inputs_outputs', ['stage'])


def downgrade():
    op.drop_index('idx_stage', table_name='finishing_inputs_outputs')
    op.drop_index('idx_date', table_name='finishing_inputs_outputs')
    op.drop_index('idx_spk', table_name='finishing_inputs_outputs')
    op.drop_table('finishing_inputs_outputs')
    
    op.drop_index('idx_material', table_name='finishing_material_consumptions')
    op.drop_index('idx_stage', table_name='finishing_material_consumptions')
    op.drop_index('idx_spk', table_name='finishing_material_consumptions')
    op.drop_table('finishing_material_consumptions')
    
    op.drop_index('idx_product', table_name='warehouse_finishing_stocks')
    op.drop_index('idx_stage', table_name='warehouse_finishing_stocks')
    op.drop_table('warehouse_finishing_stocks')
```

---

## ✅ IMPLEMENTATION CHECKLIST

### Models & Database
- [ ] Create `app/core/models/finishing.py` with 3 model classes
- [ ] Create migration `011_warehouse_finishing_2stage.py`
- [ ] Run migration: `alembic upgrade head`
- [ ] Verify tables created in database

### Services
- [ ] Create `app/modules/finishing/finishing_service.py`
- [ ] Implement FinishingService with 4 main methods:
  - [ ] create_stage1_spk()
  - [ ] create_stage2_spk()
  - [ ] input_stage1_result()
  - [ ] input_stage2_result()
- [ ] Add audit logging to all methods
- [ ] Test service methods with sample data

### API
- [ ] Create `app/api/v1/finishing.py`
- [ ] Implement 4 endpoints:
  - [ ] POST /stage1-spk
  - [ ] POST /stage2-spk
  - [ ] POST /stage1-input
  - [ ] POST /stage2-input
- [ ] Add authentication/authorization
- [ ] Test endpoints with Postman/curl

### Testing
- [ ] Create `tests/test_phase2a_finishing.py`
- [ ] Write unit tests for service methods (8+ tests)
- [ ] Write integration tests (6+ tests)
- [ ] Achieve 90%+ code coverage

### Integration
- [ ] Update Packing SPK creation to trigger Stage 1/2 SPKs
- [ ] Update Rework service (Phase 2B) to accept finishing defects
- [ ] Update Dashboard to show finishing stage status
- [ ] Document API endpoints in Swagger/OpenAPI

---

## 🎯 SUCCESS CRITERIA

### Functional
- ✅ Can create 2-stage finishing SPKs
- ✅ Can record daily input/output with yield tracking
- ✅ Material consumption properly tracked
- ✅ Defects auto-trigger rework tickets (Phase 2B integration)
- ✅ Finished goods available for packing

### Technical
- ✅ 90%+ code coverage
- ✅ All SQL queries optimized (<100ms)
- ✅ Proper foreign key constraints
- ✅ Audit trail complete
- ✅ Error handling robust

### Business
- ✅ Yield analysis available (daily reports)
- ✅ Material tracking precise (KG level for filling)
- ✅ Visibility into finishing bottlenecks
- ✅ Rework queue automatically managed

---

## 📚 RESOURCES

- **Related Files**:
  - [PHASE1_COMPLETION_REPORT.md](PHASE1_COMPLETION_REPORT.md)
  - [IMPLEMENTATION_ROADMAP_PHASE2_PLUS.md](../IMPLEMENTATION_ROADMAP_PHASE2_PLUS.md)
  - [app/core/models/manufacturing.py](../../erp-softtoys/app/core/models/manufacturing.py)

- **Dependencies**:
  - Phase 1 complete ✅
  - SPK model (from Phase 1) ✅
  - Department enum (from Phase 1) ✅

---

**Document Version**: 1.0  
**Ready to Start**: ✅ YES  
**Estimated Effort**: 3-4 days  
**Target Completion**: End of Week 6
