"""Check complete BOM hierarchy for AFTONSPARV bear"""

from app.core.database import get_db
from app.core.models.products import Product
from app.core.models.bom import BOMHeader, BOMDetail

db = next(get_db())

print("\n" + "="*80)
print("🔍 CHECKING COMPLETE BOM HIERARCHY")
print("="*80)

# Get WIP_SKIN product (should have components from cutting/embo)
wip_skin = db.query(Product).filter(
    Product.code == 'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_SKIN'
).first()

if wip_skin:
    print(f"\n✅ Found: {wip_skin.code}")
    
    # Get its BOM
    bom = db.query(BOMHeader).filter_by(product_id=wip_skin.id, is_active=True).first()
    if bom:
        print(f"   BOM ID: {bom.id}")
        print(f"   Components: {len(bom.details)}")
        print(f"\n   📋 BOM Details:")
        
        for detail in bom.details:
            component = detail.component
            print(f"      - {component.code}")
            print(f"        Qty: {detail.qty_needed}")
            print(f"        Type: {component.type}")
            print(f"        Category: {component.category.name}")
            
            # If it's WIP, check its BOM recursively
            if component.type.value == 'WIP' and '_WIP_' in component.code:
                sub_bom = db.query(BOMHeader).filter_by(product_id=component.id, is_active=True).first()
                if sub_bom:
                    print(f"        → Has sub-BOM with {len(sub_bom.details)} components")
                    for sub_detail in sub_bom.details[:3]:  # Show first 3
                        print(f"           • {sub_detail.component.code}")

# Check all WIP stages for this bear
print("\n" + "="*80)
print("📦 ALL WIP STAGES FOR AFTONSPARV BEAR")
print("="*80)

wip_patterns = [
    'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_CUTTING',
    'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_EMBO',
    'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_SKIN',
    'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_BONEKA',
    'AFTONSPARV soft toy w astronaut suit 28 bear_WIP_PACKING'
]

for pattern in wip_patterns:
    wip = db.query(Product).filter(Product.code.like(f'{pattern}%')).first()
    if wip:
        bom = db.query(BOMHeader).filter_by(product_id=wip.id, is_active=True).first()
        if bom:
            print(f"\n✅ {wip.code}")
            print(f"   BOM: {len(bom.details)} components")
        else:
            print(f"\n⚠️  {wip.code} - NO BOM!")
    else:
        print(f"\n❌ {pattern} - NOT FOUND!")

print("\n" + "="*80)

db.close()
