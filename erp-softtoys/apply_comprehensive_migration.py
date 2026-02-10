"""
Direct SQL migration - apply all missing columns at once
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import engine  
from sqlalchemy import text

print("🔧 Applying comprehensive database migration...")
print("=" * 60)

try:
    with engine.connect() as conn:
        # 1. Products table - pallet columns
        print("\n1. Adding pallet columns to PRODUCTS table...")
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS pcs_per_carton INTEGER"))
            print("   ✅ pcs_per_carton")
        except Exception as e:
            print(f"   ⚠️  pcs_per_carton: {str(e)[:100]}")
        
        try:
            conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS cartons_per_pallet INTEGER"))
            print("   ✅ cartons_per_pallet")
        except Exception as e:
            print(f"   ⚠️  cartons_per_pallet: {str(e)[:100]}")
        
        # 2. Work orders table - pallet tracking
        print("\n2. Adding pallet tracking to WORK_ORDERS table...")
        try:
            conn.execute(text("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS cartons_packed INTEGER DEFAULT 0"))
            print("   ✅ cartons_packed")
        except Exception as e:
            print(f"   ⚠️  cartons_packed: {str(e)[:100]}")
        
        try:
            conn.execute(text("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS pallets_formed INTEGER DEFAULT 0"))
            print("   ✅ pallets_formed")
        except Exception as e:
            print(f"   ⚠️  pallets_formed: {str(e)[:100]}")
        
        try:
            conn.execute(text("ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS packing_validated BOOLEAN DEFAULT FALSE"))
            print("   ✅ packing_validated")
        except Exception as e:
            print(f"   ⚠️  packing_validated: {str(e)[:100]}")
        
        conn.commit()
        
        # Verify
        print("\n3. Verifying columns...")
        result = conn.execute(text("""
            SELECT table_name, column_name 
            FROM information_schema.columns 
            WHERE table_name IN ('products', 'work_orders')
              AND column_name IN ('pcs_per_carton', 'cartons_per_pallet', 
                                  'cartons_packed', 'pallets_formed', 'packing_validated')
            ORDER BY table_name, column_name
        """))
        
        print("\n✅ Added columns:")
        for row in result.fetchall():
            print(f"   - {row[0]}.{row[1]}")
        
        print("\n✅ Migration completed successfully!")
        
except Exception as e:
    print(f"\n❌ Fatal error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
