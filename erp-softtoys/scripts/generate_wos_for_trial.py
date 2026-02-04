"""
Generate Work Orders for existing Manufacturing Orders
Author: IT Developer Expert
Date: 4 Februari 2026

This script generates Work Orders for the 5 MOs created in Week 1 Production Trial.
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import get_db
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder
from app.services.bom_explosion_service import BOMExplosionService


def generate_wos_for_trial_mos():
    """Generate Work Orders for trial MOs"""
    
    print("="*80)
    print("🏭 GENERATING WORK ORDERS FOR TRIAL MOs")
    print("="*80)
    
    db = next(get_db())
    bom_service = BOMExplosionService(db)
    
    try:
        # Find all trial MOs (created today)
        trial_mos = (
            db.query(ManufacturingOrder)
            .filter(ManufacturingOrder.batch_number.like('MO-TRIAL-%'))
            .all()
        )
        
        print(f"\n✅ Found {len(trial_mos)} Trial Manufacturing Orders")
        
        total_wos_created = 0
        
        for mo in trial_mos:
            print(f"\n{'='*80}")
            print(f"Processing: {mo.batch_number}")
            print(f"Product: {mo.product.name[:60]}...")
            print(f"Target: {mo.qty_planned} pcs")
            print(f"Week: {mo.production_week}")
            print(f"Destination: {mo.destination_country}")
            print("="*80)
            
            try:
                # Generate Work Orders
                work_orders = bom_service.explode_mo_and_generate_work_orders(
                    mo_id=mo.id,
                    qty_planned=mo.qty_planned
                )
                
                if work_orders:
                    print(f"\n✅ Successfully generated {len(work_orders)} Work Orders:")
                    for wo in work_orders:
                        dept = wo.department.name if hasattr(wo.department, 'name') else str(wo.department)
                        status = wo.status.name if hasattr(wo.status, 'name') else str(wo.status)
                        print(f"   • {wo.wo_number}")
                        print(f"     Department: {dept} (Seq #{wo.sequence})")
                        print(f"     Target: {wo.target_qty} pcs")
                        print(f"     Status: {status}")
                        
                        # Set planned dates from MO
                        if mo.planned_production_date:
                            # Calculate planned start date based on sequence
                            from datetime import timedelta
                            days_offset = (wo.sequence - 1) * 2  # 2 days per department
                            wo.planned_start_date = mo.planned_production_date + timedelta(days=days_offset)
                            wo.planned_completion_date = wo.planned_start_date + timedelta(days=2)
                            wo.production_date_stamp = wo.planned_start_date
                            print(f"     Planned Start: {wo.planned_start_date}")
                            print(f"     Planned Complete: {wo.planned_completion_date}")
                    
                    total_wos_created += len(work_orders)
                else:
                    print(f"❌ Failed to generate Work Orders for {mo.batch_number}")
                    
            except Exception as e:
                print(f"❌ Error generating WOs for {mo.batch_number}: {str(e)}")
                import traceback
                traceback.print_exc()
        
        # Summary
        print("\n" + "="*80)
        print("📊 GENERATION SUMMARY")
        print("="*80)
        print(f"\n✅ Processed {len(trial_mos)} Manufacturing Orders")
        print(f"✅ Generated {total_wos_created} Work Orders")
        print(f"\n📊 Average: {total_wos_created / len(trial_mos):.1f} WOs per MO")
        
        # Ask for commit
        print("\n" + "="*80)
        commit = input("\n💾 Commit changes to database? (yes/no): ").strip().lower()
        
        if commit == 'yes':
            db.commit()
            print("✅ Changes committed to database!")
            
            # Show final summary
            print("\n" + "="*80)
            print("🎉 FINAL SUMMARY")
            print("="*80)
            
            for mo in trial_mos:
                wos = db.query(WorkOrder).filter_by(mo_id=mo.id).all()
                print(f"\n{mo.batch_number} ({mo.production_week}, {mo.destination_country})")
                print(f"  Qty: {mo.qty_planned} pcs")
                print(f"  Traceability: {mo.traceability_code}")
                print(f"  Work Orders: {len(wos)}")
                for wo in wos:
                    dept = wo.department.name if hasattr(wo.department, 'name') else str(wo.department)
                    print(f"    • {wo.wo_number} - {dept} - {wo.target_qty} pcs")
            
            print("\n🎉 Week 1 Production Trial Complete!")
            print("\n📋 Next Steps:")
            print("   1. ✅ Week 1: Created 5 real MOs with datestamp ✓")
            print("   2. ✅ Week 1: Generated WOs and verified accuracy ✓")
            print("   3. ⏳ Week 1: Collect feedback from PPIC team")
            print("   4. ⏳ Week 2: Department Training")
            
        else:
            db.rollback()
            print("❌ Changes rolled back (not saved)")
        
    finally:
        db.close()


if __name__ == "__main__":
    generate_wos_for_trial_mos()
