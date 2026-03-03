"""Apply correct UOM to all products based on Excel BOM files."""
import sys, re, openpyxl, os
sys.path.insert(0, '.')
from sqlalchemy import text
from app.core.database import SessionLocal, engine

# Map Excel UOM strings -> PG enum label (which are the Python enum .name uppercase)
def normalize_uom(uom):
    u = str(uom).strip().upper()
    if u in ('PCE', 'PCS'):        return 'PCS'
    if u == 'YARD':                return 'YARD'
    if u in ('CM', 'CENTIMETER'):  return 'CM'
    if u in ('GRAM', 'GR'):        return 'GRAM'
    if u in ('METER', 'MTR'):      return 'METER'
    if u in ('KGS', 'KG'):         return 'KG'
    if u.startswith('CTN'):        return 'PCS'
    if 'CONE' in u:                return 'PCS'
    return 'PCS'

BASE = r'D:\Project\ERP2026'
files = {
    'Cutting':   BASE + r'\docs\Masterdata\BOM Production\Cutting.xlsx',
    'Embo':      BASE + r'\docs\Masterdata\BOM Production\Embo.xlsx',
    'FG':        BASE + r'\docs\Masterdata\BOM Production\Finishing Goods.xlsx',
    'Finishing': BASE + r'\docs\Masterdata\BOM Production\Finishing.xlsx',
    'Packing':   BASE + r'\docs\Masterdata\BOM Production\Packing.xlsx',
    'Sewing':    BASE + r'\docs\Masterdata\BOM Production\Sewing.xlsx',
}

code_uom_map = {}
for fname, path in files.items():
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    comp_col = uom_col = None
    for i, h in enumerate(header):
        if h:
            hs = str(h).strip()
            if hs == 'BoM Lines/Component' and comp_col is None:
                comp_col = i
            if 'Product Un' in hs:
                uom_col = i
    for row in rows[1:]:
        comp = row[comp_col] if comp_col is not None else None
        uom  = row[uom_col]  if uom_col is not None else None
        if comp and uom:
            m = re.match(r'\[([^\]]+)\]', str(comp))
            if m:
                code = m.group(1)
                norm = normalize_uom(uom)
                if code not in code_uom_map or code_uom_map[code] == 'PCS':
                    code_uom_map[code] = norm

non_pcs = {k: v for k, v in code_uom_map.items() if v != 'PCS'}
print(f'Products to update: {len(non_pcs)}')
from collections import Counter
print('UOM distribution:', dict(Counter(non_pcs.values())))

# Step 1: Add GRAM to PG enum (safe - only adds if not exists)
with engine.connect() as conn:
    existing = [r[0] for r in conn.execute(text(
        "SELECT enumlabel FROM pg_enum e JOIN pg_type t ON e.enumtypid=t.oid WHERE t.typname='uom'"
    )).fetchall()]
    if 'GRAM' not in existing:
        conn.execute(text("ALTER TYPE uom ADD VALUE 'GRAM'"))
        conn.commit()
        print('Added GRAM to PG enum')
    else:
        print('GRAM already in PG enum')

# Step 2: Bulk update products
db = SessionLocal()
updated = 0
skipped = 0
for code, target_uom in non_pcs.items():
    result = db.execute(text(
        "UPDATE products SET uom = :uom WHERE code = :code AND uom != :uom"
    ), {'uom': target_uom, 'code': code}).rowcount
    if result:
        updated += 1
    else:
        skipped += 1

db.commit()
print(f'Updated: {updated}, Skipped (already correct): {skipped}')
db.close()

print('\nDone! Verifying...')
with engine.connect() as conn:
    vals = conn.execute(text(
        "SELECT uom, COUNT(*) as cnt FROM products GROUP BY uom ORDER BY cnt DESC"
    )).fetchall()
    for v in vals:
        print(f'  {v.uom}: {v.cnt}')
