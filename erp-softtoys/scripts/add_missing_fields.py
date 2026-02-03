"""Add missing WIP fields to work_orders table"""

from app.core.database import engine
from sqlalchemy import text

# Add missing columns
with engine.begin() as conn:
    print("\n🔄 Adding missing fields to work_orders...")
    
    # Check and add wo_number
    try:
        conn.execute(text("ALTER TABLE work_orders ADD COLUMN wo_number VARCHAR(100)"))
        print("  ✅ Added wo_number column")
    except Exception as e:
        if "already exists" in str(e):
            print("  ⏭️  wo_number already exists")
        else:
            raise
    
    # Check and add target_qty
    try:
        conn.execute(text("ALTER TABLE work_orders ADD COLUMN target_qty NUMERIC(10, 2)"))
        print("  ✅ Added target_qty column")
    except Exception as e:
        if "already exists" in str(e):
            print("  ⏭️  target_qty already exists")
        else:
            raise
    
    # Check and add notes
    try:
        conn.execute(text("ALTER TABLE work_orders ADD COLUMN notes TEXT"))
        print("  ✅ Added notes column")
    except Exception as e:
        if "already exists" in str(e):
            print("  ⏭️  notes already exists")
        else:
            raise
    
    # Add foreign keys for WIP products (if not exist)
    try:
        conn.execute(text("""
            ALTER TABLE work_orders 
            ADD CONSTRAINT fk_wo_input_wip_product 
            FOREIGN KEY (input_wip_product_id) REFERENCES products(id) ON DELETE SET NULL
        """))
        print("  ✅ Added foreign key for input_wip_product_id")
    except Exception as e:
        if "already exists" in str(e):
            print("  ⏭️  FK for input_wip_product_id already exists")
        else:
            print(f"  ⚠️  Could not add FK: {e}")
    
    try:
        conn.execute(text("""
            ALTER TABLE work_orders 
            ADD CONSTRAINT fk_wo_output_wip_product 
            FOREIGN KEY (output_wip_product_id) REFERENCES products(id) ON DELETE SET NULL
        """))
        print("  ✅ Added foreign key for output_wip_product_id")
    except Exception as e:
        if "already exists" in str(e):
            print("  ⏭️  FK for output_wip_product_id already exists")
        else:
            print(f"  ⚠️  Could not add FK: {e}")

print("\n✅ All missing fields added successfully!")
