"""Quality Control Module - API Router
Endpoints for lab testing, inline QC, metal detector checks, quality analytics.
"""

import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user, get_db
from app.core.models.quality import QCInspection, QCStatus
from app.core.models.manufacturing import ReworkRequest, ReworkStatus
from app.modules.quality.models import PerformInlineQCRequest, PerformLabTestRequest
from app.modules.quality.services import QualityService

router = APIRouter(
    prefix="/quality",
    tags=["Quality Control"],
    responses={404: {"description": "Not found"}}
)


@router.post("/lab-test/perform")
def perform_lab_test(
    request: PerformLabTestRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[QC-PHASE] Perform QC Lab Test.

    Records lab test results (Drop Test, Stability, Seam Strength) with ISO compliance.

    Request:
    - batch_number: Batch ID from manufacturing order
    - test_type: "Drop Test", "Stability 10", "Stability 27", "Seam Strength"
    - test_result: "Pass" or "Fail"
    - measured_value: Numeric test result (optional)
    - measured_unit: Unit of measurement (e.g., "cm", "Newton")
    - iso_standard: ISO standard reference (e.g., "ISO 8124")
    - test_location: Where on product (e.g., "Seam AB")
    - evidence_photo_url: Photo URL if failed

    Response:
    - test_id, test_type, result, measured_value
    - is_critical: True if failure requires P1 alert
    - tested_at: Timestamp
    """
    result = QualityService.perform_lab_test(
        db=db,
        batch_number=request.batch_number,
        test_type=request.test_type.value,
        test_result=request.test_result.value,
        measured_value=request.measured_value,
        measured_unit=request.measured_unit,
        iso_standard=request.iso_standard,
        test_location=request.test_location,
        inspector_id=current_user.get("id"),
        evidence_photo_url=request.evidence_photo_url
    )

    return {
        "status": "success",
        "data": result,
        "message": "Lab test recorded successfully"
    }


@router.get("/lab-test/batch/{batch_number}/summary")
def get_batch_test_summary(
    batch_number: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[QC-PHASE] Get Lab Test Summary for Batch.

    Returns QC lab test pass rate, failed tests, critical failures.
    Used to determine if batch can be shipped (95%+ pass rate required).

    Response:
    - total_tests, passed_tests, failed_tests
    - pass_rate: Percentage
    - can_ship: Boolean (true if >= 95% pass rate)
    - critical_failures: List of failed tests
    """
    summary = QualityService.get_batch_lab_test_summary(db, batch_number)

    return {
        "status": "success",
        "data": summary,
        "message": "Lab test summary retrieved"
    }


@router.post("/inspection/inline")
def perform_inline_qc(
    request: PerformInlineQCRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[PRODUCTION] Perform Inline QC Inspection.

    Records inline quality inspections during production.
    Types: Incoming, Inline Sewing, Final Metal Detector

    Request:
    - work_order_id: WO being inspected
    - type: "Incoming", "Inline Sewing", "Final Metal Detector"
    - status: "Pass" or "Fail"
    - defect_reason: Description of defect (if failed)
    - defect_location: Where on product
    - defect_qty: Number of defects

    Response:
    - inspection_id, status
    - escalation_required: True if failed
    """
    result = QualityService.perform_inline_qc(
        db=db,
        work_order_id=request.work_order_id,
        inspection_type=request.type.value,
        status=request.status,
        defect_reason=request.defect_reason,
        defect_location=request.defect_location,
        defect_qty=request.defect_qty,
        inspected_by=current_user.get("id")
    )

    return {
        "status": "success",
        "data": result,
        "message": "Inline QC recorded successfully"
    }


@router.post("/metal-detector/scan")
def metal_detector_check(
    work_order_id: int,
    scan_result: str,  # "PASS" or "FAIL"
    metal_detected: bool,
    metal_type: str | None = None,
    metal_location: str | None = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[CRITICAL QC] Metal Detector Scan.

    CRITICAL: Metal detection triggers P1 ALERT and blocks transfer.
    Used at Finishing department (Step 430 in production flowchart).

    Query parameters:
    - work_order_id: WO being scanned
    - scan_result: "PASS" or "FAIL"
    - metal_detected: Boolean
    - metal_type: Type of metal found (if detected)
    - metal_location: Where detected (e.g., "inside seam")

    Response (if metal detected):
    - alert_level: "P1 - CRITICAL"
    - blocked_transfer: True
    - required_actions: ["Quarantine", "Alert Manager", etc.]

    Response (if pass):
    - can_proceed_transfer: True
    """
    result = QualityService.metal_detector_scan(
        db=db,
        work_order_id=work_order_id,
        scan_result=scan_result,
        metal_detected=metal_detected,
        metal_type=metal_type,
        metal_location=metal_location,
        inspected_by=current_user.get("id")
    )

    return {
        "status": "success",
        "data": result,
        "message": "Metal detector scan completed"
    }


@router.get("/inspection/work-order/{work_order_id}/history")
def get_wo_inspection_history(
    work_order_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[QUALITY AUDIT] Get Work Order QC History.

    Returns all QC inspections performed on a work order
    (Incoming, Inline Sewing, Metal Detector, etc.)

    Response:
    - List of inspections with type, status, defects, timestamp
    """
    history = QualityService.get_wo_inspection_history(db, work_order_id)

    return {
        "status": "success",
        "data": {
            "work_order_id": work_order_id,
            "total_inspections": len(history),
            "inspections": history
        },
        "message": "QC history retrieved"
    }


@router.get("/analytics/pass-rate/{dept}")
def get_dept_pass_rate_analytics(
    dept: str,
    days: int = 7,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[ANALYTICS] Department QC Pass Rate Analysis.

    Returns QC statistics for a department over specified period.

    Query parameters:
    - dept: Department name (e.g., "Sewing", "Finishing")
    - days: Analysis period (default 7)

    Response:
    - total_inspections, passed, failed
    - pass_rate percentage
    - failure_breakdown by type
    - status: "GOOD", "WARNING", "CRITICAL"
    """
    analytics = QualityService.pass_rate_analysis(db, dept, days)

    return {
        "status": "success",
        "data": analytics,
        "message": f"Pass rate analytics for {dept} last {days} days"
    }


@router.get("/health/qc-system")
def qc_system_health_check(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[SYSTEM] QC Module Health Check.

    Verifies QC system is operational and database connected.

    Response:
    - status: "healthy" or "degraded"
    - database_connected: Boolean
    - test_data_available: Boolean
    """
    try:
        # Try to query test data
        from app.core.models.quality import QCLabTest
        test_count = db.query(QCLabTest).count()

        return {
            "status": "success",
            "data": {
                "module": "Quality Control",
                "health": "healthy",
                "database_connected": True,
                "test_records": test_count,
                "ready": True
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "data": {
                "module": "Quality Control",
                "health": "degraded",
                "database_connected": False,
                "error": str(e)
            }
        }


@router.post("/report/batch-compliance")
def generate_batch_compliance_report(
    batch_number: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """[QUALITY REPORT] Generate Batch Compliance Report.

    Generates comprehensive QC compliance report for a batch.
    Includes all lab tests, inspections, pass/fail status.
    Used for IKEA final approval before shipping.

    Response:
    - batch_number
    - compliance_status: "APPROVED" or "REJECTED"
    - test_summary, inspection_summary
    - recommendations for shipment
    """
    try:
        summary = QualityService.get_batch_lab_test_summary(db, batch_number)

        return {
            "status": "success",
            "data": {
                "batch_number": batch_number,
                "compliance_status": "APPROVED" if summary["can_ship"] else "REJECTED",
                "report_type": "QC Compliance Report",
                "test_summary": summary,
                "generated_at": str(__import__('datetime').datetime.utcnow().isoformat()),
                "recommendation": (
                    "✅ APPROVED for shipment - All QC criteria met"
                    if summary["can_ship"]
                    else "🚫 NOT APPROVED - Rework required"
                )
            },
            "message": "Batch compliance report generated"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/stats")
def get_quality_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get quality control statistics from real database.

    Returns:
    - total_inspections: Total inspections performed
    - passed: Number passed
    - failed: Number failed
    - pass_rate: Percentage passed
    - today_inspections: Count of inspections today
    """
    try:
        today = datetime.date.today()
        today_start = datetime.datetime.combine(today, datetime.time.min)

        total = db.query(func.count(QCInspection.id)).scalar() or 0
        passed = db.query(func.count(QCInspection.id)).filter(
            QCInspection.status == QCStatus.PASS
        ).scalar() or 0
        failed = db.query(func.count(QCInspection.id)).filter(
            QCInspection.status == QCStatus.FAIL
        ).scalar() or 0
        today_count = db.query(func.count(QCInspection.id)).filter(
            QCInspection.created_at >= today_start
        ).scalar() or 0

        pass_rate = round((passed / total * 100), 1) if total > 0 else 0.0

        return {
            "total_inspections": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": pass_rate,
            "today_inspections": today_count,
        }
    except Exception as e:
        return {
            "total_inspections": 0,
            "passed": 0,
            "failed": 0,
            "pass_rate": 0.0,
            "today_inspections": 0,
        }


@router.get("/rework-stats")
def get_rework_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get rework dashboard statistics from real database.

    Returns:
    - queue_count: Rework items pending or approved (not started)
    - in_progress_count: Items currently being reworked
    - completed_today: Items completed today
    - recovery_rate: % of verified items that passed (good qty / total defect qty)
    - avg_repair_time_hours: Average hours from start to completion
    - copq_this_month: Total cost of poor quality this calendar month
    """
    try:
        today = datetime.date.today()
        today_start = datetime.datetime.combine(today, datetime.time.min)
        month_start = datetime.datetime(today.year, today.month, 1)

        queue_count = db.query(func.count(ReworkRequest.id)).filter(
            ReworkRequest.status.in_([ReworkStatus.PENDING, ReworkStatus.APPROVED])
        ).scalar() or 0

        in_progress_count = db.query(func.count(ReworkRequest.id)).filter(
            ReworkRequest.status == ReworkStatus.IN_PROGRESS
        ).scalar() or 0

        completed_today = db.query(func.count(ReworkRequest.id)).filter(
            ReworkRequest.status == ReworkStatus.COMPLETED,
            ReworkRequest.rework_completed_at >= today_start
        ).scalar() or 0

        # Recovery rate: sum(verified_good_qty) / sum(defect_qty) for verified items
        verified = db.query(
            func.coalesce(func.sum(ReworkRequest.verified_good_qty), 0),
            func.coalesce(func.sum(ReworkRequest.defect_qty), 0)
        ).filter(ReworkRequest.verified_at.isnot(None)).one()
        good_qty = float(verified[0])
        total_defect = float(verified[1])
        recovery_rate = round((good_qty / total_defect * 100), 1) if total_defect > 0 else 0.0

        # Average repair time (hours) for completed items
        completed_with_times = db.query(
            ReworkRequest.rework_started_at,
            ReworkRequest.rework_completed_at
        ).filter(
            ReworkRequest.rework_started_at.isnot(None),
            ReworkRequest.rework_completed_at.isnot(None)
        ).all()
        if completed_with_times:
            total_hours = sum(
                (r.rework_completed_at - r.rework_started_at).total_seconds() / 3600
                for r in completed_with_times
            )
            avg_repair_time_hours = round(total_hours / len(completed_with_times), 1)
        else:
            avg_repair_time_hours = 0.0

        # COPQ this month
        copq = db.query(func.coalesce(func.sum(ReworkRequest.total_cost), 0)).filter(
            ReworkRequest.created_at >= month_start
        ).scalar() or 0

        return {
            "queue_count": queue_count,
            "in_progress_count": in_progress_count,
            "completed_today": completed_today,
            "recovery_rate": recovery_rate,
            "avg_repair_time_hours": avg_repair_time_hours,
            "copq_this_month": float(copq),
        }
    except Exception:
        return {
            "queue_count": 0,
            "in_progress_count": 0,
            "completed_today": 0,
            "recovery_rate": 0.0,
            "avg_repair_time_hours": 0.0,
            "copq_this_month": 0.0,
        }


@router.get("/rework")
def get_rework_list(
    status: str | None = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> list:
    """Get list of rework requests.

    Query params:
    - status: filter by status (Pending, Approved, In Progress, Completed)
    - limit: max items to return
    """
    try:
        q = db.query(ReworkRequest)
        if status:
            # Map frontend status strings to enum values
            status_map = {
                "Pending": ReworkStatus.PENDING,
                "PENDING": ReworkStatus.PENDING,
                "Approved": ReworkStatus.APPROVED,
                "APPROVED": ReworkStatus.APPROVED,
                "In Progress": ReworkStatus.IN_PROGRESS,
                "IN_PROGRESS": ReworkStatus.IN_PROGRESS,
                "Completed": ReworkStatus.COMPLETED,
                "COMPLETED": ReworkStatus.COMPLETED,
            }
            mapped = status_map.get(status)
            if mapped:
                q = q.filter(ReworkRequest.status == mapped)
        items = q.order_by(ReworkRequest.created_at.desc()).limit(limit).all()
        return [
            {
                "id": r.id,
                "work_order_id": r.spk_id,
                "defect_type": r.defect_notes or "",
                "severity": "Major",
                "status": r.status.value if r.status else "Unknown",
                "assigned_to": r.rework_operator_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.rework_completed_at.isoformat() if r.rework_completed_at else None,
            }
            for r in items
        ]
    except Exception:
        return []


@router.get("/inspections")
def get_quality_inspections(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> dict:
    """Get all quality control inspections.

    Returns list of all QC inspections with:
    - inspection_id
    - work_order_id
    - inspection_type
    - status (pass/fail)
    - defects found
    - timestamp
    - inspector name
    """
    try:
        # Get recent inspections from database - handle empty table gracefully
        inspections = []
        try:
            inspections = db.query(QCInspection).order_by(
                QCInspection.created_at.desc()
            ).limit(100).all()
        except Exception:
            # Table might not exist or have data, return empty list
            pass

        return {
            "status": "success",
            "data": [
                {
                    "id": i.id,
                    "work_order_id": i.work_order_id,
                    "inspection_type": str(i.inspection_type) if i.inspection_type else "unknown",
                    "status": str(i.status) if i.status else "unknown",
                    "defects": i.defects_found or [],
                    "timestamp": i.created_at.isoformat() if i.created_at else None,
                    "inspector": "QC Inspector"
                }
                for i in inspections
            ] if inspections else [],
            "total": len(inspections)
        }
    except Exception:
        # Return success with empty data rather than 500 error
        return {
            "status": "success",
            "data": [],
            "total": 0,
            "message": "No inspections available"
        }
