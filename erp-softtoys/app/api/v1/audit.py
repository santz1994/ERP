"""
Audit Trail API
Endpoints for viewing and querying audit logs

ISO 27001 A.12.4.1: Event Logging
Only accessible by authorized roles with audit permissions
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import Optional, List
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.dependencies import require_permission
from app.core.permissions import ModuleName, Permission
from app.core.models.audit import AuditLog, AuditAction, AuditModule, UserActivityLog, SecurityLog
from app.core.models.users import User
from app.core.base_production_service import BaseProductionService
from pydantic import BaseModel


router = APIRouter(prefix="/audit", tags=["Audit Trail"])


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    user_id: Optional[int]
    username: str
    user_role: Optional[str]
    ip_address: Optional[str]
    action: str
    module: str
    entity_type: Optional[str]
    entity_id: Optional[int]
    description: str
    old_values: Optional[dict]
    new_values: Optional[dict]
    request_method: Optional[str]
    request_path: Optional[str]
    
    class Config:
        from_attributes = True


class UserActivityResponse(BaseModel):
    id: int
    user_id: int
    username: str
    activity_type: str
    activity_details: Optional[str]
    timestamp: datetime
    ip_address: Optional[str]
    
    class Config:
        from_attributes = True


class SecurityLogResponse(BaseModel):
    id: int
    timestamp: datetime
    ip_address: str
    event_type: str
    severity: str
    username_attempted: Optional[str]
    description: str
    action_taken: Optional[str]
    
    class Config:
        from_attributes = True


class AuditSummaryResponse(BaseModel):
    total_events: int
    events_last_24h: int
    events_last_7d: int
    top_users: List[dict]
    top_modules: List[dict]
    recent_critical_events: List[dict]


# ============================================================================
# AUDIT LOG ENDPOINTS
# ============================================================================

@router.get("/logs", response_model=dict)
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.view_logs")),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    action: Optional[AuditAction] = None,
    module: Optional[AuditModule] = None,
    entity_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    search: Optional[str] = None
):
    """
    Get audit logs with filtering and pagination
    
    **Required Permission**: audit.view_logs
    
    **Filters**:
    - user_id: Filter by specific user
    - username: Filter by username (partial match)
    - action: Filter by action type (CREATE, UPDATE, DELETE, etc.)
    - module: Filter by system module
    - entity_type: Filter by entity type (e.g., PurchaseOrder)
    - start_date: Filter from this date
    - end_date: Filter until this date
    - search: Search in description field
    """
    query = db.query(AuditLog)
    
    # Apply filters
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    if username:
        query = query.filter(AuditLog.username.ilike(f"%{username}%"))
    
    if action:
        query = query.filter(AuditLog.action == action)
    
    if module:
        query = query.filter(AuditLog.module == module)
    
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    if search:
        query = query.filter(AuditLog.description.ilike(f"%{search}%"))
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    logs = query.order_by(desc(AuditLog.timestamp)).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [AuditLogResponse.from_orm(log) for log in logs]
    }


@router.get("/logs/{log_id}", response_model=AuditLogResponse)
def get_audit_log_detail(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.view_logs"))
):
    """
    Get detailed information about a specific audit log entry
    
    **Required Permission**: audit.view_logs
    """
    log = BaseProductionService.get_audit_log(db, log_id)
    
    return AuditLogResponse.from_orm(log)


@router.get("/entity/{entity_type}/{entity_id}", response_model=List[AuditLogResponse])
def get_entity_audit_history(
    entity_type: str,
    entity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.view_logs"))
):
    """
    Get complete audit history for a specific entity
    
    **Use Case**: Track all changes to a Purchase Order, Manufacturing Order, etc.
    
    **Required Permission**: audit.view_logs
    
    **Example**: GET /api/audit/entity/PurchaseOrder/123
    """
    logs = db.query(AuditLog).filter(
        AuditLog.entity_type == entity_type,
        AuditLog.entity_id == entity_id
    ).order_by(desc(AuditLog.timestamp)).all()
    
    return [AuditLogResponse.from_orm(log) for log in logs]


@router.get("/summary", response_model=AuditSummaryResponse)
def get_audit_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.view_summary"))
):
    """
    Get audit trail summary statistics
    
    **Required Permission**: audit.view_summary
    
    **Returns**:
    - Total events count
    - Events in last 24 hours
    - Events in last 7 days
    - Top 10 most active users
    - Top 10 most used modules
    - Recent critical security events
    """
    now = datetime.now()
    
    # Total events
    total_events = db.query(AuditLog).count()
    
    # Events last 24h
    events_24h = db.query(AuditLog).filter(
        AuditLog.timestamp >= now - timedelta(hours=24)
    ).count()
    
    # Events last 7d
    events_7d = db.query(AuditLog).filter(
        AuditLog.timestamp >= now - timedelta(days=7)
    ).count()
    
    # Top users (last 30 days)
    from sqlalchemy import func
    top_users = db.query(
        AuditLog.username,
        func.count(AuditLog.id).label('event_count')
    ).filter(
        AuditLog.timestamp >= now - timedelta(days=30)
    ).group_by(AuditLog.username).order_by(desc('event_count')).limit(10).all()
    
    # Top modules (last 30 days)
    top_modules = db.query(
        AuditLog.module,
        func.count(AuditLog.id).label('event_count')
    ).filter(
        AuditLog.timestamp >= now - timedelta(days=30)
    ).group_by(AuditLog.module).order_by(desc('event_count')).limit(10).all()
    
    # Recent critical events (last 7 days)
    critical_events = db.query(AuditLog).filter(
        AuditLog.timestamp >= now - timedelta(days=7),
        or_(
            AuditLog.action == AuditAction.DELETE,
            AuditLog.action == AuditAction.APPROVE
        )
    ).order_by(desc(AuditLog.timestamp)).limit(10).all()
    
    return AuditSummaryResponse(
        total_events=total_events,
        events_last_24h=events_24h,
        events_last_7d=events_7d,
        top_users=[{"username": u[0], "event_count": u[1]} for u in top_users],
        top_modules=[{"module": m[0], "event_count": m[1]} for m in top_modules],
        recent_critical_events=[
            {
                "id": e.id,
                "timestamp": e.timestamp.isoformat(),
                "username": e.username,
                "action": e.action.value,
                "description": e.description
            } for e in critical_events
        ]
    )


# ============================================================================
# SECURITY LOG ENDPOINTS
# ============================================================================

@router.get("/security-logs", response_model=dict)
def get_security_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.view_security_logs")),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    severity: Optional[str] = Query(None, regex="^(info|warning|critical)$"),
    event_type: Optional[str] = None,
    start_date: Optional[datetime] = None
):
    """
    Get security event logs
    
    **Required Permission**: audit.view_security_logs (ADMIN ONLY)
    
    **Tracks**: Failed logins, unauthorized access attempts, blocked IPs, etc.
    """
    query = db.query(SecurityLog)
    
    if severity:
        query = query.filter(SecurityLog.severity == severity)
    
    if event_type:
        query = query.filter(SecurityLog.event_type == event_type)
    
    if start_date:
        query = query.filter(SecurityLog.timestamp >= start_date)
    
    total = query.count()
    offset = (page - 1) * page_size
    logs = query.order_by(desc(SecurityLog.timestamp)).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [SecurityLogResponse.from_orm(log) for log in logs]
    }


@router.get("/user-activity/{user_id}", response_model=List[UserActivityResponse])
def get_user_activity(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.view_user_activity")),
    days: int = Query(7, ge=1, le=90)
):
    """
    Get user activity history
    
    **Required Permission**: audit.view_user_activity
    
    **Tracks**: Page views, API calls, session duration
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    activities = db.query(UserActivityLog).filter(
        UserActivityLog.user_id == user_id,
        UserActivityLog.timestamp >= cutoff_date
    ).order_by(desc(UserActivityLog.timestamp)).all()
    
    # Join with User to get username
    result = []
    for activity in activities:
        user = db.query(User).filter(User.id == activity.user_id).first()
        result.append({
            **UserActivityResponse.from_orm(activity).dict(),
            "username": user.username if user else "Unknown"
        })
    
    return result


# ============================================================================
# EXPORT ENDPOINTS
# ============================================================================

@router.get("/export/csv")
def export_audit_logs_csv(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permission("audit.export_logs")),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """
    Export audit logs to CSV format
    
    **Required Permission**: audit.export_logs
    
    **Use Case**: Compliance reporting, external audits
    """
    from fastapi.responses import StreamingResponse
    import csv
    import io
    
    query = db.query(AuditLog)
    
    if start_date:
        query = query.filter(AuditLog.timestamp >= start_date)
    if end_date:
        query = query.filter(AuditLog.timestamp <= end_date)
    
    logs = query.order_by(desc(AuditLog.timestamp)).all()
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'ID', 'Timestamp', 'Username', 'Role', 'IP Address', 
        'Action', 'Module', 'Entity Type', 'Entity ID', 'Description'
    ])
    
    # Data
    for log in logs:
        writer.writerow([
            log.id,
            log.timestamp.isoformat(),
            log.username,
            log.user_role,
            log.ip_address,
            log.action.value,
            log.module.value,
            log.entity_type,
            log.entity_id,
            log.description
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )
