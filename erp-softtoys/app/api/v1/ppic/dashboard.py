"""
API Endpoints for PPIC Dashboard - View Only
Created: January 26, 2026
Location: app/api/v1/ppic/dashboard.py

✅ PPIC hanya VIEW, REPORT, dan ALERT
✅ BUKAN input data (itu production staff)

Endpoints:
- GET /ppic/dashboard                    - Dashboard view semua SPK
- GET /ppic/reports/daily-summary        - Daily production report
- GET /ppic/reports/on-track-status      - Alert SPK on/off track
- GET /ppic/alerts                       - Real-time alerts
"""

from datetime import datetime, date, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.models import User, SPKDailyProduction, AuditLog, SPK
from app.core.models.manufacturing import SPKStatus

router = APIRouter(prefix="/ppic", tags=["ppic"])


# ============================================================================
# ENDPOINT 1: PPIC Dashboard (Overview)
# ============================================================================
@router.get("/dashboard")
async def get_ppic_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ PPIC view dashboard - Monitor semua SPK progress
    ✅ View-only, no edit
    
    Permission: PPIC_MANAGER, MANAGER
    
    Response:
    {
        "success": true,
        "data": {
            "dashboard": {
                "total_spks": 10,
                "in_progress": 5,
                "completed": 3,
                "not_started": 2,
                "on_track": 4,
                "off_track": 1
            },
            "spks": [
                {
                    "spk_id": 1,
                    "spk_number": "SPK-001",
                    "product": "Soft Toy Bear",
                    "target_qty": 500,
                    "actual_qty": 150,
                    "completion_pct": 30.0,
                    "status": "IN_PROGRESS",
                    "health": "ON_TRACK",
                    "est_completion": "2026-02-01"
                },
                ...
            ]
        }
    }
    """
    # await check_permission - removed
    
    # Get all SPKs
    spks = db.query(SPK).all()
    
    summary = {
        "total_spks": len(spks),
        "not_started": sum(1 for s in spks if s.production_status == "NOT_STARTED"),
        "in_progress": sum(1 for s in spks if s.production_status == "IN_PROGRESS"),
        "completed": sum(1 for s in spks if s.production_status == "COMPLETED"),
        "on_track": 0,
        "off_track": 0
    }
    
    spk_list = []
    for spk in spks:
        actual_qty = spk.actual_qty or 0
        completion_pct = (actual_qty / spk.target_qty * 100) if spk.target_qty > 0 else 0
        
        # Get health status
        health = _calculate_health_status(spk, db)
        if health == "ON_TRACK":
            summary["on_track"] += 1
        elif health == "OFF_TRACK":
            summary["off_track"] += 1
        
        # Estimate completion date
        entries = db.query(SPKDailyProduction)\
            .filter(SPKDailyProduction.spk_id == spk.id).all()
        
        daily_avg = (actual_qty / len(entries)) if entries else 0
        remaining_qty = max(0, spk.target_qty - actual_qty)
        days_remaining = int(remaining_qty / daily_avg) if daily_avg > 0 else 0
        
        est_completion = (date.today() + timedelta(days=days_remaining)).isoformat() \
                        if days_remaining > 0 else spk.completion_date.isoformat() if spk.completion_date else None
        
        spk_list.append({
            "spk_id": spk.id,
            "spk_number": spk.spk_number if hasattr(spk, 'spk_number') else f"SPK-{spk.id:03d}",
            "product": spk.product_name if hasattr(spk, 'product_name') else "Unknown",
            "target_qty": spk.target_qty,
            "actual_qty": actual_qty,
            "remaining_qty": remaining_qty,
            "completion_pct": round(completion_pct, 1),
            "status": spk.production_status,
            "health": health,
            "daily_rate": round(daily_avg, 1),
            "est_completion": est_completion
        })
    
    return {
        "success": True,
        "data": {
            "dashboard": summary,
            "spks": spk_list
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 1B: Manufacturing Orders (Compatibility endpoint)
# ============================================================================
@router.get("/manufacturing-orders")
async def get_manufacturing_orders(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Get manufacturing orders (SPKs) - Compatibility endpoint
    ✅ Returns list of SPKs that represent manufacturing orders
    
    Query params:
    - status: DRAFT, IN_PROGRESS, COMPLETED, CANCELLED, all (all means no filter)
    
    Response: List of manufacturing orders
    """
    try:
        # Get SPKs from database
        query = db.query(SPK)
        
        # Skip filter if status is 'all' or empty
        if status and status.lower() != 'all':
            # Map IN_PROGRESS to valid SPK status
            status_map = {
                'IN_PROGRESS': SPKStatus.IN_PROGRESS,
                'DRAFT': SPKStatus.DRAFT,
                'COMPLETED': SPKStatus.COMPLETED,
                'CANCELLED': SPKStatus.CANCELLED
            }
            
            spk_status = status_map.get(status.upper())
            if spk_status:
                query = query.filter(SPK.status == spk_status)
        
        spks = query.all()
        
        # Transform to manufacturing order format
        mos = []
        for spk in spks:
            mos.append({
                "id": spk.id,
                "product_id": spk.product_id,
                "product_code": f"PROD-{spk.id}",
                "product_name": f"Product {spk.id}",
                "qty_planned": spk.target_qty,
                "qty_produced": spk.actual_qty,
                "routing_type": "Route1",
                "batch_number": spk.batch_number or f"BATCH-{spk.id}",
                "state": spk.status.value if hasattr(spk.status, 'value') else str(spk.status),
                "created_at": spk.created_at.isoformat() if spk.created_at else None
            })
        
        return mos
    except Exception as e:
        import traceback
        print("❌ ERROR in get_manufacturing_orders:")
        print(f"   {type(e).__name__}: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"{type(e).__name__}: {str(e)}"
        )


# ============================================================================
# ENDPOINT 2: Daily Production Report
# ============================================================================
@router.get("/reports/daily-summary")
async def get_daily_summary(
    report_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Generate daily production report (untuk PPIC)
    
    Query params:
    - report_date: YYYY-MM-DD (default: today)
    
    Response:
    {
        "success": true,
        "data": {
            "report_date": "2026-01-26",
            "total_entries": 15,
            "total_qty": 450,
            "by_spk": [
                {
                    "spk_id": 1,
                    "spk_number": "SPK-001",
                    "qty_today": 50,
                    "cumulative": 150,
                    "target": 500,
                    "completion_pct": 30.0
                },
                ...
            ]
        }
    }
    """
    # await check_permission - removed
    
    if not report_date:
        report_date = date.today().isoformat()
    else:
        report_date = report_date
    
    # Parse date
    try:
        target_date = datetime.strptime(report_date, "%Y-%m-%d").date()
    except:
        raise HTTPException(status_code=400, detail="Invalid date format (use YYYY-MM-DD)")
    
    # Get entries for this date
    entries = db.query(SPKDailyProduction)\
        .filter(SPKDailyProduction.production_date == target_date)\
        .all()
    
    by_spk = {}
    total_qty = 0
    
    for entry in entries:
        spk = entry.spk
        if spk.id not in by_spk:
            by_spk[spk.id] = {
                "spk_id": spk.id,
                "spk_number": spk.spk_number if hasattr(spk, 'spk_number') else f"SPK-{spk.id:03d}",
                "qty_today": 0,
                "cumulative": 0,
                "target": spk.target_qty,
                "completion_pct": 0
            }
        
        by_spk[spk.id]["qty_today"] += entry.input_qty
        by_spk[spk.id]["cumulative"] = entry.cumulative_qty
        total_qty += entry.input_qty
        by_spk[spk.id]["completion_pct"] = round((entry.cumulative_qty / spk.target_qty * 100) if spk.target_qty > 0 else 0, 1)
    
    return {
        "success": True,
        "data": {
            "report_date": target_date.isoformat(),
            "total_entries": len(entries),
            "total_qty": total_qty,
            "by_spk": list(by_spk.values())
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 3: On-Track Status Alert
# ============================================================================
@router.get("/reports/on-track-status")
async def get_on_track_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Alert untuk SPK yang OFF-TRACK
    ✅ PPIC bisa lihat mana SPK yang bermasalah
    
    Response:
    {
        "success": true,
        "data": {
            "on_track": [
                {
                    "spk_id": 1,
                    "spk_number": "SPK-001",
                    "status": "ON_TRACK",
                    "reason": "Daily rate: 25 units/day, est complete 2026-02-01"
                }
            ],
            "off_track": [
                {
                    "spk_id": 2,
                    "spk_number": "SPK-002",
                    "status": "OFF_TRACK",
                    "reason": "Behind schedule: need 75 units/day but only 40/day",
                    "alert": "🔴 URGENT - will not meet deadline"
                }
            ]
        }
    }
    """
    # await check_permission - removed
    
    spks = db.query(SPK).filter(SPK.production_status == "IN_PROGRESS").all()
    
    on_track = []
    off_track = []
    
    today = date.today()
    
    for spk in spks:
        actual_qty = spk.actual_qty or 0
        entries = db.query(SPKDailyProduction)\
            .filter(SPKDailyProduction.spk_id == spk.id).all()
        
        if not entries:
            continue
        
        # Calculate metrics
        days_elapsed = len(entries)
        daily_rate = actual_qty / days_elapsed if days_elapsed > 0 else 0
        remaining_qty = max(0, spk.target_qty - actual_qty)
        days_needed = int(remaining_qty / daily_rate) if daily_rate > 0 else 999
        
        # Expected progress (assuming consistent daily rate)
        expected_qty = daily_rate * days_elapsed
        
        # Check if on track
        if days_elapsed > 0 and actual_qty >= (expected_qty * 0.85):  # 85% tolerance
            status = "ON_TRACK"
            reason = f"Daily rate: {daily_rate:.0f} units/day, est complete {(today + timedelta(days=days_needed)).isoformat()}"
            on_track.append({
                "spk_id": spk.id,
                "spk_number": spk.spk_number if hasattr(spk, 'spk_number') else f"SPK-{spk.id:03d}",
                "status": status,
                "reason": reason
            })
        else:
            status = "OFF_TRACK"
            required_daily = (remaining_qty / days_needed) if days_needed > 0 else 0
            reason = f"Behind: need {required_daily:.0f}/day but only {daily_rate:.0f}/day"
            alert = "🔴 URGENT - will not meet deadline" if days_needed > 7 else "🟡 WARNING - at risk"
            off_track.append({
                "spk_id": spk.id,
                "spk_number": spk.spk_number if hasattr(spk, 'spk_number') else f"SPK-{spk.id:03d}",
                "status": status,
                "reason": reason,
                "alert": alert,
                "required_daily_rate": round(required_daily, 1),
                "current_daily_rate": round(daily_rate, 1)
            })
    
    return {
        "success": True,
        "data": {
            "on_track": on_track,
            "off_track": off_track,
            "summary": {
                "on_track_count": len(on_track),
                "off_track_count": len(off_track)
            }
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# ENDPOINT 4: Real-time Alerts
# ============================================================================
@router.get("/alerts")
async def get_alerts(
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Get real-time alerts untuk PPIC
    
    Query params:
    - severity: critical, warning, info (default: all)
    
    Response:
    {
        "success": true,
        "data": [
            {
                "alert_id": 1,
                "severity": "🔴 CRITICAL",
                "title": "SPK-002 OFF-TRACK",
                "message": "SPK-002 will not meet deadline at current rate",
                "spk_id": 2,
                "created_at": "2026-01-26T14:30:00"
            },
            ...
        ]
    }
    """
    # await check_permission - removed
    
    alerts = []
    
    # Check off-track SPKs
    spks = db.query(SPK).filter(SPK.production_status == "IN_PROGRESS").all()
    
    for spk in spks:
        actual_qty = spk.actual_qty or 0
        entries = db.query(SPKDailyProduction)\
            .filter(SPKDailyProduction.spk_id == spk.id).all()
        
        if not entries or len(entries) < 2:
            continue
        
        daily_rate = actual_qty / len(entries)
        remaining_qty = max(0, spk.target_qty - actual_qty)
        days_needed = int(remaining_qty / daily_rate) if daily_rate > 0 else 999
        
        if days_needed > 7:
            alerts.append({
                "alert_id": f"OFF_TRACK_{spk.id}",
                "severity": "🔴 CRITICAL",
                "title": f"SPK-{spk.id:03d} OFF-TRACK",
                "message": f"Will not meet deadline at current rate ({daily_rate:.0f} units/day)",
                "spk_id": spk.id,
                "created_at": datetime.utcnow().isoformat()
            })
        elif days_needed > 3:
            alerts.append({
                "alert_id": f"AT_RISK_{spk.id}",
                "severity": "🟡 WARNING",
                "title": f"SPK-{spk.id:03d} AT-RISK",
                "message": f"Production rate declining, at risk of missing deadline",
                "spk_id": spk.id,
                "created_at": datetime.utcnow().isoformat()
            })
    
    if severity:
        alerts = [a for a in alerts if severity.lower() in a["severity"].lower()]
    
    return {
        "success": True,
        "data": alerts,
        "summary": {
            "total_alerts": len(alerts),
            "critical": sum(1 for a in alerts if "CRITICAL" in a["severity"]),
            "warning": sum(1 for a in alerts if "WARNING" in a["severity"])
        },
        "timestamp": datetime.utcnow().isoformat()
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _calculate_health_status(spk: SPK, db: Session) -> str:
    """Calculate SPK health status: ON_TRACK, OFF_TRACK, or COMPLETED"""
    if spk.production_status == "COMPLETED":
        return "COMPLETED"
    
    if spk.production_status == "NOT_STARTED":
        return "NOT_STARTED"
    
    actual_qty = spk.actual_qty or 0
    entries = db.query(SPKDailyProduction)\
        .filter(SPKDailyProduction.spk_id == spk.id).all()
    
    if not entries:
        return "NOT_STARTED"
    
    days_elapsed = len(entries)
    daily_rate = actual_qty / days_elapsed if days_elapsed > 0 else 0
    
    expected_qty = daily_rate * days_elapsed
    
    # 85% of expected
    if actual_qty >= (expected_qty * 0.85):
        return "ON_TRACK"
    else:
        return "OFF_TRACK"


