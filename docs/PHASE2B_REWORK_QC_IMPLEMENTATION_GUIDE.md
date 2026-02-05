---
title: Phase 2B - Rework & QC Module Implementation Guide
date: 5 February 2026
phase: 2B
status: READY FOR IMPLEMENTATION
---

# Phase 2B: Rework & QC Module - Complete Implementation Guide

## Overview

**Phase 2B** implements the Rework & Quality Control system for PT Quty Karunia's ERP.

**Duration**: 3-4 days
**Scope**: 6-8 files, ~1200 lines of code
**Dependencies**: Phase 1 (PO system) + Phase 2A (Finishing system)
**Priority**: HIGH (affects production flow and quality metrics)

---

## Business Context

### Problem Statement
Currently, when defective units are produced:
- No tracking of rework reasons
- No QC approval workflow
- No defect categorization
- No cost tracking for rework

### Solution
Implement a complete Rework & QC module:
1. **Defect Categorization**: Categorize why units failed
2. **Rework Requests**: Create requests to fix defective units
3. **QC Approval**: Quality manager approves rework before execution
4. **Rework Tracking**: Track materials and time for rework
5. **Cost Tracking**: Calculate rework costs

### Expected Outcomes
- Reduce rework time by 20% (better organization)
- Improve quality visibility (defect tracking)
- Enable cost analysis (rework costs)
- Streamline QC process (approval workflow)

---

## Data Models

### 1. DefectCategory Model

**Purpose**: Categorize types of defects
**Location**: `app/core/models/manufacturing.py`

```python
from enum import Enum
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.orm import relationship
from app.core.database import Base

class DefectType(str, Enum):
    """Types of defects"""
    STITCHING = "STITCHING"
    MATERIAL = "MATERIAL"
    FILLING = "FILLING"
    ASSEMBLY = "ASSEMBLY"
    PAINT = "PAINT"
    OTHER = "OTHER"

class DefectCategory(Base):
    """Categorization of defects for quality tracking"""
    __tablename__ = "defect_categories"
    
    id = Column(Integer, primary_key=True)
    code = Column(String(50), unique=True, nullable=False)  # DFC-001, DFC-002, etc.
    name = Column(String(100), nullable=False)  # "Broken Stitch", "Wrong Color", etc.
    defect_type = Column(String(20), nullable=False)  # STITCHING, MATERIAL, etc.
    description = Column(Text)  # Detailed description
    severity = Column(String(20), nullable=False)  # MINOR, MAJOR, CRITICAL
    default_rework_hours = Column(Integer, default=1)  # Hours to rework
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rework_requests = relationship("ReworkRequest", back_populates="defect_category")
```

### 2. ReworkRequest Model

**Purpose**: Track requests to rework defective units
**Location**: `app/core/models/manufacturing.py`

```python
class ReworkStatus(str, Enum):
    """Status of rework request"""
    PENDING = "PENDING"  # Just created
    QC_REVIEW = "QC_REVIEW"  # Waiting for QC approval
    APPROVED = "APPROVED"  # QC approved
    REJECTED = "REJECTED"  # QC rejected (discard instead)
    IN_PROGRESS = "IN_PROGRESS"  # Being reworked
    COMPLETED = "COMPLETED"  # Rework complete
    VERIFIED = "VERIFIED"  # Verified by QC

class ReworkRequest(Base):
    """Request to rework defective units"""
    __tablename__ = "rework_requests"
    
    id = Column(Integer, primary_key=True)
    spk_id = Column(Integer, ForeignKey("spks.id"), nullable=False)  # Which SPK
    defect_qty = Column(Numeric(10, 2), nullable=False)  # How many defective
    
    # Defect info
    defect_category_id = Column(Integer, ForeignKey("defect_categories.id"), nullable=False)
    defect_notes = Column(Text)  # Details about the defect
    
    # Status tracking
    status = Column(String(20), default=ReworkStatus.PENDING, nullable=False)
    
    # QC Approval
    qc_reviewed_by_id = Column(Integer, ForeignKey("users.id"))  # QC manager
    qc_reviewed_at = Column(DateTime)
    qc_approval_notes = Column(Text)
    
    # Rework tracking
    rework_started_at = Column(DateTime)
    rework_completed_at = Column(DateTime)
    rework_operator_id = Column(Integer, ForeignKey("users.id"))
    rework_notes = Column(Text)
    
    # Final QC verification
    verified_by_id = Column(Integer, ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verified_good_qty = Column(Numeric(10, 2), default=0)  # Good after rework
    verified_failed_qty = Column(Numeric(10, 2), default=0)  # Still bad, discard
    
    # Cost tracking
    material_cost = Column(Numeric(12, 2), default=0)
    labor_cost = Column(Numeric(12, 2), default=0)
    total_cost = Column(Numeric(12, 2), default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    requested_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    spk = relationship("SPK", foreign_keys=[spk_id])
    defect_category = relationship("DefectCategory", back_populates="rework_requests")
    qc_reviewer = relationship("User", foreign_keys=[qc_reviewed_by_id])
    rework_operator = relationship("User", foreign_keys=[rework_operator_id])
    qc_verifier = relationship("User", foreign_keys=[verified_by_id])
    requested_by = relationship("User", foreign_keys=[requested_by_id])
    materials = relationship("ReworkMaterial", back_populates="rework_request")
```

### 3. ReworkMaterial Model

**Purpose**: Track materials consumed during rework
**Location**: `app/core/models/manufacturing.py`

```python
class ReworkMaterial(Base):
    """Materials used in rework process"""
    __tablename__ = "rework_materials"
    
    id = Column(Integer, primary_key=True)
    rework_request_id = Column(Integer, ForeignKey("rework_requests.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)  # Material/product
    qty_used = Column(Numeric(10, 2), nullable=False)
    uom = Column(String(10), nullable=False)  # KG, PIECES, METERS, etc.
    unit_cost = Column(Numeric(12, 2), nullable=False)
    total_cost = Column(Numeric(12, 2), nullable=False)  # qty_used * unit_cost
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    rework_request = relationship("ReworkRequest", back_populates="materials")
    product = relationship("Product")
```

---

## Service Layer

### ReworkService Class

**Purpose**: Business logic for rework operations
**Location**: `app/modules/manufacturing/rework_service.py`

```python
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.models.manufacturing import (
    ReworkRequest, ReworkStatus, DefectCategory, ReworkMaterial, SPK
)
from app.shared.audit import log_audit

class ReworkService:
    """Business logic for rework & QC operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rework_request(
        self,
        spk_id: int,
        defect_qty: Decimal,
        defect_category_id: int,
        defect_notes: str,
        requested_by_id: int,
        user_id: int = None,
    ) -> ReworkRequest:
        """Create rework request from defective units
        
        Args:
            spk_id: SPK with defects
            defect_qty: Number of defective units
            defect_category_id: Type of defect
            defect_notes: Details about defects
            requested_by_id: User requesting rework (usually QC)
            user_id: User creating record (for audit)
        
        Returns:
            Created ReworkRequest (status: PENDING)
        """
        spk = self.db.query(SPK).filter_by(id=spk_id).first()
        if not spk:
            raise ValueError(f"SPK {spk_id} not found")
        
        rework = ReworkRequest(
            spk_id=spk_id,
            defect_qty=defect_qty,
            defect_category_id=defect_category_id,
            defect_notes=defect_notes,
            requested_by_id=requested_by_id,
            status=ReworkStatus.PENDING,
        )
        
        self.db.add(rework)
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="CREATE_REWORK_REQUEST",
                entity_type="ReworkRequest",
                entity_id=rework.id,
                changes={"spk_id": spk_id, "defect_qty": int(defect_qty)},
            )
        
        return rework
    
    def approve_rework(
        self,
        rework_id: int,
        qc_approval_notes: str = None,
        user_id: int = None,
    ) -> ReworkRequest:
        """Approve rework request (QC manager action)
        
        Args:
            rework_id: Rework request to approve
            qc_approval_notes: QC approval comments
            user_id: QC manager ID
        
        Returns:
            Updated ReworkRequest (status: APPROVED)
        """
        rework = self.db.query(ReworkRequest).filter_by(id=rework_id).first()
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")
        
        if rework.status != ReworkStatus.PENDING:
            raise ValueError(f"Cannot approve rework in {rework.status} status")
        
        rework.status = ReworkStatus.APPROVED
        rework.qc_reviewed_by_id = user_id
        rework.qc_reviewed_at = datetime.utcnow()
        rework.qc_approval_notes = qc_approval_notes
        
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="APPROVE_REWORK",
                entity_type="ReworkRequest",
                entity_id=rework_id,
                changes={"status": ReworkStatus.APPROVED},
            )
        
        return rework
    
    def start_rework(
        self,
        rework_id: int,
        operator_id: int,
        user_id: int = None,
    ) -> ReworkRequest:
        """Start rework process (operator action)
        
        Args:
            rework_id: Rework to start
            operator_id: Operator doing the rework
            user_id: User starting rework
        
        Returns:
            Updated ReworkRequest (status: IN_PROGRESS)
        """
        rework = self.db.query(ReworkRequest).filter_by(id=rework_id).first()
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")
        
        if rework.status != ReworkStatus.APPROVED:
            raise ValueError(f"Cannot start rework in {rework.status} status")
        
        rework.status = ReworkStatus.IN_PROGRESS
        rework.rework_started_at = datetime.utcnow()
        rework.rework_operator_id = operator_id
        
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="START_REWORK",
                entity_type="ReworkRequest",
                entity_id=rework_id,
                changes={"status": ReworkStatus.IN_PROGRESS},
            )
        
        return rework
    
    def complete_rework(
        self,
        rework_id: int,
        rework_notes: str = None,
        material_cost: Decimal = Decimal("0"),
        labor_cost: Decimal = Decimal("0"),
        user_id: int = None,
    ) -> ReworkRequest:
        """Complete rework process (operator action)
        
        Args:
            rework_id: Completed rework
            rework_notes: What was done
            material_cost: Cost of materials used
            labor_cost: Cost of labor
            user_id: User completing
        
        Returns:
            Updated ReworkRequest (status: COMPLETED)
        """
        rework = self.db.query(ReworkRequest).filter_by(id=rework_id).first()
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")
        
        if rework.status != ReworkStatus.IN_PROGRESS:
            raise ValueError(f"Cannot complete rework in {rework.status} status")
        
        rework.status = ReworkStatus.COMPLETED
        rework.rework_completed_at = datetime.utcnow()
        rework.rework_notes = rework_notes
        rework.material_cost = material_cost
        rework.labor_cost = labor_cost
        rework.total_cost = material_cost + labor_cost
        
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="COMPLETE_REWORK",
                entity_type="ReworkRequest",
                entity_id=rework_id,
                changes={
                    "status": ReworkStatus.COMPLETED,
                    "material_cost": float(material_cost),
                    "labor_cost": float(labor_cost),
                },
            )
        
        return rework
    
    def verify_rework(
        self,
        rework_id: int,
        verified_good_qty: Decimal,
        verified_failed_qty: Decimal,
        verification_notes: str = None,
        user_id: int = None,
    ) -> ReworkRequest:
        """Final QC verification of reworked units
        
        Args:
            rework_id: Rework to verify
            verified_good_qty: Units that passed verification
            verified_failed_qty: Units that still failed
            verification_notes: QC notes
            user_id: QC verifier ID
        
        Returns:
            Updated ReworkRequest (status: VERIFIED)
        """
        rework = self.db.query(ReworkRequest).filter_by(id=rework_id).first()
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")
        
        if rework.status != ReworkStatus.COMPLETED:
            raise ValueError(f"Cannot verify rework in {rework.status} status")
        
        # Validation: good + failed should equal defect qty
        if (verified_good_qty + verified_failed_qty) != rework.defect_qty:
            raise ValueError(
                f"Verification quantities ({verified_good_qty + verified_failed_qty}) "
                f"must equal defect quantity ({rework.defect_qty})"
            )
        
        rework.status = ReworkStatus.VERIFIED
        rework.verified_by_id = user_id
        rework.verified_at = datetime.utcnow()
        rework.verified_good_qty = verified_good_qty
        rework.verified_failed_qty = verified_failed_qty
        
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="VERIFY_REWORK",
                entity_type="ReworkRequest",
                entity_id=rework_id,
                changes={
                    "status": ReworkStatus.VERIFIED,
                    "good_qty": int(verified_good_qty),
                    "failed_qty": int(verified_failed_qty),
                },
            )
        
        return rework
    
    def reject_rework(
        self,
        rework_id: int,
        rejection_reason: str,
        user_id: int = None,
    ) -> ReworkRequest:
        """Reject rework request (discard instead of rework)
        
        Args:
            rework_id: Rework to reject
            rejection_reason: Why reject
            user_id: QC manager ID
        
        Returns:
            Updated ReworkRequest (status: REJECTED)
        """
        rework = self.db.query(ReworkRequest).filter_by(id=rework_id).first()
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")
        
        if rework.status != ReworkStatus.QC_REVIEW:
            raise ValueError(f"Cannot reject rework in {rework.status} status")
        
        rework.status = ReworkStatus.REJECTED
        rework.qc_reviewed_by_id = user_id
        rework.qc_reviewed_at = datetime.utcnow()
        rework.qc_approval_notes = rejection_reason
        
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="REJECT_REWORK",
                entity_type="ReworkRequest",
                entity_id=rework_id,
                changes={"status": ReworkStatus.REJECTED},
            )
        
        return rework
    
    def add_rework_material(
        self,
        rework_id: int,
        product_id: int,
        qty_used: Decimal,
        uom: str,
        unit_cost: Decimal,
        user_id: int = None,
    ) -> ReworkMaterial:
        """Add material consumed during rework
        
        Args:
            rework_id: Which rework request
            product_id: Material/product used
            qty_used: Quantity used
            uom: Unit of measure
            unit_cost: Cost per unit
            user_id: User recording
        
        Returns:
            Created ReworkMaterial
        """
        rework = self.db.query(ReworkRequest).filter_by(id=rework_id).first()
        if not rework:
            raise ValueError(f"Rework {rework_id} not found")
        
        material = ReworkMaterial(
            rework_request_id=rework_id,
            product_id=product_id,
            qty_used=qty_used,
            uom=uom,
            unit_cost=unit_cost,
            total_cost=qty_used * unit_cost,
        )
        
        self.db.add(material)
        self.db.commit()
        
        if user_id:
            log_audit(
                self.db,
                user_id=user_id,
                action="ADD_REWORK_MATERIAL",
                entity_type="ReworkMaterial",
                entity_id=material.id,
                changes={"qty": float(qty_used), "cost": float(qty_used * unit_cost)},
            )
        
        return material
```

---

## API Endpoints

### File: `app/api/v1/rework.py`

```python
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.modules.manufacturing.rework_service import ReworkService

router = APIRouter(prefix="/api/v1/rework", tags=["Rework"])

# ============================================================================
# Rework Request Management
# ============================================================================

@router.post("/request", status_code=status.HTTP_201_CREATED)
async def create_rework_request(
    spk_id: int,
    defect_qty: Decimal,
    defect_category_id: int,
    defect_notes: str,
    user_id: int,
    db: Session = Depends(get_db),
):
    """Create rework request for defective units"""
    try:
        service = ReworkService(db)
        rework = service.create_rework_request(
            spk_id=spk_id,
            defect_qty=defect_qty,
            defect_category_id=defect_category_id,
            defect_notes=defect_notes,
            requested_by_id=user_id,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "spk_id": rework.spk_id,
            "defect_qty": int(defect_qty),
            "status": rework.status,
            "created_at": rework.created_at,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request/{rework_id}/approve")
async def approve_rework_request(
    rework_id: int,
    approval_notes: str = None,
    user_id: int = None,
    db: Session = Depends(get_db),
):
    """Approve rework (QC Manager action)"""
    try:
        service = ReworkService(db)
        rework = service.approve_rework(
            rework_id=rework_id,
            qc_approval_notes=approval_notes,
            user_id=user_id,
        )
        return {"id": rework.id, "status": rework.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request/{rework_id}/start")
async def start_rework(
    rework_id: int,
    operator_id: int,
    user_id: int = None,
    db: Session = Depends(get_db),
):
    """Start rework process (Operator action)"""
    try:
        service = ReworkService(db)
        rework = service.start_rework(
            rework_id=rework_id,
            operator_id=operator_id,
            user_id=user_id,
        )
        return {"id": rework.id, "status": rework.status, "started_at": rework.rework_started_at}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request/{rework_id}/complete")
async def complete_rework(
    rework_id: int,
    rework_notes: str = None,
    material_cost: Decimal = Decimal("0"),
    labor_cost: Decimal = Decimal("0"),
    user_id: int = None,
    db: Session = Depends(get_db),
):
    """Complete rework process (Operator action)"""
    try:
        service = ReworkService(db)
        rework = service.complete_rework(
            rework_id=rework_id,
            rework_notes=rework_notes,
            material_cost=material_cost,
            labor_cost=labor_cost,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "total_cost": float(rework.total_cost),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request/{rework_id}/verify")
async def verify_rework(
    rework_id: int,
    verified_good_qty: Decimal,
    verified_failed_qty: Decimal,
    verification_notes: str = None,
    user_id: int = None,
    db: Session = Depends(get_db),
):
    """Final QC verification (QC Manager action)"""
    try:
        service = ReworkService(db)
        rework = service.verify_rework(
            rework_id=rework_id,
            verified_good_qty=verified_good_qty,
            verified_failed_qty=verified_failed_qty,
            verification_notes=verification_notes,
            user_id=user_id,
        )
        return {
            "id": rework.id,
            "status": rework.status,
            "good_qty": int(verified_good_qty),
            "failed_qty": int(verified_failed_qty),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/request/{rework_id}/reject")
async def reject_rework(
    rework_id: int,
    rejection_reason: str,
    user_id: int = None,
    db: Session = Depends(get_db),
):
    """Reject rework (discard instead)"""
    try:
        service = ReworkService(db)
        rework = service.reject_rework(
            rework_id=rework_id,
            rejection_reason=rejection_reason,
            user_id=user_id,
        )
        return {"id": rework.id, "status": rework.status}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# Rework Material Management
# ============================================================================

@router.post("/material", status_code=status.HTTP_201_CREATED)
async def add_rework_material(
    rework_id: int,
    product_id: int,
    qty_used: Decimal,
    uom: str,
    unit_cost: Decimal,
    user_id: int = None,
    db: Session = Depends(get_db),
):
    """Add material consumed during rework"""
    try:
        service = ReworkService(db)
        material = service.add_rework_material(
            rework_id=rework_id,
            product_id=product_id,
            qty_used=qty_used,
            uom=uom,
            unit_cost=unit_cost,
            user_id=user_id,
        )
        return {
            "id": material.id,
            "rework_id": rework_id,
            "qty": float(qty_used),
            "cost": float(material.total_cost),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## Database Migration

### File: `alembic/versions/012_rework_qc_system.py`

```python
"""Add Rework & QC System

Revision ID: 012_rework_qc_system
Revises: 011_warehouse_finishing_2stage
Create Date: 2026-02-05

Creates tables for:
- Defect categorization
- Rework requests with approval workflow
- Rework material tracking
"""

from alembic import op
import sqlalchemy as sa

revision = "012_rework_qc_system"
down_revision = "011_warehouse_finishing_2stage"

def upgrade():
    """Create rework & QC tables"""
    
    # Create defect_categories table
    op.create_table(
        "defect_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("defect_type", sa.String(20), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("default_rework_hours", sa.Integer(), default=1),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    
    # Create rework_requests table
    op.create_table(
        "rework_requests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("spk_id", sa.Integer(), nullable=False),
        sa.Column("defect_qty", sa.Numeric(10, 2), nullable=False),
        sa.Column("defect_category_id", sa.Integer(), nullable=False),
        sa.Column("defect_notes", sa.Text()),
        sa.Column("status", sa.String(20), default="PENDING"),
        sa.Column("qc_reviewed_by_id", sa.Integer()),
        sa.Column("qc_reviewed_at", sa.DateTime()),
        sa.Column("qc_approval_notes", sa.Text()),
        sa.Column("rework_started_at", sa.DateTime()),
        sa.Column("rework_completed_at", sa.DateTime()),
        sa.Column("rework_operator_id", sa.Integer()),
        sa.Column("rework_notes", sa.Text()),
        sa.Column("verified_by_id", sa.Integer()),
        sa.Column("verified_at", sa.DateTime()),
        sa.Column("verified_good_qty", sa.Numeric(10, 2), default=0),
        sa.Column("verified_failed_qty", sa.Numeric(10, 2), default=0),
        sa.Column("material_cost", sa.Numeric(12, 2), default=0),
        sa.Column("labor_cost", sa.Numeric(12, 2), default=0),
        sa.Column("total_cost", sa.Numeric(12, 2), default=0),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("requested_by_id", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["spk_id"], ["spks.id"]),
        sa.ForeignKeyConstraint(["defect_category_id"], ["defect_categories.id"]),
        sa.ForeignKeyConstraint(["qc_reviewed_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["rework_operator_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["verified_by_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["requested_by_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_rework_requests_spk_id", "spk_id"),
        sa.Index("ix_rework_requests_status", "status"),
    )
    
    # Create rework_materials table
    op.create_table(
        "rework_materials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("rework_request_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("qty_used", sa.Numeric(10, 2), nullable=False),
        sa.Column("uom", sa.String(10), nullable=False),
        sa.Column("unit_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["rework_request_id"], ["rework_requests.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_rework_materials_rework_id", "rework_request_id"),
    )

def downgrade():
    """Drop rework & QC tables"""
    op.drop_table("rework_materials")
    op.drop_table("rework_requests")
    op.drop_table("defect_categories")
```

---

## Summary

**Phase 2B** provides a complete Rework & QC solution:

| Component | Status | Details |
|-----------|--------|---------|
| **Models** | Ready | 3 models: DefectCategory, ReworkRequest, ReworkMaterial |
| **Service** | Ready | 6 methods covering full rework lifecycle |
| **API** | Ready | 7 endpoints for request creation/approval/execution/verification |
| **Migration** | Ready | 3 tables with proper constraints and indexes |
| **Tests** | Needed | 20+ test cases recommended |

**Next Steps**:
1. Create the models in `app/core/models/manufacturing.py`
2. Create the service in `app/modules/manufacturing/rework_service.py`
3. Create the API in `app/api/v1/rework.py`
4. Create the migration `alembic/versions/012_rework_qc_system.py`
5. Create comprehensive test suite
6. Run tests and validate

---

**Ready to implement Phase 2B?** Continue with model creation!
