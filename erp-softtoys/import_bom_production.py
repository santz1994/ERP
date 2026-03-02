"""
BOM Production Import Script
Imports all articles + BOMs from docs/Masterdata/BOM Production/*.xlsx

Files:
  - Cutting.xlsx      → WIP Cutting BOMs
  - Embo.xlsx         → WIP Embroidery BOMs
  - Sewing.xlsx       → WIP Sewing BOMs
  - Finishing.xlsx    → WIP Finishing BOMs
  - Finishing Goods.xlsx → Finished Good articles
  - Packing.xlsx      → WIP Packing BOMs

Strategy:
  1. Read all 6 files, parse products + BOM lines
  2. Upsert all products (FINISH_GOOD, WIP, RAW_MATERIAL)
  3. Create BOMHeader + BOMDetail per product per department
  4. Build CONSOLIDATED flat BOM for each FINISH_GOOD article
     (recursive explosion → leaf RAW_MATERIAL nodes only)
     → Used by PO BOM explosion endpoint
"""

import sys
import os
import re
from pathlib import Path
from collections import defaultdict
from decimal import Decimal
from datetime import datetime
from typing import Dict, Tuple

import pandas as pd  # type: ignore[import-untyped]

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session  # noqa: E402
from app.core.database import SessionLocal  # noqa: E402
from app.core.models.products import Product, ProductType, Category  # noqa: E402
from app.core.models.bom import BOMHeader, BOMDetail, BOMType  # noqa: E402

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

BOM_DIR = Path("../docs/Masterdata/BOM Production")

FILES = {
    "Cutting":          BOM_DIR / "Cutting.xlsx",
    "Embo":             BOM_DIR / "Embo.xlsx",
    "Sewing":           BOM_DIR / "Sewing.xlsx",
    "Finishing":        BOM_DIR / "Finishing.xlsx",
    "Finishing Goods":  BOM_DIR / "Finishing Goods.xlsx",
    "Packing":          BOM_DIR / "Packing.xlsx",
}

# Category name → DB id mapping (auto-resolved)
CAT_MAP = {
    "Finished Goods":   None,
    "WIP Cutting":      None,
    "WIP Embroidery":   None,
    "WIP Sewing":       None,
    "WIP Finishing":    None,
    "WIP Packing":      None,
    "Raw Materials":    None,
}

FILE_WIP_CAT = {
    "Cutting":         "WIP Cutting",
    "Embo":            "WIP Embroidery",
    "Sewing":          "WIP Sewing",
    "Finishing":       "WIP Finishing",
    "Finishing Goods": "Finished Goods",
    "Packing":         "WIP Packing",
}

UOM_MAP = {
    "PCE":  "Pcs",  "PCS":  "Pcs",  "PIECE": "Pcs",  "EA": "Pcs",
    "YARD": "Yard", "YD":   "Yard",
    "KG":   "Kg",   "KILO": "Kg",
    "M":    "Meter", "METER": "Meter", "MTR":  "Meter",
    "ROLL": "Roll",
    "CM":   "Cm",
}

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────


def ts() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str, level: str = "INFO"):
    icons = {"INFO": "ℹ️", "OK": "✅", "WARN": "⚠️", "ERR": "❌", "HEAD": "📋"}
    print(f"[{ts()}] {icons.get(level, 'ℹ️')} {msg}")


def parse_code_name(raw: str) -> Tuple[str, str]:
    """Extract code + name from '[CODE] Name' or 'Name_WIP_DEPT' strings."""
    raw = str(raw).strip()
    m = re.match(r'^\[([^\]]+)\]\s*(.+)$', raw)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    # No bracket code — use truncated string as code
    code = raw[:50].replace(" ", "_").upper()
    return code, raw


def normalize_uom(raw: str) -> str:
    if not raw or (isinstance(raw, float)):
        return "Pcs"
    u = str(raw).strip().upper()
    # Handle CTN variants
    if u.startswith("CTN"):
        return "Pcs"
    return UOM_MAP.get(u, "Pcs")


def resolve_categories(db: Session):
    """Populate CAT_MAP with real DB ids, create missing ones."""
    for name in CAT_MAP:
        cat = db.query(Category).filter(Category.name == name).first()
        if not cat:
            cat = Category(
                name=name,
                description=f"Auto-created from BOM import: {name}",
            )
            db.add(cat)
            db.flush()
            log(f"Created category '{name}'", "OK")
        CAT_MAP[name] = cat.id  # type: ignore[assignment]


def infer_product_type(product_str: str) -> str:
    """Infer product type from name string."""
    s = str(product_str).upper()
    if "_WIP_" in s or "_SEMI_" in s:
        return "WIP"
    # Check if it has bracket code that suggests a raw material
    if re.match(r'^\[[A-Z]{2,}', product_str):
        return "RAW"
    return "OTHER"


def get_or_create_product(
    db: Session,
    code: str,
    name: str,
    p_type: ProductType,
    uom: str,
    cat_id: int,
) -> Product:
    """Upsert product by code."""
    product = db.query(Product).filter(Product.code == code).first()
    if not product:
        product = Product(
            code=code,
            name=name[:255],
            type=p_type,
            uom=uom,
            category_id=cat_id,
            is_active=True,
        )
        db.add(product)
        db.flush()
    else:
        # Update name/type if it was a placeholder
        if product.name != name[:255]:
            product.name = name[:255]  # type: ignore[assignment]
        if product.type != p_type:
            product.type = p_type  # type: ignore[assignment]
        db.flush()
    return product


# ─────────────────────────────────────────────
# Step 1: Load all BOM files
# ─────────────────────────────────────────────

def load_bom_files() -> Dict[str, pd.DataFrame]:
    """Read all BOM Excel files and forward-fill the Product column."""
    dfs = {}
    for name, path in FILES.items():
        if not path.exists():
            log(f"File not found: {path}", "WARN")
            continue
        df = pd.read_excel(path)

        # Forward-fill 'Product' column (blank rows belong to the same BOM)
        df["Product"] = df["Product"].ffill()
        df["Product/Name"] = df["Product/Name"].ffill()
        df["Quantity"] = df["Quantity"].ffill()
        df["Unit of Measure"] = df["Unit of Measure"].ffill()

        # Keep only rows that have a BOM line component
        df = df[df["BoM Lines/Component"].notna()].copy()

        product_count = df['Product'].nunique()
        log(f"Loaded {name}: {len(df)} BOM lines, {product_count} products", "OK")
        dfs[name] = df
    return dfs


# ─────────────────────────────────────────────
# Step 2 & 3: Upsert products + create department BOMs
# ─────────────────────────────────────────────

def import_department_boms(
    db: Session,
    dfs: Dict[str, pd.DataFrame],
) -> Dict[str, int]:
    """Import all products and create BOMHeader/BOMDetail per department.

    Returns dict: product_code → product_id
    """
    log("=" * 60, "HEAD")
    log("STEP 1-2: Upsert products + department BOMs", "HEAD")
    log("=" * 60, "HEAD")

    product_id_map: Dict[str, int] = {}   # code → product.id
    bom_counter = 0
    detail_counter = 0

    for dept_name, df in dfs.items():
        wip_cat_name = FILE_WIP_CAT[dept_name]
        wip_cat_id = CAT_MAP[wip_cat_name]
        raw_cat_id = CAT_MAP["Raw Materials"]

        is_fg_file = dept_name == "Finishing Goods"

        log(f"\n--- Processing {dept_name} ({len(df)} lines) ---")

        # Group by Product
        for product_str, grp in df.groupby("Product"):
            qty_raw = grp["Quantity"].iloc[0]
            qty_output = float(qty_raw) if pd.notna(qty_raw) else 1.0
            uom_str = normalize_uom(str(grp["Unit of Measure"].iloc[0]))

            # Parse product code/name
            code, name = parse_code_name(str(product_str))

            # Determine product type from file/name
            if is_fg_file:
                p_type = ProductType.FINISH_GOOD
                cat_id = CAT_MAP["Finished Goods"]
            elif infer_product_type(str(product_str)) == "WIP":
                p_type = ProductType.WIP
                cat_id = wip_cat_id
            else:
                # Still treat as WIP (it's a sub-product in a dept BOM)
                p_type = ProductType.WIP
                cat_id = wip_cat_id

            # Upsert parent product
            parent = get_or_create_product(
                db, code, name, p_type, uom_str,
                cat_id,  # type: ignore[arg-type]
            )
            product_id_map[code] = parent.id  # type: ignore[assignment]

            # Delete existing BOMHeader for this product + dept to avoid duplication
            # (keyed by product_id + revision tag)
            # Revision tag must fit VARCHAR(10)
            dept_key = {
                "Cutting": "CUT-1.0",
                "Embo": "EMB-1.0",
                "Sewing": "SEW-1.0",
                "Finishing": "FIN-1.0",
                "Finishing Goods": "FGD-1.0",
                "Packing": "PCK-1.0",
            }.get(dept_name, dept_name[:7] + "-1")
            dept_revision = dept_key
            existing_bom = (
                db.query(BOMHeader)
                .filter(
                    BOMHeader.product_id == parent.id,
                    BOMHeader.revision == dept_revision,
                )
                .first()
            )
            if existing_bom:
                db.delete(existing_bom)
                db.flush()

            bom_header = BOMHeader(
                product_id=parent.id,
                bom_type=BOMType.MANUFACTURING,
                qty_output=Decimal(str(max(qty_output, 1.0))),
                is_active=True,
                revision=dept_revision,
                revision_reason=f"Imported from {dept_name}.xlsx",
            )
            db.add(bom_header)
            db.flush()
            bom_counter += 1

            # Process BOM lines
            for _, row in grp.iterrows():
                comp_str = str(row["BoM Lines/Component"]).strip()
                comp_qty_raw = row["BoM Lines/Quantity"]
                comp_uom_raw = row["BoM Lines/Product Unit of Measure"]

                comp_qty = float(comp_qty_raw) if pd.notna(comp_qty_raw) else 1.0
                comp_uom = normalize_uom(
                    str(comp_uom_raw) if pd.notna(comp_uom_raw) else "Pcs"
                )

                comp_code, comp_name = parse_code_name(comp_str)

                # Determine component type
                comp_type_hint = infer_product_type(comp_str)
                if comp_type_hint == "WIP":
                    comp_type = ProductType.WIP
                    comp_cat_id = wip_cat_id  # same dept (approximate)
                else:
                    comp_type = ProductType.RAW_MATERIAL
                    comp_cat_id = raw_cat_id

                comp_product = get_or_create_product(
                    db, comp_code, comp_name, comp_type, comp_uom,
                    comp_cat_id,  # type: ignore[arg-type]
                )
                product_id_map[comp_code] = comp_product.id  # type: ignore[assignment]

                bom_detail = BOMDetail(
                    bom_header_id=bom_header.id,
                    component_id=comp_product.id,
                    qty_needed=Decimal(str(max(comp_qty, 0.0))),
                    wastage_percent=Decimal("0"),
                    has_variants=False,
                )
                db.add(bom_detail)
                detail_counter += 1

        db.commit()
        log(f"  ✅ {dept_name}: committed", "OK")

    log(
        f"\nDept BOMs: {bom_counter} headers / {detail_counter} details",
        "OK",
    )
    return product_id_map


# ─────────────────────────────────────────────
# Step 4: Build consolidated FLAT BOMs for FINISH_GOOD
# ─────────────────────────────────────────────

def build_consolidated_bom(db: Session, _product_id_map: Dict[str, int]):
    """
    For every FINISH_GOOD article, recursively walk the department BOMs
    and collect all leaf RAW_MATERIAL components (aggregated quantities).

    Creates (or replaces) a BOMHeader with revision 'PURCH-1.0' for each FG.
    This BOM is used by the purchasing BOM explosion endpoint.
    """
    log("=" * 60, "HEAD")
    log("STEP 3: Build consolidated purchasing BOMs (FINISH_GOOD)", "HEAD")
    log("=" * 60, "HEAD")

    articles = (
        db.query(Product)
        .filter(Product.type == ProductType.FINISH_GOOD, Product.is_active)
        .all()
    )
    log(f"Found {len(articles)} FINISH_GOOD articles to process")

    created = 0
    skipped = 0

    for article in articles:
        # Recursively collect raw materials
        raw_materials = _collect_raw_materials(
            db, int(article.id), qty_multiplier=1.0, visited=set()
        )

        if not raw_materials:
            skipped += 1
            continue

        # Delete old consolidated BOM
        old_bom = (
            db.query(BOMHeader)
            .filter(
                BOMHeader.product_id == article.id,
                BOMHeader.revision == "PURCH-1.0",
            )
            .first()
        )
        if old_bom:
            db.delete(old_bom)
            db.flush()

        # Create new consolidated BOM header
        bom_header = BOMHeader(
            product_id=article.id,
            bom_type=BOMType.MANUFACTURING,
            qty_output=Decimal("1"),
            is_active=True,
            revision="PURCH-1.0",
            revision_reason="Auto-consolidated from BOM Production files",
        )
        db.add(bom_header)
        db.flush()

        # Create BOM detail lines (aggregate duplicate materials)
        for comp_id, total_qty in raw_materials.items():
            db.add(BOMDetail(
                bom_header_id=bom_header.id,
                component_id=comp_id,
                qty_needed=Decimal(str(round(float(total_qty), 6))),
                wastage_percent=Decimal("0"),
                has_variants=False,
            ))

        db.commit()
        created += 1

        if created % 50 == 0:
            log(f"  Progress: {created}/{len(articles)} articles processed")

    log(
        f"Consolidated BOMs: {created} created, {skipped} skipped (no raw materials)",
        "OK",
    )


def _collect_raw_materials(
    db: Session,
    product_id: int,
    qty_multiplier: float,
    visited: set,
) -> Dict[int, float]:
    """
    Recursively walk all BOMHeaders for product_id,
    return dict {component_product_id: total_qty} for leaf RAW_MATERIAL nodes.
    """
    if product_id in visited:
        return {}
    visited.add(product_id)

    result: Dict[int, float] = defaultdict(float)

    # Find all active BOMs for this product (department BOMs, not consolidated)
    bom_headers = (
        db.query(BOMHeader)
        .filter(
            BOMHeader.product_id == product_id,
            BOMHeader.is_active,
            BOMHeader.revision != "PURCH-1.0",
        )
        .all()
    )

    for bom in bom_headers:
        qty_out = float(bom.qty_output) if bom.qty_output else 1.0
        scale = qty_multiplier / max(qty_out, 1.0)

        details = (
            db.query(BOMDetail)
            .filter(BOMDetail.bom_header_id == bom.id)
            .all()
        )
        for detail in details:
            comp = (
                db.query(Product)
                .filter(Product.id == detail.component_id)
                .first()
            )
            if not comp:
                continue

            required_qty = float(detail.qty_needed) * scale

            if comp.type == ProductType.RAW_MATERIAL:
                result[int(comp.id)] += required_qty
            elif comp.type == ProductType.WIP:
                # Recurse into WIP
                sub_materials = _collect_raw_materials(
                    db, int(comp.id), required_qty, visited.copy()
                )
                for sub_id, sub_qty in sub_materials.items():
                    result[sub_id] += sub_qty

    return dict(result)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    log("=" * 60, "HEAD")
    log("BOM PRODUCTION IMPORT — START", "HEAD")
    log("=" * 60, "HEAD")
    log(f"BOM directory: {BOM_DIR.resolve()}")

    db: Session = SessionLocal()
    try:
        # Resolve categories
        resolve_categories(db)

        # Load files
        dfs = load_bom_files()
        if not dfs:
            log("No BOM files loaded. Aborting.", "ERR")
            return

        # Import department BOMs
        product_id_map = import_department_boms(db, dfs)
        log(f"Total products in map: {len(product_id_map)}", "OK")

        # Build consolidated purchasing BOMs
        build_consolidated_bom(db, product_id_map)

        # Final summary
        log("=" * 60, "HEAD")
        log("IMPORT SUMMARY", "HEAD")
        log("=" * 60, "HEAD")

        products = db.query(Product).all()
        fg = sum(1 for p in products if p.type == ProductType.FINISH_GOOD)
        wip = sum(1 for p in products if p.type == ProductType.WIP)
        raw = sum(1 for p in products if p.type == ProductType.RAW_MATERIAL)
        bom_total = db.query(BOMHeader).count()
        detail_total = db.query(BOMDetail).count()
        purch_boms = db.query(BOMHeader).filter(BOMHeader.revision == "PURCH-1.0").count()

        log(f"Products — FG: {fg} | WIP: {wip} | RAW: {raw}", "OK")
        log(f"BOM Headers: {bom_total} total ({purch_boms} PURCH-1.0)", "OK")
        log(f"BOM Details total: {detail_total}", "OK")
        log("✅ IMPORT COMPLETE", "OK")

    except Exception as e:  # pylint: disable=broad-exception-caught
        db.rollback()
        import traceback
        log(f"FATAL ERROR: {e}", "ERR")
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
