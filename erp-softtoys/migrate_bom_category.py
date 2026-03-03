"""One-time migration: add bom_category column to bom_headers."""
from app.core.database import engine
from sqlalchemy import text

with engine.connect() as conn:

    # 1. Check/fix enum type
    rows = conn.execute(text(
        "SELECT e.enumlabel FROM pg_type t JOIN pg_enum e "
        "ON t.oid = e.enumtypid WHERE t.typname = 'bomcategory'"
    )).fetchall()
    existing_vals = [r[0] for r in rows]
    print(f"Existing bomcategory values: {existing_vals}")

    # Drop if wrong-case values exist
    if existing_vals and "Production" not in existing_vals:
        conn.execute(text("DROP TYPE bomcategory CASCADE"))
        conn.commit()
        existing_vals = []
        print("Dropped old bomcategory enum (wrong case)")

    # Create enum if missing
    if not existing_vals:
        conn.execute(text(
            "CREATE TYPE bomcategory AS ENUM ('Production', 'Purchase')"
        ))
        conn.commit()
        print("Created bomcategory enum")
    else:
        print("bomcategory enum OK")

    # 2. Add column if missing
    col = conn.execute(text(
        "SELECT 1 FROM information_schema.columns "
        "WHERE table_name='bom_headers' AND column_name='bom_category'"
    )).fetchone()

    if not col:
        conn.execute(text(
            "ALTER TABLE bom_headers "
            "ADD COLUMN bom_category bomcategory NOT NULL DEFAULT 'Production'"
        ))
        conn.commit()
        print("Column bom_category added")
    else:
        print("Column bom_category already exists")

    # 3. Classify: PURCH% and FGD% -> Purchase
    result = conn.execute(text(
        "UPDATE bom_headers SET bom_category = 'Purchase' "
        "WHERE (revision ILIKE 'PURCH%' OR revision ILIKE 'FGD%') "
        "AND bom_category = 'Production'"
    ))
    conn.commit()
    print(f"Set to Purchase: {result.rowcount} rows")

    # 4. Summary
    rows = conn.execute(text(
        "SELECT bom_category, COUNT(*) FROM bom_headers GROUP BY bom_category"
    )).fetchall()
    print("\nSummary:")
    for row in rows:
        print(f"  {row[0]}: {row[1]} BOM headers")

print("Migration complete.")
