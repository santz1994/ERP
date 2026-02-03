"""Check what Finished Good products exist in database from BOM import"""

from app.core.database import get_db
from app.core.models.products import Product
from app.core.models.bom import BOMHeader

db = next(get_db())

print("\n" + "="*80)
print("🔍 CHECKING FINISHED GOOD PRODUCTS")
print("="*80)

# Check 1: Products with [code] format (from Finishing Goods.xlsx)
print("\n1. Products with [code] format (finished goods):")
fg_products = db.query(Product).filter(
    Product.code.like('[%]%')
).limit(10).all()

if fg_products:
    for idx, p in enumerate(fg_products, 1):
        print(f"  {idx}. [{p.code}] {p.name}")
        print(f"     Type: {p.type}")
        print(f"     Category: {p.category.name if p.category else 'N/A'}")
else:
    print("  ❌ No products with [code] format found!")

# Check 2: Products from FINISH_GOOD or FG category
print("\n2. Products from FINISH_GOOD/FG category:")
fg_by_category = db.query(Product).join(Product.category).filter(
    Product.category.has(name='FINISH_GOOD')
).limit(10).all()

if fg_by_category:
    for idx, p in enumerate(fg_by_category, 1):
        print(f"  {idx}. {p.code} - {p.name}")
        print(f"     Type: {p.type}")
        
        # Check if has BOM
        bom = db.query(BOMHeader).filter_by(product_id=p.id).first()
        if bom:
            print(f"     ✅ Has BOM with {len(bom.details)} components")
        else:
            print(f"     ❌ No BOM found")
else:
    print("  ❌ No products in FINISH_GOOD category!")

# Check 3: All categories to see what we have
print("\n3. All product categories in database:")
from app.core.models.products import Category
categories = db.query(Category).all()
for cat in categories:
    count = db.query(Product).filter_by(category_id=cat.id).count()
    print(f"  - {cat.name}: {count} products")

# Check 4: Sample products from each WIP category
print("\n4. Sample WIP products (potential finished goods):")
wip_categories = ['WIP_PACKING', 'FINISH_GOOD']
for cat_name in wip_categories:
    print(f"\n  {cat_name}:")
    products = db.query(Product).join(Product.category).filter(
        Product.category.has(name=cat_name)
    ).limit(5).all()
    
    for p in products:
        print(f"    • {p.code}")
        # Check if this WIP has a BOM that uses it as component (i.e., it's output)
        bom_count = db.query(BOMHeader).filter_by(product_id=p.id).count()
        if bom_count > 0:
            print(f"      → Has BOM (can be finished good)")

print("\n" + "="*80)
print("✅ Check complete!")
print("="*80)

db.close()
