"""
Add pallet planning columns to purchase_orders table
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import engine
from sqlalchemy import text

print("🔧 Adding pallet planning columns to purchase_orders table...")

migration_sql = """
ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS target_pallets INTEGER;

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS expected_cartons INTEGER;

ALTER TABLE purchase_orders 
ADD COLUMN IF NOT EXISTS calculated_pcs INTEGER;
"""

comments_sql = """
COMMENT ON COLUMN purchase_orders.target_pallets IS 
    'Number of pallets Purchasing wants to produce (input by Purchasing staff)';
COMMENT ON COLUMN purchase_orders.expected_cartons IS 
    'Auto-computed: target_pallets × article.cartons_per_pallet';
COMMENT ON COLUMN purchase_orders.calculated_pcs IS 
    'Auto-computed: target_pallets × article.pcs_per_pallet. Must match article_qty.';
"""

try:
    with engine.connect() as conn:
        print("\n1. Adding columns...")
        for stmt in migration_sql.split(';'):
            stmt = stmt.strip()
            if stmt:
                conn.execute(text(stmt))
                print(f"   ✅ {stmt[:60]}...")
        
        print("\n2. Adding comments...")
        for stmt in comments_sql.split(';'):
            stmt = stmt.strip()
            if stmt and not stmt.startswith('--'):
                conn.execute(text(stmt))
        
        conn.commit()
        
        # Verify
        print("\n3. Verifying columns...")
        verify_sql = """
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'purchase_orders' 
          AND column_name IN ('target_pallets', 'expected_cartons', 'calculated_pcs');
        """
        result = conn.execute(text(verify_sql))
        rows = result.fetchall()
        
        print("✅ Added columns:")
        for row in rows:
            print(f"   - {row[0]}: {row[1]}")
        
        print("\n✅ Migration completed successfully!")
        
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
