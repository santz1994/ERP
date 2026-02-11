"""Extract and import all materials from BOM files."""
import sys
sys.path.insert(0, 'erp-softtoys')

import pandas as pd
from pathlib import Path
from datetime import datetime

# Import from actual app
from app.core.models.products import Product, Category, ProductType, UOM
from app.core.database import SessionLocal

# Database connection from app
session = SessionLocal()

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
        
        # Get components from both possible column names
        components = None
        if 'BoM Lines/Component' in df.columns:
            components = df['BoM Lines/Component'].dropna()
        elif 'BoM Lines/Component/Name' in df.columns:
            components = df['BoM Lines/Component/Name'].dropna()
        
        if components is not None:
            for comp in components:
                comp_str = str(comp)
                # Extract code from [CODE] format
                if '[' in comp_str and ']' in comp_str:
                    code = comp_str.split('[')[1].split(']')[0]
                    if code not in materials:
                        materials[code] = comp_str
            
            print(f"   Found {len([c for c in components if '[' in str(c) and ']' in str(c)])} material entries")

print(f"\n✅ Total unique materials: {len(materials)}")

# Check which materials already exist
print(f"\n🔍 Checking database for existing materials...")
existing_codes = set()
existing_products = session.query(Product.code).all()
existing_codes = {p.code for p in existing_products}
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
    
    # Parse name from [CODE] NAME format
    if ']' in full_text:
        name = full_text.split(']')[1].strip()
    else:
        name = full_text.strip()
    
    # Remove duplicate code prefix if exists
    name = name.replace(f'[{code}]', '').strip()
    
    to_import.append({
        'code': code,
        'name': name[:255],  # Limit to 255 chars
        'category': get_category(code)
    })

print(f"\n📊 Import summary:")
print(f"   ✅ To import: {len(to_import)} new materials")
print(f"   ⏭️  Skipped: {len(skipped)} already exist")

if not to_import:
    print("\n✅ All materials already exist in database!")
    session.close()
    exit(0)

# Show preview
print(f"\n📋 Preview of materials to import (first 10):")
for item in to_import[:10]:
    print(f"   [{item['code']}] {item['name'][:60]}")
    print(f"      Category: {item['category']}")

# Get or create categories
print(f"\n🏷️  Setting up categories...")
category_map = {}  # name -> id
for item in to_import:
    cat_name = item['category']
    if cat_name not in category_map:
        # Check if exists
        cat = session.query(Category).filter(Category.name == cat_name).first()
        if not cat:
            cat = Category(name=cat_name)
            session.add(cat)
            session.flush()  # Get ID
        category_map[cat_name] = cat.id

session.commit()
print(f"   ✅ {len(category_map)} categories ready")

# Confirm import
print(f"\n⚠️  Ready to import {len(to_import)} materials as RAW_MATERIAL type")
response = input("   Continue? (yes/no): ").strip().lower()

if response != 'yes':
    print("❌ Import cancelled")
    session.close()
    exit(0)

# Import materials
print(f"\n🚀 Importing {len(to_import)} materials...")
imported = 0
errors = []

for item in to_import:
    try:
        product = Product(
            code=item['code'],
            name=item['name'],
            type=ProductType.RAW_MATERIAL,  # Use enum directly
            category_id=category_map[item['category']],
            uom=UOM.PCS,  # Use enum directly
            min_stock=0,
            is_active=True
        )
        session.add(product)
        imported += 1
        
        if imported % 50 == 0:
            print(f"   Imported {imported}/{len(to_import)}...")
    except Exception as e:
        errors.append(f"[{item['code']}] {str(e)}")

# Commit
try:
    session.commit()
    print(f"\n✅ Successfully imported {imported} materials!")
except Exception as e:
    session.rollback()
    print(f"\n❌ Error committing: {e}")
    errors.append(f"Commit error: {e}")

if errors:
    print(f"\n⚠️  Errors encountered ({len(errors)}):")
    for err in errors[:10]:
        print(f"   {err}")
    if len(errors) > 10:
        print(f"   ... and {len(errors) - 10} more")

# Verify
final_count = session.query(Product).filter(
    Product.type == ProductType.RAW_MATERIAL  # Use enum directly
).count()
print(f"\n📊 Final count:")
print(f"   RAW_MATERIAL products in database: {final_count}")

# Show category breakdown
print(f"\n📊 Materials by category:")
from sqlalchemy import func
categories = session.query(
    Category.name,
    func.count(Product.id).label('count')
).join(
    Product, Product.category_id == Category.id
).filter(
    Product.type == ProductType.RAW_MATERIAL  # Use enum directly
).group_by(Category.name).order_by(func.count(Product.id).desc()).all()

for cat_name, count in categories:
    print(f"   {cat_name}: {count}")

session.close()
print("\n" + "=" * 80)
print("✅ MATERIAL IMPORT COMPLETE")
print("=" * 80)
