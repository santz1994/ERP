"""Manually add missing PO Reference System columns"""
from app.core.database import engine
from sqlalchemy import text

# Add 5 missing columns
with engine.begin() as conn:
    # Column 1: source_po_kain_id
    conn.execute(text("""
        ALTER TABLE purchase_orders 
        ADD COLUMN IF NOT EXISTS source_po_kain_id INTEGER
    """))
    
    # Column 2: article_id (FK → products.id)
    conn.execute(text("""
        ALTER TABLE purchase_orders 
        ADD COLUMN IF NOT EXISTS article_id INTEGER
    """))
    
    # Column 3: article_qty
    conn.execute(text("""
        ALTER TABLE purchase_orders 
        ADD COLUMN IF NOT EXISTS article_qty INTEGER
    """))
    
    # Column 4: week
    conn.execute(text("""
        ALTER TABLE purchase_orders 
        ADD COLUMN IF NOT EXISTS week VARCHAR(20)
    """))
    
    # Column 5: destination
    conn.execute(text("""
        ALTER TABLE purchase_orders 
        ADD COLUMN IF NOT EXISTS destination VARCHAR(100)
    """))
    
    print("✅ Added 5 missing columns to purchase_orders")

# Add foreign keys
with engine.begin() as conn:
    # FK 1: source_po_kain_id → purchase_orders.id
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_po_source_po_kain') THEN
                ALTER TABLE purchase_orders 
                ADD CONSTRAINT fk_po_source_po_kain 
                FOREIGN KEY (source_po_kain_id) REFERENCES purchase_orders(id) ON DELETE RESTRICT;
            END IF;
        END $$;
    """))
    
    # FK 2: article_id → products.id
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_po_article') THEN
                ALTER TABLE purchase_orders 
                ADD CONSTRAINT fk_po_article 
                FOREIGN KEY (article_id) REFERENCES products(id) ON DELETE RESTRICT;
            END IF;
        END $$;
    """))
    
    # FK 3: linked_mo_id → manufacturing_orders.id (may already exist)
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_po_linked_mo') THEN
                ALTER TABLE purchase_orders 
                ADD CONSTRAINT fk_po_linked_mo 
                FOREIGN KEY (linked_mo_id) REFERENCES manufacturing_orders(id) ON DELETE SET NULL;
            END IF;
        END $$;
    """))
    
    print("✅ Added 3 foreign keys")

# Add indexes
with engine.begin() as conn:
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_po_source_po_kain ON purchase_orders(source_po_kain_id)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_po_article ON purchase_orders(article_id)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_po_type_status ON purchase_orders(po_type, status)
    """))
    
    conn.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_po_week ON purchase_orders(week)
    """))
    
    print("✅ Added 4 indexes")

# Add business rule constraints
with engine.begin() as conn:
    # Constraint 1: PO LABEL must have source_po_kain_id
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_po_label_requires_kain') THEN
                ALTER TABLE purchase_orders
                ADD CONSTRAINT chk_po_label_requires_kain
                CHECK (
                    (po_type = 'LABEL' AND source_po_kain_id IS NOT NULL) OR
                    (po_type != 'LABEL')
                );
            END IF;
        END $$;
    """))
    
    # Constraint 2: PO LABEL must have week AND destination
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_po_label_week_destination') THEN
                ALTER TABLE purchase_orders
                ADD CONSTRAINT chk_po_label_week_destination
                CHECK (
                    (po_type = 'LABEL' AND week IS NOT NULL AND destination IS NOT NULL) OR
                    (po_type != 'LABEL')
                );
            END IF;
        END $$;
    """))
    
    # Constraint 3: PO KAIN cannot self-reference
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_po_kain_no_self_reference') THEN
                ALTER TABLE purchase_orders
                ADD CONSTRAINT chk_po_kain_no_self_reference
                CHECK (
                    (po_type = 'KAIN' AND source_po_kain_id IS NULL) OR
                    (po_type != 'KAIN')
                );
            END IF;
        END $$;
    """))
    
    # Constraint 4: PO KAIN/LABEL must have article_id
    conn.execute(text("""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_po_article_required_for_kain_label') THEN
                ALTER TABLE purchase_orders
                ADD CONSTRAINT chk_po_article_required_for_kain_label
                CHECK (
                    ((po_type IN ('KAIN', 'LABEL')) AND article_id IS NOT NULL) OR
                    (po_type = 'ACCESSORIES')
                );
            END IF;
        END $$;
    """))
    
    print("✅ Added 4 business rule constraints")

print("\n🎉 PO Reference System migration complete!")
print("   - 7 columns (2 existing + 5 new)")
print("   - 3 foreign keys")
print("   - 4 indexes")
print("   - 4 business rule constraints")
