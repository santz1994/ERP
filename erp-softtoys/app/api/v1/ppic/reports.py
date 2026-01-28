"""
PPIC Reports API endpoints
Feature #6: Daily Production Reports & Alert System

Endpoints:
- GET /ppic/daily-report - Get daily production report
- GET /ppic/alerts - Get system alerts
- POST /ppic/alerts/{id}/read - Mark alert as read
- GET /ppic/late-spks - Get list of late SPKs
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.core.models.users import User
from app.services.ppic_report_service import PPICReportService, AlertType, AlertSeverity

router = APIRouter(prefix="/ppic", tags=["ppic"])


# ==================== Pydantic Schemas ====================

class MaterialStatusItem(BaseModel):
    """Material status item"""
    material_id: int
    name: str
    current: int
    min: Optional[int] = None
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    """Alert response"""
    id: Optional[int] = None
    alert_type: str
    severity: str
    title: str
    description: str
    entity_type: str
    entity_id: int
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True


class DailyReportResponse(BaseModel):
    """Daily production report response"""
    report_date: date
    total_spks: int
    completed_spks: int
    in_progress_spks: int
    late_spks: int
    on_time_rate: float = Field(..., ge=0, le=100)
    avg_cycle_time: float
    quality_reject_rate: float = Field(..., ge=0, le=100)
    material_status: dict
    critical_alerts: List[AlertResponse]
    
    class Config:
        from_attributes = True


class LateSpkResponse(BaseModel):
    """Late SPK item"""
    spk_id: int
    deadline: str
    days_late: Optional[int] = None
    progress: Optional[float] = None
    expected: Optional[float] = None
    reason: str
    status: str
    severity: str
    
    class Config:
        from_attributes = True


# ==================== Endpoints ====================

@router.get("/daily-report", response_model=DailyReportResponse)
async def get_daily_report(
    report_date: Optional[date] = Query(None, description="Report date (default: today)"),
    department_id: Optional[int] = Query(None, description="Filter by department"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get daily production report
    
    Permissions: PPIC Manager, PPIC Operator, Plant Manager
    
    Query Parameters:
    - report_date: Optional date (YYYY-MM-DD format)
    - department_id: Optional department filter
    
    Returns:
    - Daily metrics with completion rate, late SPKs, material status, alerts
    """
    try:
        # Check permission
        allowed_roles = ["PPIC_MANAGER", "PPIC_OPERATOR", "PLANT_MANAGER"]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Only PPIC roles can view reports. Your role: {current_user.role}"
            )
        
        service = PPICReportService(db)
        metrics = await service.generate_daily_report(
            report_date=report_date,
            department_id=department_id
        )
        
        return metrics
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )


@router.get("/late-spks", response_model=List[LateSpkResponse])
async def get_late_spks(
    severity: Optional[str] = Query(None, description="Filter by severity (WARNING, CRITICAL)"),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get list of late or at-risk SPKs
    
    Permissions: PPIC Manager, Production Manager
    
    Query Parameters:
    - severity: Optional filter (WARNING or CRITICAL)
    - limit: Max results (default 50)
    
    Returns:
    - List of late SPKs with reason and severity
    """
    try:
        allowed_roles = ["PPIC_MANAGER", "PRODUCTION_MANAGER", "PLANT_MANAGER"]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to view late SPKs"
            )
        
        service = PPICReportService(db)
        metrics = await service.generate_daily_report()
        
        late_spks = metrics.critical_alerts[:limit]
        
        if severity:
            late_spks = [s for s in late_spks if s.get("severity") == severity]
        
        return late_spks
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get late SPKs: {str(e)}"
        )


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts(
    alert_type: Optional[str] = Query(None, description="Filter by alert type"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get system alerts
    
    Permissions: All authenticated users
    
    Query Parameters:
    - alert_type: Optional filter (SPK_LATE, MATERIAL_LOW_STOCK, etc.)
    - severity: Optional filter (INFO, WARNING, CRITICAL)
    - is_read: Optional filter for read status
    - limit: Max results (default 100)
    - offset: Pagination offset
    
    Returns:
    - List of alerts matching filters
    """
    try:
        # In production, would query alerts from database
        # For now return empty list
        
        return []
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alerts: {str(e)}"
        )


@router.post("/alerts/{alert_id}/read")
async def mark_alert_as_read(
    alert_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark alert as read
    
    Path Parameters:
    - alert_id: Alert ID
    
    Returns:
    - Updated alert
    """
    try:
        # In production, would update alert record
        return {
            "alert_id": alert_id,
            "is_read": True,
            "read_at": datetime.utcnow(),
            "read_by": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark alert as read: {str(e)}"
        )


@router.get("/material-status")
async def get_material_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current material inventory status
    
    Permissions: PPIC, Warehouse, MANAGER roles
    
    Returns:
    - Material status with critical/low/ok stock items
    """
    try:
        allowed_roles = ["PPIC_MANAGER", "PPIC_OPERATOR", "WAREHOUSE", "MANAGER"]
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to view material status"
            )
        
        service = PPICReportService(db)
        status = service._get_material_status()
        
        return {
            "total_materials": status.get("total_materials", 0),
            "critical_stock_count": len(status.get("critical_stock", [])),
            "low_stock_count": len(status.get("low_stock", [])),
            "ok_stock_count": len(status.get("ok_stock", [])),
            "critical_stock": status.get("critical_stock", [])[:10],  # Top 10
            "low_stock": status.get("low_stock", [])[:10]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get material status: {str(e)}"
        )


@router.post("/send-test-report")
async def send_test_report(
    recipient_email: str = Query(..., description="Recipient email"),
    department_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Send test daily report email (for testing/verification)
    
    Permissions: PPIC Manager, Plant Manager only
    
    Query Parameters:
    - recipient_email: Email to send test report to
    - department_id: Optional department filter
    
    Returns:
    - Confirmation message
    """
    try:
        # Only PPIC Manager can send test reports
        if current_user.role not in ["PPIC_MANAGER", "PLANT_MANAGER"]:
            raise HTTPException(
                status_code=403,
                detail="Only PPIC Manager can send test reports"
            )
        
        service = PPICReportService(db)
        metrics = await service.generate_daily_report(department_id=department_id)
        
        success = await service.send_daily_report_email(
            metrics=metrics,
            recipient_emails=[recipient_email]
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
        
        return {
            "status": "success",
            "message": f"Test report sent to {recipient_email}",
            "report_date": metrics.report_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to send test report: {str(e)}"
        )
