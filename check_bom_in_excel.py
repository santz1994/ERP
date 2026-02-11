"""Check if BOM material codes exist in DATABASE MATERIAL ALL.xlsx"""
import pandas as pd

print("🔍 CHECKING BOM CODES IN DATABASE MATERIAL ALL.xlsx")
print("=" * 80)

# Read material database
material_db = pd.read_excel("docs/Masterdata/Material/DATABASE MATERIAL ALL.xlsx")
print(f"📋 Material database has {len(material_db)} rows")
print(f"   Columns: {list(material_db.columns)}")

# Get material codes from column (check which column has the code)
print("\n📊 Sample material data:")
print(material_db.head())

# Check if there's a code column
code_column = None
for col in ['Code', 'Material Code', 'Base Material', 'code', 'CODE']:
    if col in material_db.columns:
        code_column = col
        break

if code_column:
    print(f"\n✅ Found code column: '{code_column}'")
    db_codes = set(material_db[code_column].dropna().astype(str))
    print(f"   Unique codes: {len(db_codes)}")
    print(f"   Sample codes: {list(db_codes)[:10]}")
else:
    print("\n⚠️ No obvious code column found. Checking 'Base Material' column:")
    if 'Base Material' in material_db.columns:
        base_materials = material_db['Base Material'].dropna().unique()
        print(f"   Unique base materials: {len(base_materials)}")
        print(f"   Sample: {list(base_materials)[:15]}")
        db_codes = set(base_materials)

# Read BOM codes
bom_codes = []
with open('bom_material_codes.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('[') and ']' in line:
            code = line.split('[')[1].split(']')[0]
            bom_codes.append(code)

bom_codes = set(bom_codes)
print(f"\n📋 BOM has {len(bom_codes)} unique material codes")

# Match
found = []
not_found = []

for code in sorted(bom_codes):
    if code in db_codes:
        found.append(code)
    else:
        not_found.append(code)

print(f"\n✅ FOUND: {len(found)}/{len(bom_codes)} ({len(found)/len(bom_codes)*100:.1f}%)")
if found:
    print("\nFirst 30 found codes:")
    for code in found[:30]:
        # Get material info
        if code_column:
            row = material_db[material_db[code_column] == code]
        else:
            row = material_db[material_db['Base Material'] == code]
        
        if not row.empty:
            name = row.iloc[0].get('MATERIAL NAME', row.iloc[0].get('Material Name', ''))
            print(f"   ✅ [{code}] {str(name)[:60]}")
    if len(found) > 30:
        print(f"   ... and {len(found) - 30} more")

print(f"\n❌ NOT FOUND: {len(not_found)}/{len(bom_codes)} ({len(not_found)/len(bom_codes)*100:.1f}%)")
if not_found:
    print("\nFirst 30 missing codes:")
    for code in list(not_found)[:30]:
        print(f"   ❌ [{code}]")
    if len(not_found) > 30:
        print(f"   ... and {len(not_found) - 30} more")

print("\n" + "=" * 80)
print(f"🎯 CONCLUSION: {len(found)}/{len(bom_codes)} materials exist in Excel ({len(found)/len(bom_codes)*100:.1f}%)")
print("=" * 80)
