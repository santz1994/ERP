"""
Create Dummy Data with Real BOMs
Session 41 - Quick Data Population Script

This script creates:
1. Manufacturing Orders (MOs) - using real products from DB
2. Work Orders (WOs) - for each department based on routing
3. Uses actual BOM data from database

Run with: python create_dummy_data.py
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models.manufacturing import (
    ManufacturingOrder, WorkOrder, Department,
    MOState, WorkOrderStatus, RoutingType
)
from app.core.models.products import Product, ProductType
from app.core.models.bom import BOMHeader


def create_dummy_data(db: Session):
    """Create dummy manufacturing orders and work orders."""
    
    print("=" * 60)
    print("CREATING DUMMY DATA WITH REAL BOMs")
    print("=" * 60)
    
    # Get real products with BOMs
    products_with_bom = (
        db.query(Product)
        .join(BOMHeader, BOMHeader.product_id == Product.id)
        .filter(
            Product.type.in_([ProductType.WIP, ProductType.FINISH_GOOD]),
            BOMHeader.is_active == True
        )
        .limit(10)
        .all()
    )
    
    if not products_with_bom:
        print("❌ No products with active BOMs found!")
        print("   Please create BOMs first using BOM Explorer in the frontend.")
        return
    
    print(f"\n✅ Found {len(products_with_bom)} products with active BOMs")
    print("\nProducts to create MOs for:")
    for prod in products_with_bom:
        print(f"   - [{prod.code}] {prod.name} ({prod.type})")
    
    # Create Manufacturing Orders
    mos_created = []
    batch_base = datetime.now().strftime("%Y%m%d")
    
    for idx, product in enumerate(products_with_bom[:5], start=1):  # Create 5 MOs
        # Check if batch already exists
        batch_number = f"BATCH-{batch_base}-{idx:03d}"
        existing = db.query(ManufacturingOrder).filter(
            ManufacturingOrder.batch_number == batch_number
        ).first()
        
        if existing:
            print(f"\n⚠️  MO for {batch_number} already exists, skipping...")
            mos_created.append(existing)
            continue
        
        # Determine routing based on product type
        if idx % 3 == 0:
            routing = RoutingType.ROUTE1  # Full: Cutting → Emb → Sewing → Finishing → Packing
        elif idx % 3 == 1:
            routing = RoutingType.ROUTE2  # Direct: Sewing → Finishing → Packing
        else:
            routing = RoutingType.ROUTE3  # Subcon: Finishing → Packing
        
        # Create MO
        mo = ManufacturingOrder(
            product_id=product.id,
            qty_planned=Decimal(1000 + (idx * 100)),  # 1000, 1100, 1200, etc.
            qty_produced=Decimal(0),
            routing_type=routing.value,
            batch_number=batch_number,
            state=MOState.DRAFT,
            created_at=datetime.utcnow(),
            so_line_id=None  # No sales order link for dummy data
        )
        
        db.add(mo)
        db.flush()  # Get ID before creating WOs
        
        mos_created.append(mo)
        print(f"\n✅ Created MO #{mo.id}: {product.code} | {batch_number} | {routing.value}")
        
        # Create Work Orders based on routing
        departments = []
        if routing == RoutingType.ROUTE1:
            departments = [
                Department.CUTTING,
                Department.EMBROIDERY,
                Department.SEWING,
                Department.FINISHING,
                Department.PACKING
            ]
        elif routing == RoutingType.ROUTE2:
            departments = [
                Department.SEWING,
                Department.FINISHING,
                Department.PACKING
            ]
        else:  # ROUTE3
            departments = [
                Department.FINISHING,
                Department.PACKING
            ]
        
        # Create WOs for each department
        for seq, dept in enumerate(departments, start=1):
            wo = WorkOrder(
                mo_id=mo.id,
                product_id=product.id,  # Add product_id (required)
                department=dept,
                sequence=seq,  # Changed from sequence_number to sequence
                status=WorkOrderStatus.PENDING,
                input_qty=mo.qty_planned,
                output_qty=Decimal(0),
                reject_qty=Decimal(0),
                start_time=None,
                end_time=None,
                notes=f"Auto-generated WO for {dept.value}"
            )
            db.add(wo)
            print(f"   └─ WO {seq}: {dept.value} (PENDING)")
    
    # Commit all changes
    try:
        db.commit()
        print("\n" + "=" * 60)
        print(f"✅ SUCCESS! Created {len(mos_created)} Manufacturing Orders")
        print("=" * 60)
        
        # Summary
        print("\n📊 SUMMARY:")
        print(f"   Total MOs created: {len(mos_created)}")
        
        total_wos = db.query(WorkOrder).filter(
            WorkOrder.mo_id.in_([mo.id for mo in mos_created])
        ).count()
        print(f"   Total WOs created: {total_wos}")
        
        # Count by department
        for dept in Department:
            count = db.query(WorkOrder).filter(
                WorkOrder.mo_id.in_([mo.id for mo in mos_created]),
                WorkOrder.department == dept
            ).count()
            if count > 0:
                print(f"      - {dept.value}: {count} WOs")
        
        print("\n✅ You can now:")
        print("   1. View MOs in PPIC Page")
        print("   2. Start MOs using the Start button")
        print("   3. Process WOs in each department page")
        print("   4. Track production progress in dashboard")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR: {str(e)}")
        raise


def main():
    """Main execution."""
    db = SessionLocal()
    try:
        create_dummy_data(db)
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
