"""
Apply PRODUCTS table pallet columns migration
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import engine
from sqlalchemy import text

print("🔧 Applying PRODUCTS table pallet columns migration...")

migration_sql = """
-- Add pallet specifications to products table
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS pcs_per_carton INTEGER;

ALTER TABLE products 
ADD COLUMN IF NOT EXISTS cartons_per_pallet INTEGER;

-- Add comments
COMMENT ON COLUMN products.pcs_per_carton IS 
    'Fixed number of pieces per carton (e.g., 60 for AFTONSPARV). NULL for non-finished goods.';
COMMENT ON COLUMN products.cartons_per_pallet IS 
    'Fixed number of cartons per pallet (typically 8 from BOM analysis). NULL for non-finished goods.';
"""

try:
    with engine.connect() as conn:
        # Execute migration
        for stmt in migration_sql.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                print(f"Executing: {stmt[:80]}...")
                conn.execute(text(stmt))
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify columns were added
        verify_sql = """
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'products' 
          AND column_name IN ('pcs_per_carton', 'cartons_per_pallet');
        """
        result = conn.execute(text(verify_sql))
        rows = result.fetchall()
        
        print("\n📊 Verification - Added columns:")
        for row in rows:
            print(f"  - {row[0]}: {row[1]} (default: {row[2]})")
            
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
