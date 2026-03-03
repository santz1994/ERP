"""One-time migration: add bom_category column to bom_headers."""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # 1. Create enum type in Postgres
    conn.execute(text("""
        DO $$ BEGIN
            CREATE TYPE bomcategory AS ENUM ('Production', 'Purchase');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """))
    print('Enum type bomcategory: OK')

    # 2. Add column (idempotent)
    conn.execute(text("""
        ALTER TABLE bom_headers
        ADD COLUMN IF NOT EXISTS bom_category bomcategory NOT NULL DEFAULT 'Production';
    """))
    print('Column bom_category: OK')

    # 3. Classify existing BOMs
    result = conn.execute(text("""
        UPDATE bom_headers
        SET bom_category = 'Purchase'
        WHERE revision ILIKE 'PURCH%' OR revision ILIKE 'FGD%';
    """))
    print(f'Set Purchase category: {result.rowcount} rows')

    conn.commit()

    # 4. Summary
    rows = conn.execute(text(
        "SELECT bom_category, COUNT(*) FROM bom_headers GROUP BY bom_category"
    )).fetchall()
    print('\nSummary:')
    for row in rows:
        print(f'  {row[0]}: {row[1]} BOM headers')

print('\nMigration complete.')
