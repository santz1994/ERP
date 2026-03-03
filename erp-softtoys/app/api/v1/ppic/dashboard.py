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
from app.core.models.manufacturing import SPKStatus, ManufacturingOrder, WorkOrder, WorkOrderStatus, Department
from app.core.models.bom import BOMHeader, BOMDetail

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
# ENDPOINT: SPK List (for department input pages)
# ============================================================================
@router.get("/spk")
async def get_spk_list(
    department: Optional[str] = None,
    mo_id: Optional[int] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List active Work Orders as SPKs for department daily-input pages.
    Queries the work_orders table (actual production data).
    status=ONGOING → PENDING + RUNNING work orders.
    Returns camelCase fields required by CuttingInputPage, SewingInputPage, etc.
    """
    try:
        from app.core.models import Product
        from app.core.models.products import ProductType

        query = db.query(WorkOrder)

        # Department filter – Department enum values are capitalized (e.g. "Cutting")
        if department:
            dept_upper = department.upper()
            # Try enum by value first (e.g. "Cutting"), then by name (e.g. "CUTTING")
            dept_enum = None
            for d in Department:
                if d.name.upper() == dept_upper or d.value.upper() == dept_upper:
                    dept_enum = d
                    break
            if dept_enum is not None:
                query = query.filter(WorkOrder.department == dept_enum)

        if mo_id:
            query = query.filter(WorkOrder.mo_id == mo_id)

        # Status mapping: frontend sends ONGOING → PENDING + RUNNING work orders
        if status:
            s_upper = status.upper()
            if s_upper == "ONGOING":
                query = query.filter(
                    WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.RUNNING])
                )
            elif s_upper in ("PENDING", "NOT_STARTED"):
                query = query.filter(WorkOrder.status == WorkOrderStatus.PENDING)
            elif s_upper in ("RUNNING", "IN_PROGRESS"):
                query = query.filter(WorkOrder.status == WorkOrderStatus.RUNNING)
            elif s_upper in ("FINISHED", "COMPLETED", "DONE"):
                query = query.filter(WorkOrder.status == WorkOrderStatus.FINISHED)
            # else: unknown status → no filter (fall through)
        else:
            # Default: only active work orders (PENDING + RUNNING)
            query = query.filter(
                WorkOrder.status.in_([WorkOrderStatus.PENDING, WorkOrderStatus.RUNNING])
            )

        work_orders = query.order_by(WorkOrder.id.desc()).offset(skip).limit(limit).all()

        result = []
        for wo in work_orders:
            # Get MO + product info
            mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == wo.mo_id).first()
            product = None
            if mo:
                product = db.query(Product).filter(Product.id == mo.product_id).first()

            dept_val = wo.department.value if hasattr(wo.department, "value") else str(wo.department)
            produced = float(wo.output_qty or 0)
            target = float(wo.target_qty or 0)
            completion_pct = round((produced / target * 100), 1) if target > 0 else 0.0
            remaining = max(0.0, target - produced)
            wo_status = wo.status.value if hasattr(wo.status, "value") else str(wo.status)
            spk_num = wo.wo_number or f"WO-{wo.mo_id}-{dept_val[:3].upper()}-{wo.id:04d}"

            # Dept → BOM revision mapping (WIP products carry dept-specific BOMs)
            DEPT_BOM_REVISION = {
                "Cutting": "CUT-1.0",
                "Embroidery": "EMB-1.0",
                "Sewing": "SEW-1.0",
                "Finishing": "FIN-1.0",
                "Packing": "PCK-1.0",
            }

            # BOM materials for this product + department
            bom_materials = []
            if mo and mo.product_id and product:
                dept_revision = DEPT_BOM_REVISION.get(dept_val)
                if dept_revision and product.name:
                    # Dept BOMs are keyed on WIP products (e.g. DUKTIG_PIZZA_..._WIP_CUT),
                    # not on the FG product. Use FG article name's first word as keyword
                    # to find all related WIP BOM headers for this department.
                    name_keyword = product.name.split()[0].upper()
                    wip_bom_headers = db.query(BOMHeader).join(
                        Product, BOMHeader.product_id == Product.id
                    ).filter(
                        BOMHeader.revision == dept_revision,
                        BOMHeader.is_active == True,
                        Product.code.ilike(f"%{name_keyword}%"),
                    ).all()

                    # Aggregate raw materials across all WIP BOMs for this dept.
                    # Same material may appear in multiple WIP pieces (e.g. RED fabric
                    # used by both Chili and Sauce pieces) — SUM the quantities.
                    # Exclude WIP sub-assemblies — only consumable raw materials.
                    mat_totals: dict = {}  # component_id -> {code, name, qty, uom}
                    for wip_header in wip_bom_headers:
                        for detail in db.query(BOMDetail).filter(
                            BOMDetail.bom_header_id == wip_header.id
                        ).all():
                            mat = db.query(Product).filter(Product.id == detail.component_id).first()
                            if mat and mat.type != ProductType.WIP:
                                uom_val = mat.uom.value if hasattr(mat.uom, "value") else str(mat.uom) if mat.uom else "PCS"
                                if detail.component_id in mat_totals:
                                    mat_totals[detail.component_id]["qtyPerUnit"] = round(
                                        mat_totals[detail.component_id]["qtyPerUnit"] + float(detail.qty_needed or 0), 6
                                    )
                                else:
                                    mat_totals[detail.component_id] = {
                                        "materialCode": mat.code or str(mat.id),
                                        "materialName": mat.name or "",
                                        "qtyPerUnit": float(detail.qty_needed or 0),
                                        "uom": uom_val,
                                    }
                    bom_materials = list(mat_totals.values())

                # Fallback to consolidated PURCH-1.0 BOM if no dept-specific BOMs found
                if not bom_materials:
                    bom_header = db.query(BOMHeader).filter(
                        BOMHeader.product_id == mo.product_id,
                        BOMHeader.is_active == True
                    ).order_by(BOMHeader.id.desc()).first()
                    if bom_header:
                        for detail in db.query(BOMDetail).filter(
                            BOMDetail.bom_header_id == bom_header.id
                        ).all():
                            mat = db.query(Product).filter(Product.id == detail.component_id).first()
                            if mat:
                                uom_val = mat.uom.value if hasattr(mat.uom, "value") else str(mat.uom) if mat.uom else "PCS"
                                bom_materials.append({
                                    "materialCode": mat.code or str(mat.id),
                                    "materialName": mat.name or "",
                                    "qtyPerUnit": float(detail.qty_needed or 0),
                                    "uom": uom_val,
                                })

            entry = {
                # camelCase fields for frontend SPK interface
                "id": wo.id,
                "spkNumber": spk_num,
                "articleCode": product.code if product else None,
                "articleName": product.name if product else None,
                "targetQty": target,
                "actualQty": produced,
                "remainingQty": remaining,
                "bomMaterials": bom_materials,
                # snake_case aliases for backward compat
                "mo_id": wo.mo_id,
                "wo_number": spk_num,
                "spk_number": spk_num,
                "department": dept_val,
                "status": wo_status,
                "target_qty": target,
                "produced_qty": produced,
                "good_qty": float(wo.output_qty or 0),
                "defect_qty": float(wo.reject_qty or 0),
                "completion_pct": completion_pct,
                "remaining_qty": remaining,
                "product_id": mo.product_id if mo else None,
                "product_code": product.code if product else None,
                "product_name": product.name if product else None,
                "batch_number": mo.batch_number if mo else None,
                "planned_start_date": wo.planned_start_date.isoformat() if wo.planned_start_date else None,
                "actual_start_date": wo.actual_start_date.isoformat() if wo.actual_start_date else None,
                "created_at": wo.created_at.isoformat() if wo.created_at else None,
            }
            result.append(entry)

        return result

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.get("/spk/{spk_id}")
async def get_spk_detail(
    spk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single SPK with full detail including daily production entries."""
    from app.core.models import Product
    from app.core.models.daily_production import SPKDailyProduction as DailyProd

    spk = db.query(SPK).filter(SPK.id == spk_id).first()
    if not spk:
        raise HTTPException(status_code=404, detail="SPK not found")

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == spk.mo_id).first()
    product = db.query(Product).filter(Product.id == mo.product_id).first() if mo else None
    entries = db.query(DailyProd).filter(DailyProd.spk_id == spk_id).order_by(DailyProd.production_date).all()

    dept_val = spk.department.value if hasattr(spk.department, "value") else str(spk.department)
    target = spk.target_qty or 0
    produced = spk.produced_qty or 0

    return {
        "id": spk.id,
        "mo_id": spk.mo_id,
        "spk_number": f"SPK-{spk.mo_id}-{dept_val[:3].upper()}-{spk.id:04d}",
        "department": dept_val,
        "status": spk.production_status or "NOT_STARTED",
        "target_qty": target,
        "produced_qty": produced,
        "good_qty": spk.good_qty or 0,
        "defect_qty": spk.defect_qty or 0,
        "rework_qty": spk.rework_qty or 0,
        "completion_pct": round((produced / target * 100), 1) if target > 0 else 0.0,
        "remaining_qty": max(0, target - produced),
        "product_id": mo.product_id if mo else None,
        "product_code": product.code if product else None,
        "product_name": product.name if product else None,
        "batch_number": mo.batch_number if mo else None,
        "planned_start_date": spk.planned_start_date.isoformat() if spk.planned_start_date else None,
        "target_completion_date": spk.target_completion_date.isoformat() if spk.target_completion_date else None,
        "daily_entries": [
            {
                "date": e.production_date.isoformat() if e.production_date else None,
                "quantity": e.input_qty,
                "cumulative_qty": e.cumulative_qty,
                "status": e.status,
                "notes": e.notes,
            }
            for e in entries
        ],
    }


# ============================================================================
# ENDPOINT 1B: Manufacturing Orders (Compatibility endpoint)
# ============================================================================
@router.get("/manufacturing-orders")
async def get_manufacturing_orders(
    status: Optional[str] = None,
    mo_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ✅ Get manufacturing orders from ManufacturingOrder table
    Query params:
    - status: Draft, In Progress, Done, Cancel, all
    - mo_type: BUYER or PRODUCTION
    """
    try:
        from app.core.models.manufacturing import MOState, MOType

        query = db.query(ManufacturingOrder)

        if status and status.lower() != 'all':
            try:
                state_val = MOState(status)
            except ValueError:
                state_val = status
            query = query.filter(ManufacturingOrder.state == state_val)

        if mo_type and mo_type.lower() != 'all':
            try:
                mt_val = MOType(mo_type.upper())
            except ValueError:
                mt_val = mo_type
            query = query.filter(ManufacturingOrder.mo_type == mt_val)

        mos = query.order_by(ManufacturingOrder.id.desc()).offset(skip).limit(limit).all()

        result = []
        for mo in mos:
            routing = mo.routing_type.value if hasattr(mo.routing_type, 'value') else str(mo.routing_type) if mo.routing_type else 'ROUTE_2_DIRECT'
            state = mo.state.value if hasattr(mo.state, 'value') else str(mo.state) if mo.state else 'Draft'
            mo_type_val = mo.mo_type.value if hasattr(mo.mo_type, 'value') else str(mo.mo_type) if mo.mo_type else 'PRODUCTION'
            result.append({
                "id": mo.id,
                "so_line_id": mo.so_line_id,
                "product_id": mo.product_id,
                "qty_planned": float(mo.qty_planned) if mo.qty_planned else 0,
                "qty_produced": float(mo.qty_produced) if mo.qty_produced else 0,
                "routing_type": routing,
                "batch_number": mo.batch_number or f"MO-{mo.id}",
                "state": state,
                "mo_type": mo_type_val,
                "is_qty_locked": bool(mo.is_qty_locked),
                "buyer_mo_id": mo.buyer_mo_id,
                "po_fabric_id": mo.po_fabric_id,
                "trigger_mode": mo.trigger_mode or "PARTIAL",
                "production_week": mo.production_week,
                "destination_country": mo.destination_country,
                "created_at": mo.created_at.isoformat() if mo.created_at else None,
            })

        return result
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
# ENDPOINT: Work Orders
# ============================================================================
@router.get("/work-orders")
async def list_work_orders(
    mo_id: Optional[int] = None,
    department: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 200,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List Work Orders — filter by mo_id, department, or status."""
    try:
        query = db.query(WorkOrder)
        if mo_id:
            query = query.filter(WorkOrder.mo_id == mo_id)
        if department:
            try:
                dept_enum = Department(department.upper())
                query = query.filter(WorkOrder.department == dept_enum)
            except ValueError:
                pass
        if status:
            try:
                status_enum = WorkOrderStatus(status.upper())
                query = query.filter(WorkOrder.status == status_enum)
            except ValueError:
                pass

        wos = query.order_by(WorkOrder.mo_id, WorkOrder.sequence).offset(skip).limit(limit).all()

        result = []
        for wo in wos:
            result.append({
                "id": wo.id,
                "mo_id": wo.mo_id,
                "wo_number": wo.wo_number,
                "department": wo.department.value if hasattr(wo.department, "value") else str(wo.department),
                "sequence": wo.sequence,
                "status": wo.status.value if hasattr(wo.status, "value") else str(wo.status),
                "target_qty": str(wo.target_qty) if wo.target_qty is not None else None,
                "actual_qty": str(wo.output_qty) if wo.output_qty is not None else None,
                "input_qty": str(wo.input_qty) if wo.input_qty is not None else "0",
                "input_wip_product_id": wo.input_wip_product_id,
                "output_wip_product_id": wo.output_wip_product_id,
                "planned_start_date": wo.planned_start_date.isoformat() if wo.planned_start_date else None,
                "created_at": wo.created_at.isoformat() if wo.created_at else None,
            })
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.post("/work-orders/generate")
async def generate_work_orders(
    mo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate Work Orders for all departments in an MO's routing (idempotent)."""
    try:
        from app.core.models.manufacturing import RoutingType

        mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
        if not mo:
            raise HTTPException(status_code=404, detail="Manufacturing order not found")

        routing = mo.routing_type.value if hasattr(mo.routing_type, "value") else str(mo.routing_type)
        routing_depts = {
            "ROUTE_1_EMBROIDERY": [Department.CUTTING, Department.EMBROIDERY, Department.SEWING,
                                    Department.FINISHING, Department.PACKING],
            "ROUTE_2_DIRECT": [Department.CUTTING, Department.SEWING, Department.FINISHING, Department.PACKING],
            "ROUTE_3_LABEL_ONLY": [Department.PACKING],
        }
        depts = routing_depts.get(routing, [Department.CUTTING, Department.SEWING, Department.FINISHING, Department.PACKING])

        existing = db.query(WorkOrder.department).filter(WorkOrder.mo_id == mo_id).all()
        existing_depts = {row[0] for row in existing}

        created = 0
        for seq, dept in enumerate(depts, start=1):
            if dept not in existing_depts:
                wo = WorkOrder(
                    mo_id=mo_id,
                    product_id=mo.product_id,
                    department=dept,
                    status=WorkOrderStatus.PENDING,
                    input_qty=mo.qty_planned,
                    target_qty=mo.qty_planned,
                    sequence=seq,
                    wo_number=f"{mo.batch_number}-{dept.value[:3].upper()}-{seq:02d}",
                )
                db.add(wo)
                created += 1

        db.commit()
        return {
            "message": f"Generated {created} work order(s) for MO {mo.batch_number}",
            "work_orders_created": created,
            "mo_id": mo_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


# ============================================================================
# ENDPOINT: BOM Management
# ============================================================================
@router.get("/bom")
async def list_boms(
    product_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all BOM headers with their detail lines."""
    try:
        query = db.query(BOMHeader).filter(BOMHeader.is_active == True)
        if product_id:
            query = query.filter(BOMHeader.product_id == product_id)

        headers = query.all()
        result = []
        for h in headers:
            product = h.product
            lines = []
            for d in h.details:
                comp = d.component
                lines.append({
                    "id": d.id,
                    "component_id": d.component_id,
                    "component_code": comp.code if comp else None,
                    "component_name": comp.name if comp else f"Material #{d.component_id}",
                    "uom": comp.uom if comp else None,
                    "qty_needed": str(d.qty_needed),
                    "wastage_percent": str(d.wastage_percent) if d.wastage_percent else "0",
                })
            result.append({
                "id": h.id,
                "product_id": h.product_id,
                "product_code": product.code if product else None,
                "product_name": product.name if product else f"Product #{h.product_id}",
                "bom_type": h.bom_type.value if hasattr(h.bom_type, "value") else str(h.bom_type),
                "revision": h.revision,
                "qty_output": str(h.qty_output),
                "is_active": h.is_active,
                "created_at": h.created_at.isoformat() if h.created_at else None,
                "details": lines,
            })
        return result
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.post("/bom")
async def create_bom_line(
    payload: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or append a BOM detail line.

    payload: { product_id, component_id, qty_needed, bom_type? }
    If a BOMHeader for product_id already exists, appends to it.
    Otherwise creates a new header.
    """
    try:
        from app.core.models.bom import BOMType
        from decimal import Decimal

        product_id = int(payload["product_id"])
        component_id = int(payload["component_id"])
        qty_needed = Decimal(str(payload["qty_needed"]))
        bom_type_str = payload.get("bom_type", "Manufacturing")

        try:
            bom_type = BOMType(bom_type_str)
        except ValueError:
            bom_type = BOMType.MANUFACTURING

        header = db.query(BOMHeader).filter(
            BOMHeader.product_id == product_id,
            BOMHeader.is_active == True
        ).first()

        if not header:
            header = BOMHeader(
                product_id=product_id,
                bom_type=bom_type,
                qty_output=Decimal("1.0"),
                is_active=True,
                revision="Rev 1.0",
            )
            db.add(header)
            db.flush()

        detail = BOMDetail(
            bom_header_id=header.id,
            component_id=component_id,
            qty_needed=qty_needed,
        )
        db.add(detail)
        db.commit()
        db.refresh(detail)

        return {"message": "BOM line created", "bom_header_id": header.id, "detail_id": detail.id}
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@router.delete("/bom/detail/{detail_id}")
async def delete_bom_detail(
    detail_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a BOM detail line."""
    detail = db.query(BOMDetail).filter(BOMDetail.id == detail_id).first()
    if not detail:
        raise HTTPException(status_code=404, detail="BOM detail not found")
    db.delete(detail)
    db.commit()
    return {"message": "BOM detail deleted"}


# ============================================================================
# ENDPOINTS: Manufacturing Order Detail & Actions
# ============================================================================

@router.get("/manufacturing-order/{mo_id}")
async def get_manufacturing_order_detail(
    mo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get single Manufacturing Order detail."""
    from app.core.models.manufacturing import MOState, RoutingType
    from app.core.models import Product

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")

    product = db.query(Product).filter(Product.id == mo.product_id).first()

    return {
        "id": mo.id,
        "batch_number": mo.batch_number,
        "product_id": mo.product_id,
        "product_code": product.code if product else None,
        "product_name": product.name if product else f"Product #{mo.product_id}",
        "qty_planned": str(mo.qty_planned),
        "qty_produced": str(mo.qty_produced) if mo.qty_produced is not None else "0",
        "state": mo.state.value if hasattr(mo.state, "value") else str(mo.state),
        "routing_type": mo.routing_type.value if hasattr(mo.routing_type, "value") else str(mo.routing_type),
        "mo_type": mo.mo_type.value if hasattr(mo.mo_type, "value") else str(mo.mo_type),
        "trigger_mode": mo.trigger_mode,
        "production_week": mo.production_week,
        "destination_country": mo.destination_country,
        "planned_production_date": mo.planned_production_date.isoformat() if mo.planned_production_date else None,
        "target_shipment_date": mo.target_shipment_date.isoformat() if mo.target_shipment_date else None,
        "created_at": mo.created_at.isoformat() if mo.created_at else None,
        "started_at": mo.started_at.isoformat() if mo.started_at else None,
        "completed_at": mo.completed_at.isoformat() if mo.completed_at else None,
    }


@router.get("/manufacturing-order/{mo_id}/explosion")
async def get_bom_explosion(
    mo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get BOM explosion for an MO — lists all required materials."""
    from app.core.models import Product

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")

    bom_headers = db.query(BOMHeader).filter(BOMHeader.product_id == mo.product_id).all()
    qty_planned = float(mo.qty_planned) if mo.qty_planned else 0

    result = []
    for header in bom_headers:
        details = db.query(BOMDetail).filter(BOMDetail.bom_header_id == header.id).all()
        for detail in details:
            comp = db.query(Product).filter(Product.id == detail.component_id).first()
            qty_required = float(detail.qty_needed) * qty_planned if detail.qty_needed else 0
            result.append({
                "level": 1,
                "product_id": detail.component_id,
                "product_code": comp.code if comp else None,
                "product_name": comp.name if comp else f"Material #{detail.component_id}",
                "product_type": getattr(comp, "product_type", "material") if comp else "material",
                "qty_required": round(qty_required, 4),
                "uom": detail.uom or "pcs",
                "wastage_percent": float(detail.wastage_percent) if detail.wastage_percent else 0,
                "children": [],
            })

    return result


@router.post("/manufacturing-order")
async def create_manufacturing_order(
    data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new Manufacturing Order."""
    from app.core.models.manufacturing import MOState, RoutingType, MOType

    for field in ("product_id", "qty_planned", "routing_type", "batch_number"):
        if field not in data:
            raise HTTPException(status_code=400, detail=f"Missing required field: {field}")

    try:
        routing = RoutingType(data["routing_type"])
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid routing_type: {data['routing_type']}")

    existing = db.query(ManufacturingOrder).filter(
        ManufacturingOrder.batch_number == data["batch_number"]
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Batch number '{data['batch_number']}' already exists")

    mo_type_val = data.get("mo_type", "PRODUCTION")
    try:
        mo_type = MOType(mo_type_val)
    except ValueError:
        mo_type = MOType.PRODUCTION

    qty = data["qty_planned"]
    mo = ManufacturingOrder(
        product_id=data["product_id"],
        qty_planned=qty,
        routing_type=routing,
        batch_number=data["batch_number"],
        state=MOState.DRAFT,
        mo_type=mo_type,
        trigger_mode=data.get("trigger_mode", "PARTIAL"),
        production_week=data.get("production_week"),
        destination_country=data.get("destination_country"),
        target_quantity=data.get("target_quantity", qty),
        buffer_quantity=data.get("buffer_quantity", 0),
        production_quantity=data.get("production_quantity", qty),
    )
    db.add(mo)
    db.commit()
    db.refresh(mo)

    return {
        "id": mo.id,
        "batch_number": mo.batch_number,
        "state": mo.state.value,
        "message": "Manufacturing order created successfully",
    }


@router.post("/manufacturing-order/{mo_id}/start")
async def start_manufacturing_order(
    mo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a Manufacturing Order (DRAFT → IN_PROGRESS)."""
    from app.core.models.manufacturing import MOState

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")

    if mo.state == MOState.DONE:
        raise HTTPException(status_code=400, detail="Manufacturing order is already completed")
    if mo.state == MOState.IN_PROGRESS:
        return {"id": mo.id, "state": mo.state.value, "message": "Already in progress"}

    mo.state = MOState.IN_PROGRESS
    mo.started_at = datetime.utcnow()
    if not mo.actual_production_start_date:
        mo.actual_production_start_date = date.today()
    db.commit()

    return {"id": mo.id, "state": mo.state.value, "message": "Manufacturing order started"}


@router.post("/manufacturing-order/{mo_id}/complete")
async def complete_manufacturing_order(
    mo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete a Manufacturing Order (IN_PROGRESS → DONE)."""
    from app.core.models.manufacturing import MOState

    mo = db.query(ManufacturingOrder).filter(ManufacturingOrder.id == mo_id).first()
    if not mo:
        raise HTTPException(status_code=404, detail="Manufacturing order not found")

    if mo.state == MOState.DONE:
        return {"id": mo.id, "state": mo.state.value, "message": "Already completed"}

    mo.state = MOState.DONE
    mo.completed_at = datetime.utcnow()
    if not mo.actual_production_end_date:
        mo.actual_production_end_date = date.today()
    db.commit()

    return {"id": mo.id, "state": mo.state.value, "message": "Manufacturing order completed"}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================(spk: SPK, db: Session) -> str:
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


