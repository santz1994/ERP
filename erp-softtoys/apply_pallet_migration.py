"""
Apply database migration to add pallet columns to work_orders table
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import engine
from sqlalchemy import text

print("🔧 Applying database migration...")
print("Adding pallet tracking columns to work_orders table\n")

migration_sql = """
-- Add columns
ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS cartons_packed INTEGER DEFAULT 0;

ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS pallets_formed INTEGER DEFAULT 0;

ALTER TABLE work_orders 
ADD COLUMN IF NOT EXISTS packing_validated BOOLEAN DEFAULT FALSE;

-- Add comments
COMMENT ON COLUMN work_orders.cartons_packed IS 'Number of cartons packed (must be multiple of article.cartons_per_pallet)';
COMMENT ON COLUMN work_orders.pallets_formed IS 'Number of pallets formed: cartons_packed / article.cartons_per_pallet';
COMMENT ON COLUMN work_orders.packing_validated IS 'TRUE if packing quantities validated (no partial cartons/pallets)';
"""

try:
    with engine.connect() as conn:
        # Execute migration
        for stmt in migration_sql.split(';'):
            stmt = stmt.strip()
            if stmt:
                print(f"Executing: {stmt[:80]}...")
                conn.execute(text(stmt))
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
        # Verify columns were added
        verify_sql = """
        SELECT column_name, data_type, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'work_orders' 
          AND column_name IN ('cartons_packed', 'pallets_formed', 'packing_validated');
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
