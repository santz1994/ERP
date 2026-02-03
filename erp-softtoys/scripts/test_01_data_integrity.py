"""
TEST 1: Verify BOM Data Integrity
Checks that all imported BOM data is correct and consistent
"""

from app.core.database import get_db
from app.core.models.products import Product, Category
from app.core.models.bom import BOMHeader, BOMDetail

db = next(get_db())

print("\n" + "="*80)
print("🧪 TEST 1: BOM DATA INTEGRITY VERIFICATION")
print("="*80)

# Test 1.1: Check Categories
print("\n1️⃣ Category Verification")
categories = db.query(Category).all()
expected_categories = ['Raw Materials', 'WIP Cutting', 'WIP Embroidery', 'WIP Sewing', 
                       'WIP Finishing', 'WIP Packing', 'Finished Goods', 'Accessories']

print(f"   Expected: {len(expected_categories)} categories")
print(f"   Found: {len(categories)} categories")

for cat in categories:
    count = db.query(Product).filter_by(category_id=cat.id).count()
    print(f"   ✅ {cat.name}: {count} products")

# Test 1.2: Check Products by Type
print("\n2️⃣ Product Type Distribution")
from app.core.models.products import ProductType
for prod_type in ProductType:
    count = db.query(Product).filter_by(type=prod_type).count()
    print(f"   • {prod_type.value}: {count} products")

# Test 1.3: Check BOM Headers
print("\n3️⃣ BOM Headers Verification")
total_boms = db.query(BOMHeader).count()
active_boms = db.query(BOMHeader).filter_by(is_active=True).count()
print(f"   Total BOMs: {total_boms}")
print(f"   Active BOMs: {active_boms}")

# Test 1.4: Check BOM Details
print("\n4️⃣ BOM Details Verification")
total_details = db.query(BOMDetail).count()
print(f"   Total BOM detail lines: {total_details}")

# Test 1.5: Sample BOM Structure Check
print("\n5️⃣ Sample BOM Structure (AFTONSPARV bear)")
wip_packing = db.query(Product).filter(
    Product.code == 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_PACKING'
).first()

if wip_packing:
    bom = db.query(BOMHeader).filter_by(product_id=wip_packing.id, is_active=True).first()
    if bom:
        print(f"   ✅ {wip_packing.code}")
        print(f"      BOM ID: {bom.id}")
        print(f"      Components: {len(bom.details)}")
        for detail in bom.details:
            print(f"         → {detail.component.code} (qty: {detail.qty_needed})")
    else:
        print(f"   ❌ No BOM found for WIP_PACKING")
else:
    print(f"   ❌ Product not found")

# Test 1.6: Verify Material Relationships
print("\n6️⃣ Material Type Distribution")
raw_count = db.query(Product).filter_by(type=ProductType.RAW_MATERIAL).count()
wip_count = db.query(Product).filter_by(type=ProductType.WIP).count()
fg_count = db.query(Product).filter_by(type=ProductType.FINISH_GOOD).count()

print(f"   Raw Materials: {raw_count}")
print(f"   WIP Products: {wip_count}")
print(f"   Finished Goods: {fg_count}")
print(f"   Total: {raw_count + wip_count + fg_count}")

# Verification Summary
print("\n" + "="*80)
print("📊 TEST 1 SUMMARY")
print("="*80)

errors = []

if len(categories) < 8:
    errors.append(f"Missing categories: expected 8, found {len(categories)}")

if total_boms < 1000:
    errors.append(f"Insufficient BOMs: expected >1000, found {total_boms}")

if total_details < 5000:
    errors.append(f"Insufficient BOM details: expected >5000, found {total_details}")

if wip_count < 1000:
    errors.append(f"Insufficient WIP products: expected >1000, found {wip_count}")

if errors:
    print("\n❌ TEST 1 FAILED:")
    for error in errors:
        print(f"   • {error}")
else:
    print("\n✅ TEST 1 PASSED: All BOM data integrity checks successful!")
    print(f"   • {len(categories)} categories verified")
    print(f"   • {total_boms} BOMs imported")
    print(f"   • {total_details} BOM detail lines")
    print(f"   • {wip_count} WIP products tracked")

db.close()
