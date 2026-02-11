"""Quick check: Compare material codes from Excel vs Database."""
import pandas as pd
from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:password123@localhost:5432/erp_quty_karunia"
engine = create_engine(DATABASE_URL)

print("📊 MATERIAL CODE COMPARISON")
print("=" * 80)

# Get material codes from database
with engine.connect() as conn:
    # First, check what ProductType values actually exist
    result = conn.execute(text("""
        SELECT DISTINCT type FROM products ORDER BY type
    """))
    types = [row[0] for row in result]
    print(f"\n📋 ProductType values in database: {types}")
    
    # Get materials - try different type value
    result = conn.execute(text("""
        SELECT code, name, type
        FROM products 
        WHERE code IS NOT NULL
        ORDER BY code
        LIMIT 15
    """))
    db_materials = [(row[0], row[1], row[2]) for row in result]

print(f"\n✅ Database products (first 15):")
for code, name, ptype in db_materials:
    print(f"   [{code}] {name[:50]} ({ptype})")

# Get material codes from Excel (Cutting.xlsx)
df = pd.read_excel('docs/Masterdata/BOM Production/Cutting.xlsx', nrows=20)
excel_components = df['BoM Lines/Component'].dropna().unique()[:10]

print(f"\n📋 Excel BOM has material codes (first 10):")
for comp in excel_components:
    # Extract code from [CODE] format
    if '[' in str(comp) and ']' in str(comp):
        code = str(comp).split('[')[1].split(']')[0]
        print(f"   [{code}] {comp[:70]}")

print("\n" + "=" * 80)
print("🔍 Checking if Excel codes exist in database...")

match_count = 0
for comp in excel_components:
    if '[' in str(comp) and ']' in str(comp):
        code = str(comp).split('[')[1].split(']')[0]
        # Check if exists in DB (any type)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*), type
                FROM products 
                WHERE code = :code
                GROUP BY type
            """), {"code": code})
            row = result.first()
            exists = row is not None
        
        if exists:
            print(f"   ✅ {code} - EXISTS (type: {row[1]})")
            match_count += 1
        else:
            print(f"   ❌ {code} - NOT FOUND")

print(f"\n📊 Match rate: {match_count}/{len(excel_components)} ({match_count/len(excel_components)*100:.0f}%)")
