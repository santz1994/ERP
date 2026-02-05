"""Create Phase 2A warehouse finishing tables manually"""
import sys
sys.path.insert(0, r'd:\Project\ERP2026\erp-softtoys')

from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()

try:
    # Create warehouse_finishing_stocks table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS warehouse_finishing_stocks (
            id SERIAL PRIMARY KEY,
            stage VARCHAR(20) NOT NULL,
            product_id INTEGER NOT NULL REFERENCES products(id),
            good_qty NUMERIC(10, 2) NOT NULL DEFAULT 0,
            defect_qty NUMERIC(10, 2) NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
            UNIQUE(stage, product_id)
        )
    """))
    print("✅ warehouse_finishing_stocks created")
    
    # Create finishing_material_consumptions table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS finishing_material_consumptions (
            id SERIAL PRIMARY KEY,
            spk_id INTEGER NOT NULL REFERENCES spks(id),
            stage VARCHAR(20) NOT NULL,
            material_id INTEGER NOT NULL REFERENCES products(id),
            qty_planned NUMERIC(10, 2) NOT NULL,
            qty_actual NUMERIC(10, 2),
            uom VARCHAR(10) NOT NULL,
            lot_id INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """))
    print("✅ finishing_material_consumptions created")
    
    # Create index for finishing_material_consumptions
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_finishing_material_consumptions_spk_id 
        ON finishing_material_consumptions(spk_id)
    """))
    
    # Create finishing_inputs_outputs table
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS finishing_inputs_outputs (
            id SERIAL PRIMARY KEY,
            spk_id INTEGER NOT NULL REFERENCES spks(id),
            stage VARCHAR(20) NOT NULL,
            production_date DATE NOT NULL,
            input_qty NUMERIC(10, 2) NOT NULL,
            good_qty NUMERIC(10, 2) NOT NULL,
            defect_qty NUMERIC(10, 2) NOT NULL,
            rework_qty NUMERIC(10, 2) NOT NULL DEFAULT 0,
            yield_rate NUMERIC(5, 2) NOT NULL,
            operator_id INTEGER REFERENCES users(id),
            notes TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """))
    print("✅ finishing_inputs_outputs created")
    
    # Create indexes for finishing_inputs_outputs
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_finishing_inputs_outputs_spk_id 
        ON finishing_inputs_outputs(spk_id)
    """))
    
    db.execute(text("""
        CREATE INDEX IF NOT EXISTS ix_finishing_inputs_outputs_production_date 
        ON finishing_inputs_outputs(production_date)
    """))
    
    db.commit()
    print("\n✅ All Phase 2A warehouse finishing tables created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
