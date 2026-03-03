"""Quality Control Models."""

import enum

from sqlalchemy import NUMERIC, TEXT, Column, DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class TestType(str, enum.Enum):
    """QC Lab Test Types."""

    DROP_TEST = "Drop Test"
    STABILITY_10 = "Stability 10"
    STABILITY_27 = "Stability 27"
    SEAM_STRENGTH = "Seam Strength"


class TestResult(str, enum.Enum):
    """Test result."""

    PASS = "Pass"
    FAIL = "Fail"


class QCInspectionType(str, enum.Enum):
    """QC Inspection types."""

    INCOMING = "Incoming"
    INLINE_SEWING = "Inline Sewing"
    FINAL_METAL_DETECTOR = "Final Metal Detector"


class QCStatus(str, enum.Enum):
    """Inspection status."""

    PASS = "Pass"
    FAIL = "Fail"


class QCLabTest(Base):
    """QC Lab Testing Results
    Gap Fix #5: Changed measured_value from FLOAT to NUMERIC for ISO precision.
    """

    __tablename__ = "qc_lab_tests"

    id = Column(Integer, primary_key=True, index=True)
    batch_number = Column(String(50), nullable=False, index=True)  # Link to Lot Produksi

    # Test specification
    test_type = Column(Enum(TestType), nullable=False, index=True)
    test_result = Column(Enum(TestResult), nullable=False, index=True)

    # Measurement (Gap Fix #5: NUMERIC for precision)
    measured_value = Column(NUMERIC(10, 2), nullable=True)  # e.g., kekuatan tarik value
    measured_unit = Column(String(20), nullable=True)  # e.g., "Newton", "cm", "%"
    iso_standard = Column(String(50), nullable=True)  # e.g., "ISO 8124"
    test_location = Column(String(100), nullable=True)  # e.g., "Seam AB", "Corner X"

    # Inspector
    inspector_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Evidence
    evidence_photo_url = Column(String(500), nullable=True)  # Photo if Fail

    # Audit
    tested_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    inspector = relationship("User", foreign_keys=[inspector_id])

    def __repr__(self):
        return f"<QCLabTest(test={self.test_type.value}, result={self.test_result.value})>"


class QCCheckpointType(str, enum.Enum):
    """4-Checkpoint QC types (matches frontend)."""

    AFTER_CUTTING = "AFTER_CUTTING"
    AFTER_SEWING = "AFTER_SEWING"
    AFTER_FINISHING = "AFTER_FINISHING"
    PRE_PACKING = "PRE_PACKING"


class QCCheckpoint(Base):
    """QC 4-Checkpoint records per SPK.
    Inline quality inspection at each production stage.
    """

    __tablename__ = "qc_checkpoints"

    id = Column(Integer, primary_key=True, index=True)
    spk_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)

    # Checkpoint type
    checkpoint = Column(Enum(QCCheckpointType), nullable=False, index=True)

    # Quantities
    inspected_qty = Column(Integer, nullable=False)
    pass_qty = Column(Integer, nullable=False, default=0)
    fail_qty = Column(Integer, nullable=False, default=0)

    # Defect info
    defect_type = Column(String(255), nullable=True)
    defect_description = Column(TEXT, nullable=True)

    # Inspector
    inspector_name = Column(String(255), nullable=False)
    inspected_by = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Date
    inspection_date = Column(String(20), nullable=True)
    notes = Column(TEXT, nullable=True)

    # Computed
    first_pass_yield = Column(NUMERIC(5, 2), nullable=True)

    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    spk = relationship("WorkOrder", foreign_keys=[spk_id])
    inspector = relationship("User", foreign_keys=[inspected_by])

    def __repr__(self):
        return f"<QCCheckpoint(spk={self.spk_id}, checkpoint={self.checkpoint.value}, fpy={self.first_pass_yield}%)>"


class QCInspection(Base):
    """QC Inspections - Pass/Fail at various stages
    Inline inspection, metal detector, final QC.
    """

    __tablename__ = "qc_inspections"

    id = Column(Integer, primary_key=True, index=True)
    work_order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)

    # Inspection type
    type = Column(Enum(QCInspectionType), nullable=False, index=True)
    status = Column(Enum(QCStatus), nullable=False, index=True)

    # Defect tracking
    defect_reason = Column(TEXT, nullable=True)  # e.g., "Jahitan loncat", "Jarum patah", "Logam ditemukan"
    defect_location = Column(String(255), nullable=True)  # Where on the product
    defect_qty = Column(Integer, default=1)  # How many defects

    # Inspector
    inspected_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Audit
    inspected_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    work_order = relationship("WorkOrder", back_populates="qc_inspections")
    inspector = relationship("User", foreign_keys=[inspected_by])

    def __repr__(self):
        return f"<QCInspection(type={self.type.value}, status={self.status.value})>"
