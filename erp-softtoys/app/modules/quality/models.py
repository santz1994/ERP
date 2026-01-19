"""
Quality Control Module - Pydantic Schemas
Request/Response models for QC operations
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum


class TestType(str, Enum):
    """QC Lab Test Types"""
    DROP_TEST = "Drop Test"
    STABILITY_10 = "Stability 10"
    STABILITY_27 = "Stability 27"
    SEAM_STRENGTH = "Seam Strength"
    METAL_DETECTOR = "Metal Detector"


class TestResult(str, Enum):
    """Test result"""
    PASS = "Pass"
    FAIL = "Fail"


class QCInspectionType(str, Enum):
    """QC Inspection types"""
    INCOMING = "Incoming"
    INLINE_SEWING = "Inline Sewing"
    FINAL_METAL_DETECTOR = "Final Metal Detector"


# QC Lab Test Schemas
class QCLabTestBase(BaseModel):
    test_type: TestType
    test_result: TestResult
    measured_value: Optional[float] = None
    measured_unit: Optional[str] = None
    iso_standard: Optional[str] = None
    test_location: Optional[str] = None
    evidence_photo_url: Optional[str] = None


class QCLabTestCreate(QCLabTestBase):
    batch_number: str
    inspector_id: int


class QCLabTestResponse(QCLabTestBase):
    id: int
    batch_number: str
    inspector_id: int
    tested_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# QC Inspection Schemas
class QCInspectionBase(BaseModel):
    type: QCInspectionType
    status: str  # Pass or Fail
    defect_reason: Optional[str] = None
    defect_location: Optional[str] = None
    defect_qty: int = 1


class QCInspectionCreate(QCInspectionBase):
    work_order_id: int
    inspected_by: int


class QCInspectionResponse(QCInspectionBase):
    id: int
    work_order_id: int
    inspected_by: int
    inspected_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# Batch Test Request
class PerformLabTestRequest(BaseModel):
    batch_number: str
    test_type: TestType
    test_result: TestResult
    measured_value: Optional[float] = None
    measured_unit: Optional[str] = None
    iso_standard: Optional[str] = None
    test_location: Optional[str] = None
    evidence_photo_url: Optional[str] = None


# Inline QC Request
class PerformInlineQCRequest(BaseModel):
    work_order_id: int
    type: QCInspectionType
    status: str  # Pass or Fail
    defect_reason: Optional[str] = None
    defect_location: Optional[str] = None
    defect_qty: int = 1


# Lab Test Summary
class LabTestSummaryResponse(BaseModel):
    batch_number: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    pass_rate: float
    critical_failures: List[dict]
    last_test_at: datetime

    class Config:
        from_attributes = True
