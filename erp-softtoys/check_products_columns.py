"""
Check products table columns
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import engine
from sqlalchemy import text

print("🔍 Checking products table columns...")

try:
    with engine.connect() as conn:
        # Check all columns
        verify_sql = """
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'products'
        ORDER BY ordinal_position;
        """
        result = conn.execute(text(verify_sql))
        rows = result.fetchall()
        
        print("\n📊 Products table columns:")
        has_pcs_per_carton = False
        has_cartons_per_pallet = False
        for row in rows:
            print(f"  - {row[0]}: {row[1]}")
            if row[0] == 'pcs_per_carton':
                has_pcs_per_carton = True
            if row[0] == 'cartons_per_pallet':
                has_cartons_per_pallet = True
        
        print(f"\n{'✅' if has_pcs_per_carton else '❌'} pcs_per_carton column")
        print(f"{'✅' if has_cartons_per_pallet else '❌'} cartons_per_pallet column")
        
        if not has_pcs_per_carton or not has_cartons_per_pallet:
            print("\n🔧 Adding missing columns...")
            if not has_pcs_per_carton:
                conn.execute(text("ALTER TABLE products ADD COLUMN pcs_per_carton INTEGER"))
                print("  ✅ Added pcs_per_carton")
            if not has_cartons_per_pallet:
                conn.execute(text("ALTER TABLE products ADD COLUMN cartons_per_pallet INTEGER"))
                print("  ✅ Added cartons_per_pallet")
            conn.commit()
            
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
