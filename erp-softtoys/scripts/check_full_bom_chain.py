"""Check what components are used in Cutting and Embroidery BOMs"""

from app.core.database import get_db
from app.core.models.products import Product
from app.core.models.bom import BOMHeader

db = next(get_db())

print("\n" + "="*80)
print("🔍 FULL BOM CHAIN FOR AFTONSPARV BEAR")
print("="*80)

stages = [
    ('WIP_CUTTING', 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_CUTTING'),
    ('WIP_EMBO', 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_EMBO'),
    ('WIP_SKIN', 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_SKIN'),
    ('WIP_BONEKA', 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_BONEKA'),
    ('WIP_PACKING', 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_PACKING'),
]

for stage_name, product_code in stages:
    print(f"\n{'='*80}")
    print(f"📦 {stage_name}: {product_code}")
    print('='*80)
    
    wip = db.query(Product).filter(Product.code == product_code).first()
    
    if not wip:
        print("  ❌ Product not found!")
        continue
    
    bom = db.query(BOMHeader).filter_by(product_id=wip.id, is_active=True).first()
    
    if not bom:
        print("  ❌ No BOM found!")
        continue
    
    print(f"  BOM ID: {bom.id}")
    print(f"  Total Components: {len(bom.details)}")
    print(f"\n  📋 Components:")
    
    for idx, detail in enumerate(bom.details, 1):
        component = detail.component
        print(f"\n  {idx}. {component.code}")
        print(f"     Qty per unit: {detail.qty_needed}")
        print(f"     Type: {component.type.value}")
        print(f"     Category: {component.category.name}")
        
        # Check if component has further BOM
        if component.type.value == 'WIP':
            sub_bom = db.query(BOMHeader).filter_by(product_id=component.id, is_active=True).first()
            if sub_bom:
                print(f"     🔄 Has BOM → Will explode further")
            else:
                print(f"     ⚠️  WIP but no BOM!")

print("\n" + "="*80)
print("✅ Analysis complete!")
print("="*80)

db.close()
