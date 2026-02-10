"""
Test Database Connection and Work Orders Query
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import get_db
from app.core.models.manufacturing import WorkOrder
from sqlalchemy.orm import joinedload

print("🔍 Testing Database Connection...")

try:
    # Get DB session
    db = next(get_db())
    print("✅ Database connection successful\n")
    
    # Query work orders
    print("📊 Querying Work Orders...")
    query = db.query(WorkOrder).options(
        joinedload(WorkOrder.manufacturing_order),
        joinedload(WorkOrder.product)
    )
    
    work_orders = query.all()
    print(f"✅ Found {len(work_orders)} work orders\n")
    
    # Test accessing attributes
    if work_orders:
        wo = work_orders[0]
        print(f"Testing Work Order #{wo.id}:")
        print(f"  - mo_id: {wo.mo_id}")
        print(f"  - wo_number: {wo.wo_number}")
        print(f"  - department: {wo.department}")
        print(f"  - department.value: {wo.department.value if hasattr(wo.department, 'value') else 'N/A'}")
        print(f"  - status: {wo.status}")
        print(f"  - status.value: {wo.status.value if hasattr(wo.status, 'value') else 'N/A'}")
        print(f"  - sequence: {wo.sequence}")
        print(f"  - target_qty: {wo.target_qty}")
        print(f"  - input_qty: {wo.input_qty}")
        print(f"  - output_qty: {wo.output_qty}")
        print(f"  - reject_qty: {wo.reject_qty}")
        print(f"  - product: {wo.product}")
        if wo.product:
            print(f"  - product.code: {wo.product.code}")
            print(f"  - product.name: {wo.product.name}")
        print(f"\n✅ All attributes accessible")
    else:
        print("ℹ️  No work orders found in database")
        
except Exception as e:
    print(f"❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
