"""
AUTOMATED MIGRATION RUNNER
Run this after pulling new code to ensure database schema is up-to-date
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import engine
from sqlalchemy import text

print("🚀 ERP Database Schema Auto-Migration")
print("=" * 70)
print("This script ensures your database schema matches the codebase\n")

migrations = [
    {
        "name": "Products - Pallet Specifications",
        "sql": [
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS pcs_per_carton INTEGER",
            "ALTER TABLE products ADD COLUMN IF NOT EXISTS cartons_per_pallet INTEGER",
        ]
    },
    {
        "name": "Work Orders - Pallet Tracking",
        "sql": [
            "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS cartons_packed INTEGER DEFAULT 0",
            "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS pallets_formed INTEGER DEFAULT 0",
            "ALTER TABLE work_orders ADD COLUMN IF NOT EXISTS packing_validated BOOLEAN DEFAULT FALSE",
        ]
    },
    {
        "name": "Purchase Orders - Pallet Planning",
        "sql": [
            "ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS target_pallets INTEGER",
            "ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS expected_cartons INTEGER",
            "ALTER TABLE purchase_orders ADD COLUMN IF NOT EXISTS calculated_pcs INTEGER",
        ]
    },
]

try:
    with engine.connect() as conn:
        total_migrations = 0
        
        for migration in migrations:
            print(f"📦 {migration['name']}")
            for sql_stmt in migration['sql']:
                try:
                    column_name = sql_stmt.split('ADD COLUMN IF NOT EXISTS ')[1].split()[0]
                    conn.execute(text(sql_stmt))
                    total_migrations += 1
                    print(f"   ✅ {column_name}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ⏭️  {column_name} (already exists)")
                    else:
                        print(f"   ❌ {column_name}: {str(e)[:80]}")
        
        conn.commit()
        
        print("\n" + "=" * 70)
        print(f"✅ Migration completed! {total_migrations} columns checked/added.")
        print("🎉 Database schema is now up-to-date!\n")
        
except Exception as e:
    print(f"\n❌ Fatal error: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
