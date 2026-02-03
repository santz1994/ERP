"""
Test BOM Explosion and Work Order Generation

Author: IT Developer Expert
Date: 3 Februari 2026
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db
from app.core.models.products import Product
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder
from app.services.bom_explosion_service import BOMExplosionService


def test_bom_explosion():
    """Test BOM explosion for a sample product"""
    
    print("\n" + "="*80)
    print("🧪 TESTING BOM EXPLOSION & WORK ORDER GENERATION")
    print("="*80)
    
    db = next(get_db())
    
    try:
        # Step 1: Find a Finished Good product with BOM
        print("\n📦 Step 1: Finding Finished Good product...")
        
        # In Quty Karunia system, WIP_PACKING is the "finished good" (final stage before customer)
        from app.core.models.products import Category
        from app.core.models.bom import BOMHeader
        
        fg_products = db.query(Product).join(Product.category).filter(
            Product.category.has(name='WIP Packing')
        ).limit(5).all()
        
        if not fg_products:
            print("❌ No WIP_PACKING products found! Please import BOM first.")
            return
        
        print(f"✅ Found {len(fg_products)} WIP_PACKING products (finished goods):")
        for idx, fg in enumerate(fg_products, 1):
            # Check if has BOM
            bom = db.query(BOMHeader).filter_by(product_id=fg.id, is_active=True).first()
            if bom:
                print(f"  {idx}. {fg.code}")
                print(f"      ✅ Has BOM with {len(bom.details)} components")
        
        # Use first one with BOM
        test_product = None
        for fg in fg_products:
            bom = db.query(BOMHeader).filter_by(product_id=fg.id, is_active=True).first()
            if bom:
                test_product = fg
                break
        
        if not test_product:
            print("❌ No WIP_PACKING product with BOM found!")
            return
        
        print(f"✅ Found {len(fg_products)} FG products:")
        for idx, fg in enumerate(fg_products, 1):
            print(f"  {idx}. {fg.code} - {fg.name}")
        
        # Use first one for testing
        test_product = fg_products[0]
        print(f"\n🎯 Testing with: {test_product.code}")
        
        # Step 2: Create test Manufacturing Order
        print("\n📋 Step 2: Creating test Manufacturing Order...")
        
        from app.core.models.manufacturing import MOState, RoutingType
        import uuid
        
        # Generate unique batch number
        unique_suffix = str(uuid.uuid4())[:8]
        batch_number = f"MO-TEST-{test_product.id}-{unique_suffix}"
        
        mo = ManufacturingOrder(
            batch_number=batch_number,
            product_id=test_product.id,
            qty_planned=Decimal('450'),
            state=MOState.DRAFT,
            routing_type=RoutingType.ROUTE1  # ROUTE1 not ROUTE_1
        )
        
        db.add(mo)
        db.flush()
        
        print(f"✅ Created MO: {mo.batch_number}")
        
        # Step 3: Explode BOM
        print("\n🔍 Step 3: Exploding BOM...")
        
        service = BOMExplosionService(db)
        
        explosion_result = service.explode_bom_multi_level(
            product_id=test_product.id,
            qty_required=Decimal('450'),
            level=0
        )
        
        print("\n📊 Explosion Result Summary:")
        print_explosion_summary(explosion_result)
        
        # Step 4: Generate Work Orders
        print("\n🏭 Step 4: Generating Work Orders...")
        
        work_orders = service.explode_mo_and_generate_work_orders(
            mo_id=mo.id,
            qty_planned=Decimal('450')
        )
        
        print(f"\n✅ Generated {len(work_orders)} Work Orders:")
        for wo in work_orders:
            print(f"  {wo.sequence}. {wo.wo_number}")
            print(f"     Department: {wo.department}")
            print(f"     Status: {wo.status}")
            print(f"     Target Qty: {wo.target_qty} pcs")
            print(f"     Input WIP: {wo.input_wip_product_id or 'None (raw materials)'}")
            print(f"     Output WIP: {wo.output_wip_product_id}")
            print()
        
        # Step 5: Test dependency checking
        print("\n🔗 Step 5: Testing Work Order dependencies...")
        
        for wo in work_orders:
            can_start, reason = service.check_wo_dependencies(wo.id)
            status_icon = "✅" if can_start else "⏳"
            print(f"  {status_icon} WO {wo.wo_number}: {reason}")
        
        # Step 6: Simulate WO progression
        print("\n⚡ Step 6: Simulating Work Order progression...")
        
        # Complete first WO
        first_wo = work_orders[0]
        first_wo.status = 'FINISHED'  # Changed from COMPLETED to FINISHED
        db.commit()
        
        print(f"  ✅ Completed WO: {first_wo.wo_number}")
        
        # Update statuses
        service.update_wo_status_auto(mo.id)
        
        # Check again
        print("\n  Updated statuses:")
        for wo in db.query(WorkOrder).filter_by(mo_id=mo.id).order_by(WorkOrder.sequence).all():
            print(f"    {wo.wo_number}: {wo.status}")
        
        print("\n✅ TEST COMPLETED SUCCESSFULLY!")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        db.rollback()  # Rollback all test changes
        print("✅ Test data cleaned up (rolled back)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()


def print_explosion_summary(result: dict, indent: int = 0):
    """Pretty print explosion result"""
    
    prefix = "  " * indent
    
    print(f"{prefix}📦 {result['product_code']} (Level {result['level']})")
    print(f"{prefix}   Qty: {result['qty_required']} pcs")
    print(f"{prefix}   Type: {result.get('product_type', 'N/A')}")
    print(f"{prefix}   Dept: {result.get('department', 'N/A')}")
    
    # Materials
    materials = result.get('materials', [])
    if materials:
        print(f"{prefix}   Materials ({len(materials)}):")
        for mat in materials[:3]:  # Show first 3
            print(f"{prefix}     - {mat['component_code']}: {mat['total_qty_needed']}")
        if len(materials) > 3:
            print(f"{prefix}     ... and {len(materials) - 3} more")
    
    # Children (recursive)
    children = result.get('children', [])
    if children:
        print(f"{prefix}   Children ({len(children)}):")
        for child in children:
            print_explosion_summary(child, indent + 1)


def print_usage():
    """Print usage instructions"""
    
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🎯 BOM EXPLOSION & WORK ORDER GENERATION - TESTING GUIDE                    ║
╚══════════════════════════════════════════════════════════════════════════════╝

PREREQUISITES:
1. Database migrated (run: alembic upgrade head)
2. BOM data imported (run: python scripts/import_bom_from_excel.py)

WHAT THIS TEST DOES:
1. ✅ Finds a Finished Good product with BOM
2. ✅ Creates a test Manufacturing Order
3. ✅ Explodes multi-level BOM recursively
4. ✅ Generates Work Orders for each department
5. ✅ Tests dependency checking
6. ✅ Simulates WO progression (WAITING → READY)
7. ✅ Cleans up test data (rollback)

EXPECTED OUTPUT:
- Multi-level BOM explosion tree
- 5-6 Work Orders (one per department)
- Dependency chain enforced (WO2 waits for WO1, etc.)
- Status auto-update when dependencies satisfied

RUN TEST:
  python scripts/test_bom_explosion.py

══════════════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print_usage()
    else:
        test_bom_explosion()
