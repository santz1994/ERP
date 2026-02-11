"""Match BOM material codes with database products."""
import psycopg2
from pathlib import Path

# Database connection
conn = psycopg2.connect(
    dbname="erp_quty_karunia",
    user="postgres",
    password="password123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

print("🔍 MATCHING BOM MATERIAL CODES WITH DATABASE")
print("=" * 80)

# Read BOM codes from file
bom_codes = []
with open('bom_material_codes.txt', 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('[') and ']' in line:
            code = line.split('[')[1].split(']')[0]
            bom_codes.append(code)

print(f"📋 BOM has {len(bom_codes)} unique material codes")

# Get all product codes from database
cursor.execute("SELECT code, name, type FROM products")
db_products = cursor.fetchall()
db_codes = {p[0] for p in db_products}

print(f"💾 Database has {len(db_codes)} product codes")
print()

# Find matches
found = []
not_found = []

for code in sorted(set(bom_codes)):
    if code in db_codes:
        found.append(code)
    else:
        not_found.append(code)

print(f"✅ FOUND IN DATABASE: {len(found)}/{len(set(bom_codes))} ({len(found)/len(set(bom_codes))*100:.1f}%)")
if found:
    print("\nFirst 20 found codes:")
    for code in found[:20]:
        # Get product info
        cursor.execute("SELECT name, type FROM products WHERE code = %s", (code,))
        result = cursor.fetchone()
        if result:
            name, ptype = result
            print(f"   ✅ [{code}] {ptype}: {name[:60]}")
    if len(found) > 20:
        print(f"   ... and {len(found) - 20} more")

print(f"\n❌ NOT FOUND IN DATABASE: {len(not_found)}/{len(set(bom_codes))} ({len(not_found)/len(set(bom_codes))*100:.1f}%)")
if not_found:
    print("\nFirst 30 missing codes:")
    # Read full names from file
    code_names = {}
    with open('bom_material_codes.txt', 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('[') and ']' in line:
                code = line.split('[')[1].split(']')[0]
                name = line.split(']')[1].strip()
                code_names[code] = name
    
    for code in not_found[:30]:
        name = code_names.get(code, "")
        print(f"   ❌ [{code}] {name[:60]}")
    if len(not_found) > 30:
        print(f"   ... and {len(not_found) - 30} more")

# Analyze by prefix
print("\n" + "=" * 80)
print("📊 ANALYSIS BY CODE PREFIX")
print("=" * 80)

prefixes = {}
for code in sorted(set(bom_codes)):
    prefix = code[:3]
    if prefix not in prefixes:
        prefixes[prefix] = {'total': 0, 'found': 0, 'not_found': 0}
    prefixes[prefix]['total'] += 1
    if code in db_codes:
        prefixes[prefix]['found'] += 1
    else:
        prefixes[prefix]['not_found'] += 1

for prefix in sorted(prefixes.keys()):
    stats = prefixes[prefix]
    match_rate = (stats['found'] / stats['total'] * 100) if stats['total'] > 0 else 0
    status = "✅" if match_rate > 80 else "⚠️" if match_rate > 30 else "❌"
    print(f"{status} {prefix}xxx: {stats['found']}/{stats['total']} found ({match_rate:.1f}%)")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print(f"🎯 CONCLUSION: {len(found)}/{len(set(bom_codes))} materials exist ({len(found)/len(set(bom_codes))*100:.1f}%)")
print("=" * 80)
