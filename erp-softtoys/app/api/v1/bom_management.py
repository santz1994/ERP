"""BOM Management CRUD API.

Endpoints:
  GET        /bom-management/headers              — list all BOM headers
  GET        /bom-management/headers/{id}         — detail + lines
  POST       /bom-management/headers              — create BOM header
  PUT        /bom-management/headers/{id}         — update header
  DELETE     /bom-management/headers/{id}         — delete header (+ all lines)
  POST       /bom-management/headers/{id}/details — add a BOM line
  PUT        /bom-management/details/{id}         — update a BOM line
  DELETE     /bom-management/details/{id}         — remove a BOM line

Access:
  - VIEW (GET): all authenticated users
  - WRITE: Admin / Superadmin / Developer
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.core.database import get_db
from app.core.models.bom import BOMCategory, BOMDetail, BOMHeader, BOMType
from app.core.models.products import Product
from app.core.models.users import User, UserRole
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/bom-management", tags=["BOM Management"])

# Roles allowed to CREATE / UPDATE / DELETE BOM data
BOM_WRITE_ROLES = {
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
}


def _require_admin(user: User):
    """Raise 403 if user does not have BOM write privileges."""
    if user.role not in BOM_WRITE_ROLES:
        raise HTTPException(
            status_code=403,
            detail=(
                f"Only Admin / Superadmin / Manager / Developer can modify BOM data. "
                f"Your role: {user.role.value}"
            ),
        )


# ══════════════════════════════════════════════════════════════════════════════
# BOM HEADERS
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/headers")
def list_bom_headers(
    search: str = Query("", description="Filter by article code or name"),
    revision: str = Query("", description="Filter by revision"),
    active_only: bool = Query(False),
    bom_category: str = Query("", description="Filter by category: Production or Purchase"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    # Subquery: count details per header (avoids N+1 lazy-load on each _fmt_header)
    detail_count_sq = (
        db.query(BOMDetail.bom_header_id, func.count(BOMDetail.id).label("detail_count"))
        .group_by(BOMDetail.bom_header_id)
        .subquery()
    )

    q = (
        db.query(BOMHeader, detail_count_sq.c.detail_count)
        .options(joinedload(BOMHeader.product).joinedload(Product.category))
        .join(Product, BOMHeader.product_id == Product.id)
        .outerjoin(detail_count_sq, BOMHeader.id == detail_count_sq.c.bom_header_id)
    )
    if search:
        q = q.filter(
            Product.code.ilike(f"%{search}%") | Product.name.ilike(f"%{search}%")
        )
    if revision:
        q = q.filter(BOMHeader.revision.ilike(f"%{revision}%"))
    if active_only:
        q = q.filter(BOMHeader.is_active == True)
    if bom_category:
        try:
            cat = BOMCategory(bom_category)
            q = q.filter(BOMHeader.bom_category == cat)
        except ValueError:
            pass

    total = q.count()
    rows = (
        q.order_by(Product.code, BOMHeader.revision)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_fmt_header(h, cnt) for h, cnt in rows],
    }


@router.get("/headers/{header_id}")
def get_bom_header(
    header_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    h = (
        db.query(BOMHeader)
        .options(
            joinedload(BOMHeader.product).joinedload(Product.category),
            joinedload(BOMHeader.details).joinedload(BOMDetail.component).joinedload(Product.category),
        )
        .filter(BOMHeader.id == header_id)
        .first()
    )
    if not h:
        raise HTTPException(404, "BOM Header not found")
    return {**_fmt_header(h), "details": [_fmt_detail(d) for d in h.details]}


@router.post("/headers", status_code=201)
def create_bom_header(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    product_id = body.get("product_id")
    if not product_id:
        raise HTTPException(400, "product_id is required")
    if not db.query(Product).filter(Product.id == product_id).first():
        raise HTTPException(404, f"Product id {product_id} not found")

    revision = (body.get("revision") or "Rev 1.0").strip()
    # Check duplicate
    existing = db.query(BOMHeader).filter(
        BOMHeader.product_id == product_id,
        BOMHeader.revision == revision,
    ).first()
    if existing:
        raise HTTPException(400, f"BOM revision '{revision}' already exists for this product")

    try:
        bom_type = BOMType(body.get("bom_type", BOMType.MANUFACTURING.value))
    except ValueError:
        bom_type = BOMType.MANUFACTURING

    cat_str = body.get("bom_category", BOMCategory.PRODUCTION.value)
    try:
        bom_cat = BOMCategory(cat_str)
    except ValueError:
        bom_cat = BOMCategory.PRODUCTION

    h = BOMHeader(
        product_id=product_id,
        bom_type=bom_type,
        bom_category=bom_cat,
        revision=revision,
        qty_output=float(body.get("qty_output", 1) or 1),
        is_active=bool(body.get("is_active", True)),
        revision_reason=body.get("revision_reason"),
        revised_by=current_user.id,
    )
    db.add(h); db.commit(); db.refresh(h)
    return _fmt_header(h)


@router.put("/headers/{header_id}")
def update_bom_header(
    header_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    h = db.query(BOMHeader).filter(BOMHeader.id == header_id).first()
    if not h:
        raise HTTPException(404, "BOM Header not found")

    if "revision" in body and body["revision"]:
        h.revision = body["revision"].strip()
    if "is_active" in body:
        h.is_active = bool(body["is_active"])
    if "qty_output" in body and body["qty_output"]:
        h.qty_output = float(body["qty_output"])
    if "bom_type" in body and body["bom_type"]:
        try:
            h.bom_type = BOMType(body["bom_type"])
        except ValueError:
            pass
    if "revision_reason" in body:
        h.revision_reason = body["revision_reason"]
    if "bom_category" in body and body["bom_category"]:
        try:
            h.bom_category = BOMCategory(body["bom_category"])
        except ValueError:
            pass
    h.revised_by = current_user.id

    db.commit(); db.refresh(h)
    return _fmt_header(h)


@router.delete("/headers/{header_id}", status_code=200)
def delete_bom_header(
    header_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    h = db.query(BOMHeader).filter(BOMHeader.id == header_id).first()
    if not h:
        raise HTTPException(404, "BOM Header not found")
    product_code = h.product.code if h.product else str(header_id)
    revision = h.revision
    db.delete(h)  # cascade deletes BOMDetail rows
    db.commit()
    return {"message": f"BOM '{product_code}' rev='{revision}' deleted (with all detail lines)"}


# ══════════════════════════════════════════════════════════════════════════════
# BOM DETAILS (Lines)
# ══════════════════════════════════════════════════════════════════════════════

@router.post("/headers/{header_id}/details", status_code=201)
def add_bom_detail(
    header_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    h = db.query(BOMHeader).filter(BOMHeader.id == header_id).first()
    if not h:
        raise HTTPException(404, "BOM Header not found")

    component_id = body.get("component_id")
    if not component_id:
        raise HTTPException(400, "component_id is required")
    if not db.query(Product).filter(Product.id == component_id).first():
        raise HTTPException(404, f"Component product id {component_id} not found")

    # Prevent exact duplicate
    duplicate = db.query(BOMDetail).filter(
        BOMDetail.bom_header_id == header_id,
        BOMDetail.component_id == component_id,
    ).first()
    if duplicate:
        raise HTTPException(400, "This component already exists in the BOM. Edit it instead.")

    detail = BOMDetail(
        bom_header_id=header_id,
        component_id=component_id,
        qty_needed=float(body.get("qty_needed", 1) or 1),
        wastage_percent=float(body.get("wastage_percent", 0) or 0),
    )
    db.add(detail); db.commit(); db.refresh(detail)
    # Reload with relations
    detail_reloaded = db.query(BOMDetail).options(
        joinedload(BOMDetail.component).joinedload(Product.category)
    ).filter(BOMDetail.id == detail.id).first()
    return _fmt_detail(detail_reloaded or detail)


@router.put("/details/{detail_id}")
def update_bom_detail(
    detail_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    d = db.query(BOMDetail).filter(BOMDetail.id == detail_id).first()
    if not d:
        raise HTTPException(404, "BOM Detail not found")
    if "qty_needed" in body and body["qty_needed"] is not None:
        d.qty_needed = float(body["qty_needed"])
    if "wastage_percent" in body and body["wastage_percent"] is not None:
        d.wastage_percent = float(body["wastage_percent"])
    db.commit(); db.refresh(d)
    d_reloaded = db.query(BOMDetail).options(
        joinedload(BOMDetail.component).joinedload(Product.category)
    ).filter(BOMDetail.id == detail_id).first()
    return _fmt_detail(d_reloaded or d)


@router.delete("/details/{detail_id}", status_code=200)
def delete_bom_detail(
    detail_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    d = db.query(BOMDetail).filter(BOMDetail.id == detail_id).first()
    if not d:
        raise HTTPException(404, "BOM Detail not found")
    comp_name = d.component.name if d.component else str(detail_id)
    db.delete(d); db.commit()
    return {"message": f"Component '{comp_name}' removed from BOM"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_header(h: BOMHeader, precomputed_detail_count: int | None = None) -> dict:
    # Use pre-computed count when available (avoids N+1 lazy load in list endpoint)
    if precomputed_detail_count is not None:
        cnt = precomputed_detail_count
    elif hasattr(h, "details") and h.details is not None:
        # details were eagerly loaded (detail endpoint)
        cnt = len(h.details)
    else:
        cnt = None
    return {
        "id": h.id,
        "product_id": h.product_id,
        "product_code": h.product.code if h.product else None,
        "product_name": h.product.name if h.product else None,
        "product_type": h.product.type.value if h.product and h.product.type else None,
        "category_name": h.product.category.name if h.product and h.product.category else None,
        "revision": h.revision,
        "bom_type": h.bom_type.value if h.bom_type else None,
        "qty_output": float(h.qty_output or 1),
        "is_active": h.is_active,
        "bom_category": h.bom_category.value if h.bom_category else "Production",
        "revision_reason": h.revision_reason,
        "detail_count": cnt,
        "created_at": h.created_at.isoformat() if h.created_at else None,
        "revision_date": h.revision_date.isoformat() if h.revision_date else None,
    }


def _fmt_detail(d: BOMDetail) -> dict:
    c = d.component
    return {
        "id": d.id,
        "bom_header_id": d.bom_header_id,
        "component_id": d.component_id,
        "component_code": c.code if c else None,
        "component_name": c.name if c else None,
        "component_uom": c.uom.value if c and c.uom else None,
        "component_type": c.type.value if c and c.type else None,
        "category_name": c.category.name if c and c.category else None,
        "qty_needed": float(d.qty_needed or 0),
        "wastage_percent": float(d.wastage_percent or 0),
        "created_at": d.created_at.isoformat() if d.created_at else None,
    }
