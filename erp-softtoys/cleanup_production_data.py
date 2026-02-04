"""
Cleanup Production Data Script
Session 41 - Clear all dummy/test production data

This script removes:
1. All Work Orders
2. All Manufacturing Orders
3. Material allocations
4. SPK material allocations

Run BEFORE creating new dummy data.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder, SPKMaterialAllocation, SPK


def cleanup_production_data(db: Session):
    """Remove all production data."""
    
    print("=" * 60)
    print("CLEANING UP PRODUCTION DATA")
    print("=" * 60)
    
    try:
        # Count existing records
        wo_count = db.query(WorkOrder).count()
        mo_count = db.query(ManufacturingOrder).count()
        spk_count = db.query(SPK).count()
        spk_alloc_count = db.query(SPKMaterialAllocation).count()
        
        print(f"\n📊 Current Data:")
        print(f"   Work Orders: {wo_count}")
        print(f"   Manufacturing Orders: {mo_count}")
        print(f"   SPKs: {spk_count}")
        print(f"   SPK Material Allocations: {spk_alloc_count}")
        
        if wo_count == 0 and mo_count == 0 and spk_count == 0 and spk_alloc_count == 0:
            print("\n✅ Database is already clean! No production data found.")
            return
        
        print("\n🗑️  Deleting production data...")
        
        # Delete in correct order (foreign key constraints)
        # 1. Delete SPK Material Allocations first
        if spk_alloc_count > 0:
            deleted = db.query(SPKMaterialAllocation).delete()
            print(f"   ✅ Deleted {deleted} SPK Material Allocations")
        
        # 2. Delete Work Orders (depends on MO)
        if wo_count > 0:
            deleted = db.query(WorkOrder).delete()
            print(f"   ✅ Deleted {deleted} Work Orders")
        
        # 3. Delete SPKs (depends on MO)
        if spk_count > 0:
            deleted = db.query(SPK).delete()
            print(f"   ✅ Deleted {deleted} SPKs")
        
        # 4. Delete Manufacturing Orders last
        if mo_count > 0:
            deleted = db.query(ManufacturingOrder).delete()
            print(f"   ✅ Deleted {deleted} Manufacturing Orders")
        
        # Commit changes
        db.commit()
        
        print("\n" + "=" * 60)
        print("✅ CLEANUP COMPLETE!")
        print("=" * 60)
        print("\n✅ Production database is now clean.")
        print("✅ You can now run: python create_dummy_data.py")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ ERROR during cleanup: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


def main():
    """Main execution."""
    db = SessionLocal()
    try:
        # Ask for confirmation
        print("\n⚠️  WARNING: This will DELETE all production data!")
        print("   - All Manufacturing Orders")
        print("   - All Work Orders")
        print("   - All SPKs")
        print("   - All SPK Material Allocations")
        
        response = input("\n❓ Are you sure you want to continue? (yes/no): ")
        
        if response.lower() in ['yes', 'y']:
            cleanup_production_data(db)
        else:
            print("\n❌ Cleanup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
