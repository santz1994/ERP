"""Fix BOM qty_needed in DB to match exact Excel values for all mismatches."""
import re, openpyxl
from app.core.database import SessionLocal
from app.core.models import Product
from app.core.models.bom import BOMHeader, BOMDetail

BASE = r'D:\Project\ERP2026'

files = {
    'Cutting':   BASE + r'\docs\Masterdata\BOM Production\Cutting.xlsx',
    'Embo':      BASE + r'\docs\Masterdata\BOM Production\Embo.xlsx',
    'Finishing': BASE + r'\docs\Masterdata\BOM Production\Finishing.xlsx',
    'Packing':   BASE + r'\docs\Masterdata\BOM Production\Packing.xlsx',
    'Sewing':    BASE + r'\docs\Masterdata\BOM Production\Sewing.xlsx',
}

REVISION_MAP = {
    'Cutting':   'CUT-1.0',
    'Embo':      'EMB-1.0',
    'Finishing': 'FIN-1.0',
    'Packing':   'PCK-1.0',
    'Sewing':    'SEW-1.0',
}

db = SessionLocal()

# Build lookup: (wip_product_name_lower[:60], comp_code) -> excel_qty
excel_map = {}

for fname, path in files.items():
    revision = REVISION_MAP[fname]
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
                key = (revision, current_product.lower()[:60], comp_code)
                # If same key appears multiple times (shouldn't for per-piece), keep first
                if key not in excel_map:
                    excel_map[key] = float(qty)

print(f'Excel entries loaded: {len(excel_map)}')

# Find and fix mismatches
fixed = 0
skipped = 0
not_found = 0

bom_headers = db.query(BOMHeader).all()

for bh in bom_headers:
    wip_prod = db.query(Product).filter(Product.id == bh.product_id).first()
    if not wip_prod:
        continue

    # Build search keys from both name and code
    wip_name_lower = (wip_prod.name or '').lower()[:60]
    wip_code_lower = (wip_prod.code or '').lower()[:60]
    revision = bh.revision

    details = db.query(BOMDetail).filter(BOMDetail.bom_header_id == bh.id).all()
    for det in details:
        comp_prod = db.query(Product).filter(Product.id == det.component_id).first()
        if not comp_prod or not comp_prod.code:
            continue
        comp_code = comp_prod.code

        # Try matching by name first, then by code
        excel_qty = None
        key_name = (revision, wip_name_lower, comp_code)
        key_code = (revision, wip_code_lower, comp_code)

        if key_name in excel_map:
            excel_qty = excel_map[key_name]
        elif key_code in excel_map:
            excel_qty = excel_map[key_code]
        else:
            # Try partial match: find any key where revision matches, comp_code matches,
            # and wip key is substring of wip_name_lower
            for (rev, wp, cc), val in excel_map.items():
                if rev == revision and cc == comp_code and (wp in wip_name_lower or wp in wip_code_lower or wip_name_lower in wp or wip_code_lower in wp):
                    excel_qty = val
                    break

        if excel_qty is None:
            not_found += 1
            continue

        db_qty = float(det.qty_needed or 0)
        if abs(excel_qty - db_qty) > 0.00001:
            det.qty_needed = excel_qty
            fixed += 1
        else:
            skipped += 1

db.commit()
db.close()

print(f'Fixed:     {fixed}')
print(f'Matched (no change): {skipped}')
print(f'Not found in Excel:  {not_found}')
print('Done.')
