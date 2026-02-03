"""
Test Work Orders API Endpoints
End-to-end testing for WO generation and management

Author: IT Developer Expert
Date: 3 Februari 2026
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, MOState, Department, RoutingType
from app.core.models.products import Product, Category
from app.services.bom_explosion_service import BOMExplosionService
from decimal import Decimal
import uuid


def test_work_order_api():
    """Test Work Order API functionality"""
    
    print("=" * 80)
    print("🧪 TESTING WORK ORDER API")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # Step 1: Find a finished good with BOM
        print("\n📦 Step 1: Finding Finished Good product with BOM...")
        
        # Get WIP_PACKING category (these are our "finished goods")
        packing_category = db.query(Category).filter(
            Category.name == 'WIP Packing'
        ).first()
        
        if not packing_category:
            print("❌ No WIP_PACKING category found")
            return
        
        # Get products in this category
        fg_products = db.query(Product).filter(
            Product.category_id == packing_category.id
        ).limit(5).all()
        
        if not fg_products:
            print("❌ No WIP_PACKING products found")
            return
        
        print(f"✅ Found {len(fg_products)} WIP_PACKING products:")
        for i, prod in enumerate(fg_products, 1):
            print(f"  {i}. {prod.name}")
        
        # Use first product
        test_product = fg_products[0]
        print(f"\n🎯 Testing with: {test_product.name}")
        
        # Step 2: Create Manufacturing Order
        print("\n📋 Step 2: Creating test Manufacturing Order...")
        
        unique_suffix = str(uuid.uuid4())[:8]
        mo = ManufacturingOrder(
            batch_number=f"MO-TEST-API-{test_product.id}-{unique_suffix}",
            product_id=test_product.id,
            qty_planned=Decimal('450'),
            routing_type=RoutingType.ROUTE1
        )
        db.add(mo)
        db.flush()
        
        print(f"✅ Created MO: {mo.batch_number} (ID: {mo.id})")
        
        # Step 3: Test BOM Explosion Service
        print("\n🔍 Step 3: Testing BOM Explosion Service...")
        
        service = BOMExplosionService(db)
        
        # Explode BOM
        explosion = service.explode_bom_multi_level(
            product_id=test_product.id,
            qty_required=Decimal('450'),
            level=0
        )
        
        if explosion:
            print(f"✅ BOM explosion successful:")
            print(f"   Product: {explosion.get('product_name')}")
            print(f"   Quantity: {explosion.get('quantity')}")
            print(f"   Type: {explosion.get('type')}")
            print(f"   Level: {explosion.get('level')}")
            
            def count_children(node, depth=0):
                """Recursively count children"""
                count = 1
                if 'children' in node and node['children']:
                    for child in node['children']:
                        count += count_children(child, depth + 1)
                return count
            
            total_nodes = count_children(explosion)
            print(f"   Total BOM nodes: {total_nodes}")
        else:
            print("⚠️ No BOM explosion result")
        
        # Step 4: Generate Work Orders
        print("\n🏭 Step 4: Generating Work Orders from MO...")
        
        work_orders = service.explode_mo_and_generate_work_orders(
            mo_id=mo.id,
            qty_planned=mo.qty_planned
        )
        
        if work_orders:
            print(f"✅ Generated {len(work_orders)} Work Orders:\n")
            
            for wo in work_orders:
                dept_str = wo.department.value if hasattr(wo.department, 'value') else str(wo.department)
                status_str = wo.status.value if hasattr(wo.status, 'value') else str(wo.status)
                
                print(f"  {wo.sequence}. {wo.wo_number}")
                print(f"     Department: {dept_str}")
                print(f"     Status: {status_str}")
                print(f"     Target Qty: {wo.target_qty} pcs")
                
                # Check dependencies
                can_start, reason = service.check_wo_dependencies(wo.id)
                if can_start:
                    print(f"     ✅ Can start: {reason}")
                else:
                    print(f"     ⏳ Cannot start: {reason}")
                print()
        else:
            print("❌ No Work Orders generated")
        
        # Step 5: Test dependency checking
        print("\n🔗 Step 5: Testing Work Order dependencies...")
        
        for wo in work_orders:
            can_start, reason = service.check_wo_dependencies(wo.id)
            dept_str = wo.department.value if hasattr(wo.department, 'value') else str(wo.department)
            
            status_icon = "✅" if can_start else "⏳"
            print(f"  {status_icon} {wo.wo_number} ({dept_str}): {reason}")
        
        # Step 6: Simulate completing first WO
        print("\n⚡ Step 6: Simulating Work Order progression...")
        
        if work_orders:
            first_wo = work_orders[0]
            print(f"  ✅ Completing WO: {first_wo.wo_number}")
            
            # Complete the WO
            from app.core.models.manufacturing import WorkOrderStatus
            first_wo.status = WorkOrderStatus.FINISHED
            db.flush()
            
            # Trigger auto-update
            service.update_wo_status_auto(mo_id=mo.id)
            
            # Check updated statuses
            print("\n  Updated statuses:")
            for wo in work_orders:
                db.refresh(wo)
                status_str = wo.status.value if hasattr(wo.status, 'value') else str(wo.status)
                print(f"    {wo.wo_number}: {status_str}")
        
        # Step 7: Test API-style response
        print("\n📊 Step 7: Testing API response format...")
        
        api_response = {
            "success": True,
            "message": f"Generated {len(work_orders)} Work Orders",
            "mo_id": mo.id,
            "mo_batch_number": mo.batch_number,
            "work_orders_created": len(work_orders),
            "work_orders": [
                {
                    "id": wo.id,
                    "wo_number": wo.wo_number,
                    "department": wo.department.value if hasattr(wo.department, 'value') else str(wo.department),
                    "sequence": wo.sequence,
                    "status": wo.status.value if hasattr(wo.status, 'value') else str(wo.status),
                    "target_qty": float(wo.target_qty)
                }
                for wo in work_orders
            ]
        }
        
        print("✅ API Response format:")
        import json
        print(json.dumps(api_response, indent=2, ensure_ascii=False))
        
        print("\n✅ TEST COMPLETED SUCCESSFULLY!")
        
        # Cleanup
        print("\n🧹 Cleaning up test data...")
        db.rollback()
        print("✅ Test data cleaned up (rolled back)")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    
    finally:
        db.close()


if __name__ == "__main__":
    test_work_order_api()
