"""Masterdata CRUD API — Products, Categories, Suppliers.

Endpoints:
  GET/POST        /masterdata/products
  GET/PUT/DELETE  /masterdata/products/{id}
  GET/POST        /masterdata/categories
  GET/PUT/DELETE  /masterdata/categories/{id}
  GET/POST        /masterdata/suppliers
  GET/PUT/DELETE  /masterdata/suppliers/{id}

Access:
  - All authenticated users can VIEW (GET)
  - CREATE / UPDATE / DELETE requires ADMIN, SUPERADMIN or DEVELOPER role
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.models.products import Category, Partner, PartnerType, Product, ProductType, UOM
from app.core.models.users import User
from app.api.v1.auth import get_current_user

router = APIRouter(prefix="/masterdata", tags=["Masterdata"])

# ── Role helpers ──────────────────────────────────────────────────────────────
# Full write access (CREATE + UPDATE + DELETE): system admins
ADMIN_ROLES = {"Developer", "Superadmin", "Admin"}
# Create + update (no delete): PPIC Manager & Warehouse Admin per ROLE_PERMISSIONS
WRITE_ROLES = ADMIN_ROLES | {"PPIC Manager", "Warehouse Admin", "Purchasing Head"}


def _require_admin(user: User):
    """Full CRUD — admin-only (create / update / delete)."""
    if user.role.value not in ADMIN_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Admin / Superadmin / Developer can modify masterdata",
        )


def _require_write(user: User):
    """Create / update (not delete) — extended roles."""
    if user.role.value not in WRITE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to modify masterdata",
        )


# ══════════════════════════════════════════════════════════════════════════════
# CATEGORIES
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/categories")
def list_categories(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    cats = db.query(Category).order_by(Category.name).all()
    return [{"id": c.id, "name": c.name, "description": c.description} for c in cats]


@router.post("/categories", status_code=201)
def create_category(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "name is required")
    if db.query(Category).filter(Category.name == name).first():
        raise HTTPException(400, f"Category '{name}' already exists")
    cat = Category(name=name, description=body.get("description"))
    db.add(cat); db.commit(); db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "description": cat.description}


@router.put("/categories/{cat_id}")
def update_category(
    cat_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    if "name" in body and body["name"]:
        cat.name = body["name"].strip()
    if "description" in body:
        cat.description = body["description"]
    db.commit(); db.refresh(cat)
    return {"id": cat.id, "name": cat.name, "description": cat.description}


@router.delete("/categories/{cat_id}", status_code=200)
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    cat = db.query(Category).filter(Category.id == cat_id).first()
    if not cat:
        raise HTTPException(404, "Category not found")
    # Prevent deletion if products are linked
    if cat.products:
        raise HTTPException(
            400,
            f"Cannot delete: {len(cat.products)} product(s) linked to this category",
        )
    db.delete(cat); db.commit()
    return {"message": f"Category '{cat.name}' deleted"}


# ══════════════════════════════════════════════════════════════════════════════
# PRODUCTS (Materials + Articles)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/products")
def list_products(
    search: str = Query("", description="Filter by code or name"),
    product_type: str = Query("", description="Filter by type"),
    category_id: int = Query(0, description="Filter by category"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Product)
    if search:
        q = q.filter(
            Product.code.ilike(f"%{search}%") | Product.name.ilike(f"%{search}%")
        )
    if product_type:
        try:
            q = q.filter(Product.type == ProductType(product_type))
        except ValueError:
            pass
    if category_id:
        q = q.filter(Product.category_id == category_id)

    total = q.count()
    products = q.order_by(Product.code).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [_fmt_product(p) for p in products],
    }


@router.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    return _fmt_product(p)


@router.post("/products", status_code=201)
def create_product(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    code = (body.get("code") or "").strip().upper()
    name = (body.get("name") or "").strip()
    if not code or not name:
        raise HTTPException(400, "code and name are required")
    if db.query(Product).filter(Product.code == code).first():
        raise HTTPException(400, f"Product code '{code}' already exists")

    # Validate type and UOM
    try:
        ptype = ProductType(body.get("type", "Raw Material"))
    except ValueError:
        raise HTTPException(400, f"Invalid type. Choose from: {[e.value for e in ProductType]}")
    try:
        uom = UOM(body.get("uom", "Pcs"))
    except ValueError:
        raise HTTPException(400, f"Invalid UOM. Choose from: {[e.value for e in UOM]}")

    cat_id = body.get("category_id")
    if cat_id and not db.query(Category).filter(Category.id == cat_id).first():
        raise HTTPException(400, f"Category id {cat_id} not found")
    if not cat_id:
        # Auto-assign default category
        cat = db.query(Category).first()
        if not cat:
            raise HTTPException(400, "No categories exist. Create a category first.")
        cat_id = cat.id

    p = Product(
        code=code,
        name=name,
        type=ptype,
        uom=uom,
        category_id=cat_id,
        min_stock=float(body.get("min_stock", 0) or 0),
        is_active=True,
    )
    db.add(p); db.commit(); db.refresh(p)
    return _fmt_product(p)


@router.put("/products/{product_id}")
def update_product(
    product_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")

    if "name" in body and body["name"]:
        p.name = body["name"].strip()
    if "type" in body and body["type"]:
        try:
            p.type = ProductType(body["type"])
        except ValueError:
            raise HTTPException(400, f"Invalid type")
    if "uom" in body and body["uom"]:
        try:
            p.uom = UOM(body["uom"])
        except ValueError:
            raise HTTPException(400, f"Invalid UOM")
    if "category_id" in body and body["category_id"]:
        p.category_id = int(body["category_id"])
    if "min_stock" in body:
        p.min_stock = float(body["min_stock"] or 0)
    if "is_active" in body:
        p.is_active = bool(body["is_active"])

    db.commit(); db.refresh(p)
    return _fmt_product(p)


@router.delete("/products/{product_id}", status_code=200)
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(404, "Product not found")
    # Soft-delete: set is_active = False (preserve BOM / stock references)
    p.is_active = False
    db.commit()
    return {"message": f"Product '{p.code}' deactivated (soft-delete)"}


# ══════════════════════════════════════════════════════════════════════════════
# SUPPLIERS (Partners)
# ══════════════════════════════════════════════════════════════════════════════

@router.get("/suppliers")
def list_suppliers(
    search: str = Query(""),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Partner).filter(Partner.type == PartnerType.SUPPLIER)
    if search:
        q = q.filter(Partner.name.ilike(f"%{search}%"))
    suppliers = q.order_by(Partner.name).all()
    return [_fmt_partner(s) for s in suppliers]


@router.post("/suppliers", status_code=201)
def create_supplier(
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    name = (body.get("name") or "").strip()
    if not name:
        raise HTTPException(400, "name is required")
    s = Partner(
        name=name,
        type=PartnerType.SUPPLIER,
        address=body.get("address"),
        contact_person=body.get("contact_person"),
        phone=body.get("phone"),
        email=body.get("email"),
    )
    db.add(s); db.commit(); db.refresh(s)
    return _fmt_partner(s)


@router.put("/suppliers/{supplier_id}")
def update_supplier(
    supplier_id: int,
    body: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_write(current_user)
    s = db.query(Partner).filter(Partner.id == supplier_id, Partner.type == PartnerType.SUPPLIER).first()
    if not s:
        raise HTTPException(404, "Supplier not found")
    for field in ("name", "address", "contact_person", "phone", "email"):
        if field in body:
            setattr(s, field, body[field])
    db.commit(); db.refresh(s)
    return _fmt_partner(s)


@router.delete("/suppliers/{supplier_id}", status_code=200)
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_admin(current_user)
    s = db.query(Partner).filter(Partner.id == supplier_id, Partner.type == PartnerType.SUPPLIER).first()
    if not s:
        raise HTTPException(404, "Supplier not found")
    db.delete(s); db.commit()
    return {"message": f"Supplier '{s.name}' deleted"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt_product(p: Product) -> dict:
    return {
        "id": p.id,
        "code": p.code,
        "name": p.name,
        "type": p.type.value if p.type else None,
        "uom": p.uom.value if p.uom else None,
        "category_id": p.category_id,
        "category_name": p.category.name if p.category else None,
        "min_stock": float(p.min_stock or 0),
        "is_active": p.is_active,
        "pcs_per_carton": p.pcs_per_carton,
        "cartons_per_pallet": p.cartons_per_pallet,
        "created_at": p.created_at.isoformat() if p.created_at else None,
    }


def _fmt_partner(s: Partner) -> dict:
    return {
        "id": s.id,
        "name": s.name,
        "address": s.address,
        "contact_person": s.contact_person,
        "phone": s.phone,
        "email": s.email,
        "created_at": s.created_at.isoformat() if s.created_at else None,
    }
