"""Extract and import all materials from BOM files using raw SQL."""
import pandas as pd
from pathlib import Path
import psycopg2

# Database connection
conn = psycopg2.connect(
    dbname="erp_quty_karunia",
    user="postgres",
    password="password123",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

print("🔍 EXTRACTING MATERIALS FROM BOM FILES")
print("=" * 80)

bom_path = Path("docs/Masterdata/BOM Production")
bom_files = [
    "Cutting.xlsx",
    "Embo.xlsx",
    "Sewing.xlsx",
    "Finishing.xlsx",
    "Packing.xlsx",
    "Finishing Goods.xlsx"
]

# Extract all unique materials
materials = {}  # {code: full_text}

for filename in bom_files:
    file_path = bom_path / filename
    if file_path.exists():
        print(f"\n📋 Processing {filename}...")
        df = pd.read_excel(file_path)
        
        # Get components
        components = None
        if 'BoM Lines/Component' in df.columns:
            components = df['BoM Lines/Component'].dropna()
        elif 'BoM Lines/Component/Name' in df.columns:
            components = df['BoM Lines/Component/Name'].dropna()
        
        if components is not None:
            for comp in components:
                comp_str = str(comp)
                if '[' in comp_str and ']' in comp_str:
                    code = comp_str.split('[')[1].split(']')[0]
                    if code not in materials:
                        materials[code] = comp_str
            
            print(f"   Found {len([c for c in components if '[' in str(c) and ']' in str(c)])} material entries")

print(f"\n✅ Total unique materials: {len(materials)}")

# Check existing
cursor.execute("SELECT code FROM products")
existing_codes = {row[0] for row in cursor.fetchall()}
print(f"   Database has {len(existing_codes)} existing product codes")

# Determine category from code prefix
def get_category(code):
    prefix = code[:3]
    category_map = {
        'ACB': 'Packaging - Carton',
        'ACE': 'Packaging - Cello',
        'AEL': 'Elastic',
        'ALB': 'Label - Barcode',
        'ALL': 'Label - Regular',
        'ALS': 'Label - Sticker',
        'APE': 'Packaging - PE',
        'APP': 'Packaging - PP',
        'AST': 'Accessories - Stone',
        'ASW': 'Accessories - Swing Tag',
        'ATR': 'Thread',
        'AUL': 'Label - ULL Sticker',
        'AVC': 'Accessories - Velcro',
        'AWT': 'Accessories - Webbing Tape',
        'DB1': 'Accessories - Button',
        'DB5': 'Accessories - Button',
        'DB6': 'Accessories - Button',
        'DB7': 'Accessories - Button',
        'DBR': 'Accessories - Buckle',
        'DEL': 'Elastic',
        'IBC': 'Fabric - Batting Cotton',
        'ICS': 'Fabric - Coral Sherpa',
        'ICV': 'Fabric - Canvas',
        'IEF': 'Fabric - Embo Flannel',
        'IFT': 'Fabric - Flannel Terry',
        'IGR': 'Fabric - Grey Fabric',
        'IJB': 'Fabric - Boa/Jersey',
        'IKH': 'Fabric - Kohair',
        'IKP': 'Stuffing - Fiber/Polyester',
        'IKV': 'Fabric - Knit Velour',
        'IMT': 'Fabric - Minky Terry',
        'INP': 'Fabric - Napped',
        'INW': 'Fabric - Non Woven',
        'INY': 'Fabric - Nylex',
        'IPD': 'Fabric - Printed',
        'IPE': 'Fabric - Polyester',
        'IPL': 'Fabric - Pluche',
        'IPM': 'Fabric - Plumette',
        'IPP': 'Fabric - Polyester Print',
        'IPR': 'Fabric - Polyester',
        'IST': 'Fabric - Stripe Terry',
        'ISW': 'Fabric - Sherpa Weft',
        'IVB': 'Fabric - Velboa',
        'IVT': 'Fabric - Velvet',
        'IWD': 'Fabric - Wudhu',
        'TP0': 'Accessories - Zipper',
        'TP1': 'Accessories - Zipper',
        'TP5': 'Accessories - Zipper',
        'TP6': 'Accessories - Zipper',
        'TP7': 'Accessories - Zipper',
        'TP9': 'Accessories - Zipper',
        'TPR': 'Accessories - Zipper',
    }
    return category_map.get(prefix, 'Other Materials')

# Prepare materials to import
to_import = []
skipped = []

for code, full_text in materials.items():
    if code in existing_codes:
        skipped.append(code)
        continue
    
    # Parse name
    if ']' in full_text:
        name = full_text.split(']')[1].strip()
    else:
        name = full_text.strip()
    
    name = name.replace(f'[{code}]', '').strip()
    
    to_import.append({
        'code': code,
        'name': name[:255],
        'category': get_category(code)
    })

print(f"\n📊 Import summary:")
print(f"   ✅ To import: {len(to_import)} new materials")
print(f"   ⏭️  Skipped: {len(skipped)} already exist")

if not to_import:
    print("\n✅ All materials already exist in database!")
    cursor.close()
    conn.close()
    exit(0)

# Show preview
print(f"\n📋 Preview of materials to import (first 10):")
for item in to_import[:10]:
    print(f"   [{item['code']}] {item['name'][:60]}")
    print(f"      Category: {item['category']}")

# Get or create categories
print(f"\n🏷️  Setting up categories...")
category_map = {}  # name -> id
unique_categories = set(item['category'] for item in to_import)

for cat_name in unique_categories:
    cursor.execute("SELECT id FROM categories WHERE name = %s", (cat_name,))
    result = cursor.fetchone()
    if result:
        category_map[cat_name] = result[0]
    else:
        cursor.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id", (cat_name,))
        category_map[cat_name] = cursor.fetchone()[0]

conn.commit()
print(f"   ✅ {len(category_map)} categories ready")

# Confirm
print(f"\n⚠️  Ready to import {len(to_import)} materials as RAW_MATERIAL type")
response = input("   Continue? (yes/no): ").strip().lower()

if response != 'yes':
    print("❌ Import cancelled")
    cursor.close()
    conn.close()
    exit(0)

# Import materials
print(f"\n🚀 Importing {len(to_import)} materials...")
imported = 0
errors = []

for item in to_import:
    try:
        cursor.execute("""
            INSERT INTO products (code, name, type, category_id, uom, min_stock, is_active)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            item['code'],
            item['name'],
            'RAW_MATERIAL',  # Correct enum value
            category_map[item['category']],
            'PCS',  # Correct enum value
            0,  # min_stock
            True  # is_active
        ))
        imported += 1
        
        if imported % 50 == 0:
            print(f"   Imported {imported}/{len(to_import)}...")
    except Exception as e:
        errors.append(f"[{item['code']}] {str(e)}")

# Commit
try:
    conn.commit()
    print(f"\n✅ Successfully imported {imported} materials!")
except Exception as e:
    conn.rollback()
    print(f"\n❌ Error committing: {e}")
    errors.append(f"Commit error: {e}")

if errors:
    print(f"\n⚠️  Errors encountered ({len(errors)}):")
    for err in errors[:10]:
        print(f"   {err}")
    if len(errors) > 10:
        print(f"   ... and {len(errors) - 10} more")

# Verify
cursor.execute("SELECT COUNT(*) FROM products WHERE type = 'RAW_MATERIAL'")
final_count = cursor.fetchone()[0]
print(f"\n📊 Final count:")
print(f"   RAW_MATERIAL products in database: {final_count}")

# Category breakdown
cursor.execute("""
    SELECT c.name, COUNT(p.id)
    FROM categories c
    JOIN products p ON p.category_id = c.id
    WHERE p.type = 'RAW_MATERIAL'
    GROUP BY c.name
    ORDER BY COUNT(p.id) DESC
    LIMIT 20
""")
categories = cursor.fetchall()

print(f"\n📊 Top 20 material categories:")
for cat_name, count in categories:
    print(f"   {cat_name}: {count}")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ MATERIAL IMPORT COMPLETE")
print("=" * 80)
