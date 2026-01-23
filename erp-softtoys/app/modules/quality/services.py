"""Quality Control Module - Business Logic & Services
Handles lab testing, inline inspections, metal detector QC
"""

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.core.base_production_service import BaseProductionService
from app.core.models.manufacturing import ManufacturingOrder
from app.core.models.quality import (
    QCInspection,
    QCInspectionType,
    QCLabTest,
    QCStatus,
    TestResult,
    TestType,
)


class QualityService(BaseProductionService):
    """Business logic for quality control operations"""

    @staticmethod
    def perform_lab_test(
        db: Session,
        batch_number: str,
        test_type: str,
        test_result: str,
        measured_value: float | None = None,
        measured_unit: str | None = None,
        iso_standard: str | None = None,
        test_location: str | None = None,
        inspector_id: int | None = None,
        evidence_photo_url: str | None = None
    ) -> dict:
        """Perform QC Lab Test (Drop Test, Stability, Seam Strength, etc.)
        Records test results with measured values for ISO compliance
        """
        # Validate batch exists
        mo = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.batch_number == batch_number
        ).first()

        if not mo:
            raise HTTPException(
                status_code=404,
                detail=f"Batch {batch_number} not found"
            )

        # Map string to enum
        try:
            test_type_enum = TestType[test_type.upper().replace(" ", "_")]
            result_enum = TestResult[test_result.upper()]
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid test type or result: {str(e)}")

        # Create lab test record
        lab_test = QCLabTest(
            batch_number=batch_number,
            test_type=test_type_enum,
            test_result=result_enum,
            measured_value=measured_value,
            measured_unit=measured_unit,
            iso_standard=iso_standard,
            test_location=test_location,
            inspector_id=inspector_id or 1,  # Default to admin if not specified
            evidence_photo_url=evidence_photo_url if result_enum == TestResult.FAIL else None,
            tested_at=datetime.utcnow()
        )

        db.add(lab_test)
        db.commit()
        db.refresh(lab_test)

        # Determine if this is a critical failure (P1 alert)
        is_critical = False
        if result_enum == TestResult.FAIL:
            # Metal Detector failures are always critical
            if test_type_enum == TestType.METAL_DETECTOR or test_type_enum == TestType.DROP_TEST:
                is_critical = True

        return {
            "test_id": lab_test.id,
            "batch_number": batch_number,
            "test_type": test_type,
            "result": test_result,
            "measured_value": measured_value,
            "measured_unit": measured_unit,
            "iso_standard": iso_standard,
            "location": test_location,
            "is_critical": is_critical,
            "tested_at": lab_test.tested_at.isoformat(),
            "evidence_photo": evidence_photo_url if result_enum == TestResult.FAIL else None
        }

    @staticmethod
    def perform_inline_qc(
        db: Session,
        work_order_id: int,
        inspection_type: str,
        status: str,
        defect_reason: str | None = None,
        defect_location: str | None = None,
        defect_qty: int = 1,
        inspected_by: int | None = None
    ) -> dict:
        """Perform Inline QC Inspection (Sewing, Metal Detector, etc.)
        Records pass/fail status with defect tracking
        """
        wo = BaseProductionService.get_work_order(db, work_order_id)

        # Map string to enum
        try:
            inspection_type_enum = QCInspectionType[inspection_type.upper().replace(" ", "_")]
            status_enum = QCStatus[status.upper()]
        except KeyError as e:
            raise HTTPException(status_code=400, detail=f"Invalid inspection type or status: {str(e)}")

        # Create inspection record
        inspection = QCInspection(
            work_order_id=work_order_id,
            type=inspection_type_enum,
            status=status_enum,
            defect_reason=defect_reason,
            defect_location=defect_location,
            defect_qty=defect_qty,
            inspected_by=inspected_by or 1,
            inspected_at=datetime.utcnow()
        )

        db.add(inspection)
        db.commit()
        db.refresh(inspection)

        # Handle failure scenarios
        escalation_required = False
        if status_enum == QCStatus.FAIL:
            escalation_required = True
            # Critical failure if metal detector or seam failure
            if inspection_type_enum == QCInspectionType.FINAL_METAL_DETECTOR:
                escalation_required = True

        return {
            "inspection_id": inspection.id,
            "work_order_id": work_order_id,
            "type": inspection_type,
            "status": status,
            "defect_reason": defect_reason,
            "defect_location": defect_location,
            "defect_qty": defect_qty,
            "escalation_required": escalation_required,
            "inspected_at": inspection.inspected_at.isoformat()
        }

    @staticmethod
    def metal_detector_scan(
        db: Session,
        work_order_id: int,
        scan_result: str,
        metal_detected: bool,
        metal_type: str | None = None,
        metal_location: str | None = None,
        inspected_by: int | None = None
    ) -> dict:
        """Metal Detector QC Check
        CRITICAL: Metal detection = P1 Alert + Block Transfer
        """
        wo = BaseProductionService.get_work_order(db, work_order_id)

        mo = BaseProductionService.get_manufacturing_order(db, wo.mo_id)

        # Record inspection
        inspection = QCInspection(
            work_order_id=work_order_id,
            type=QCInspectionType.FINAL_METAL_DETECTOR,
            status=QCStatus.FAIL if metal_detected else QCStatus.PASS,
            defect_reason=f"Metal detected: {metal_type}" if metal_detected else None,
            defect_location=metal_location,
            defect_qty=1 if metal_detected else 0,
            inspected_by=inspected_by or 1,
            inspected_at=datetime.utcnow()
        )

        db.add(inspection)
        db.commit()
        db.refresh(inspection)

        # If metal detected - P1 ALERT
        result = {
            "inspection_id": inspection.id,
            "work_order_id": work_order_id,
            "scan_result": scan_result,
            "metal_detected": metal_detected,
            "metal_type": metal_type,
            "metal_location": metal_location,
            "inspection_status": "PASS" if not metal_detected else "FAIL (P1 ALERT)"
        }

        if metal_detected:
            result["alert_level"] = "P1 - CRITICAL"
            result["required_actions"] = [
                "🚨 BLOCK all transfers from this work order",
                "Quarantine affected items",
                "Alert Manager & Quality Lead",
                "Initiate root cause analysis",
                "Segregate batch for rework or scrap decision"
            ]
            result["blocked_transfer"] = True
        else:
            result["alert_level"] = "NONE"
            result["can_proceed_transfer"] = True

        return result

    @staticmethod
    def get_batch_lab_test_summary(
        db: Session,
        batch_number: str
    ) -> dict:
        """Get QC Lab Test summary for a batch
        Pass rate, failed tests, critical failures
        """
        tests = db.query(QCLabTest).filter(
            QCLabTest.batch_number == batch_number
        ).all()

        if not tests:
            raise HTTPException(
                status_code=404,
                detail=f"No lab tests found for batch {batch_number}"
            )

        passed = sum(1 for t in tests if t.test_result == TestResult.PASS)
        failed = sum(1 for t in tests if t.test_result == TestResult.FAIL)
        total = len(tests)
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Identify critical failures
        critical_failures = [
            {
                "test_id": t.id,
                "test_type": t.test_type.value,
                "measured_value": t.measured_value,
                "iso_standard": t.iso_standard,
                "tested_at": t.tested_at.isoformat()
            }
            for t in tests if t.test_result == TestResult.FAIL and
            t.test_type in [TestType.DROP_TEST, TestType.STABILITY_10, TestType.STABILITY_27]
        ]

        return {
            "batch_number": batch_number,
            "total_tests": total,
            "passed_tests": passed,
            "failed_tests": failed,
            "pass_rate": round(pass_rate, 2),
            "can_ship": pass_rate >= 95.0,  # 95% pass threshold for shipping
            "critical_failures": critical_failures,
            "last_test_at": max(t.tested_at for t in tests).isoformat()
        }

    @staticmethod
    def get_wo_inspection_history(
        db: Session,
        work_order_id: int
    ) -> list[dict]:
        """Get all QC inspections for a work order
        """
        inspections = db.query(QCInspection).filter(
            QCInspection.work_order_id == work_order_id
        ).order_by(desc(QCInspection.inspected_at)).all()

        return [
            {
                "inspection_id": i.id,
                "type": i.type.value,
                "status": i.status.value,
                "defect_reason": i.defect_reason,
                "defect_location": i.defect_location,
                "defect_qty": i.defect_qty,
                "inspected_at": i.inspected_at.isoformat()
            }
            for i in inspections
        ]

    @staticmethod
    def pass_rate_analysis(
        db: Session,
        dept: str,
        days: int = 7
    ) -> dict:
        """QC Pass Rate analysis by department
        """
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get inspections for the period
        inspections = db.query(QCInspection).filter(
            QCInspection.inspected_at >= cutoff
        ).all()

        if not inspections:
            return {
                "dept": dept,
                "period_days": days,
                "total_inspections": 0,
                "pass_rate": 0,
                "message": "No inspections found for this period"
            }

        passed = sum(1 for i in inspections if i.status == QCStatus.PASS)
        total = len(inspections)
        pass_rate = (passed / total * 100) if total > 0 else 0

        # Group failures by type
        failure_breakdown = {}
        for i in inspections:
            if i.status == QCStatus.FAIL:
                reason = i.defect_reason or "Unknown"
                failure_breakdown[reason] = failure_breakdown.get(reason, 0) + 1

        return {
            "dept": dept,
            "period_days": days,
            "total_inspections": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(pass_rate, 2),
            "failure_breakdown": failure_breakdown,
            "status": "GOOD" if pass_rate >= 95 else "WARNING" if pass_rate >= 85 else "CRITICAL"
        }
