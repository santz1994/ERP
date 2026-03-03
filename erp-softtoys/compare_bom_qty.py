"""Compare Excel BOM quantities vs DB quantities - using base_name matching (same as fix_v2)."""
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
    n = (name or '').strip().lower()
    idx = n.find('_wip_')
    return n[:idx] if idx >= 0 else n

db = SessionLocal()

# Build per-revision maps: (base_wip_name, comp_code) -> qty  (exact+base)
excel_maps_exact = {}  # revision -> {(full_name_lower, comp_code): qty}
excel_maps_base  = {}  # revision -> {(base_name, comp_code): qty}

for revision, path in REVISION_TO_FILE.items():
    em_exact = {}
    em_base  = {}
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    current = None
    for row in list(ws.iter_rows(values_only=True))[1:]:
        if row[0]:
            current = str(row[0]).strip()
        comp = row[10]
        qty  = row[12]
        if comp and qty is not None and current:
            m = re.match(r'\[([^\]]+)\]', str(comp))
            if m:
                cc = m.group(1)
                em_exact.setdefault((current.strip().lower(), cc), float(qty))
                em_base.setdefault((base_name(current), cc), float(qty))
    excel_maps_exact[revision] = em_exact
    excel_maps_base[revision]  = em_base

mismatches = []
matches = 0
total = 0

bom_headers = db.query(BOMHeader).filter(BOMHeader.revision.in_(list(REVISION_TO_FILE.keys()))).all()

for bh in bom_headers:
    revision = bh.revision
    wip = db.query(Product).filter(Product.id == bh.product_id).first()
    if not wip:
        continue

    wip_full = (wip.name or '').strip().lower()
    wip_base = base_name(wip.name or '')
    em_e = excel_maps_exact.get(revision, {})
    em_b = excel_maps_base.get(revision, {})

    for det in db.query(BOMDetail).filter(BOMDetail.bom_header_id == bh.id).all():
        comp = db.query(Product).filter(Product.id == det.component_id).first()
        if not comp or not comp.code:
            continue
        cc = comp.code

        excel_qty = em_e.get((wip_full, cc))
        if excel_qty is None:
            excel_qty = em_b.get((wip_base, cc))
        if excel_qty is None:
            continue

        total += 1
        db_qty = float(det.qty_needed or 0)
        if abs(excel_qty - db_qty) > 0.00001:
            mismatches.append({
                'wip': (wip.code or wip.name or '')[-35:],
                'comp_code': cc,
                'db_qty': db_qty,
                'excel_qty': excel_qty,
                'det_id': det.id,
            })
        else:
            matches += 1

print(f'Total compared: {total} | Matches: {matches} | Mismatches: {len(mismatches)}')
print()
if mismatches:
    print(f'{"WIP piece":<35}  {"Code":<22}  {"DB_qty":>8}  {"Excel_qty":>10}')
    for m in sorted(mismatches, key=lambda x: x["wip"])[:50]:
        print(f'{m["wip"]:35}  {m["comp_code"]:22}  {m["db_qty"]:8.4f}  {m["excel_qty"]:10.4f}')

db.close()
