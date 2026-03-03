"""Fix BOM qty_needed in DB to exactly match Excel values.
Strategy: match WIP products by BASE NAME (everything before _WIP_) + component code.
"""
import re, openpyxl
from app.core.database import SessionLocal
from app.core.models import Product
from app.core.models.bom import BOMHeader, BOMDetail

BASE = r'D:\Project\ERP2026'

REVISION_TO_FILE = {
    'CUT-1.0':  BASE + r'\docs\Masterdata\BOM Production\Cutting.xlsx',
    'EMB-1.0':  BASE + r'\docs\Masterdata\BOM Production\Embo.xlsx',
    'FIN-1.0':  BASE + r'\docs\Masterdata\BOM Production\Finishing.xlsx',
    'PCK-1.0':  BASE + r'\docs\Masterdata\BOM Production\Packing.xlsx',
    'SEW-1.0':  BASE + r'\docs\Masterdata\BOM Production\Sewing.xlsx',
}

def base_name(name: str) -> str:
    """Strip _WIP_* suffix to get base product name for matching."""
    n = (name or '').strip().lower()
    idx = n.find('_wip_')
    if idx >= 0:
        return n[:idx]
    return n

db = SessionLocal()

# Build excel_map per revision: (base_name, comp_code) -> qty
# Load each revision's xlsx separately so no cross-revision collisions
excel_maps = {}  # revision -> {(base_name, comp_code): qty}

for revision, path in REVISION_TO_FILE.items():
    emap = {}
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    current_product = None

    for row in rows[1:]:
        if row[0]:
            current_product = str(row[0]).strip()
        comp = row[10]
        qty  = row[12]
        if comp and qty is not None and current_product:
            m = re.match(r'\[([^\]]+)\]', str(comp))
            if m:
                comp_code = m.group(1)
                bname = base_name(current_product)
                key = (bname, comp_code)
                # Keep first occurrence (per-piece; don't aggregate here)
                if key not in emap:
                    emap[key] = float(qty)
                # But also store per-full-name for exact matching
    excel_maps[revision] = emap
    print(f'  {revision}: {len(emap)} entries loaded')

# Also build full-name maps for exact matching priority
excel_maps_exact = {}  # revision -> {(full_wip_name_lower, comp_code): qty}
for revision, path in REVISION_TO_FILE.items():
    emap = {}
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    current_product = None
    for row in rows[1:]:
        if row[0]:
            current_product = str(row[0]).strip()
        comp = row[10]
        qty  = row[12]
        if comp and qty is not None and current_product:
            m = re.match(r'\[([^\]]+)\]', str(comp))
            if m:
                comp_code = m.group(1)
                key = (current_product.strip().lower(), comp_code)
                if key not in emap:
                    emap[key] = float(qty)
    excel_maps_exact[revision] = emap

print()

fixed = 0
already_correct = 0
not_found = 0

# Iterate all BOM headers; only process known revisions
bom_headers = db.query(BOMHeader).filter(BOMHeader.revision.in_(list(REVISION_TO_FILE.keys()))).all()

for bh in bom_headers:
    revision = bh.revision
    emap = excel_maps.get(revision, {})
    emap_exact = excel_maps_exact.get(revision, {})

    wip_prod = db.query(Product).filter(Product.id == bh.product_id).first()
    if not wip_prod:
        continue

    wip_full_lower = (wip_prod.name or '').strip().lower()
    wip_bname = base_name(wip_prod.name or '')

    details = db.query(BOMDetail).filter(BOMDetail.bom_header_id == bh.id).all()
    for det in details:
        comp_prod = db.query(Product).filter(Product.id == det.component_id).first()
        if not comp_prod or not comp_prod.code:
            continue
        comp_code = comp_prod.code

        # Try exact full name first, then base name
        excel_qty = emap_exact.get((wip_full_lower, comp_code))
        if excel_qty is None:
            excel_qty = emap.get((wip_bname, comp_code))

        if excel_qty is None:
            not_found += 1
            continue

        db_qty = float(det.qty_needed or 0)
        if abs(excel_qty - db_qty) > 0.00001:
            det.qty_needed = excel_qty
            fixed += 1
        else:
            already_correct += 1

db.commit()
db.close()

print(f'Fixed:           {fixed}')
print(f'Already correct: {already_correct}')
print(f'Not found in Excel: {not_found}')
print('Done.')
