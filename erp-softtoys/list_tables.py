"""
Database Tables Information
Show all tables in the ERP database with row counts
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/erp_quty_karunia")

print("=" * 80)
print("ERP DATABASE STRUCTURE - erp_quty_karunia")
print("=" * 80)

try:
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # Get all tables
    tables = inspector.get_table_names()
    
    print(f"\n📋 Total Tables: {len(tables)}\n")
    print(f"{'#':<5} {'Table Name':<35} {'Row Count':<15}")
    print("-" * 80)
    
    with engine.connect() as conn:
        total_rows = 0
        for idx, table in enumerate(sorted(tables), start=1):
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                total_rows += count
                
                # Emoji indicators
                indicator = ""
                if count == 0:
                    indicator = "⚪"
                elif count < 10:
                    indicator = "🟡"
                elif count < 100:
                    indicator = "🟢"
                else:
                    indicator = "🔵"
                
                print(f"{idx:<5} {table:<35} {indicator} {count:<10}")
            except Exception as e:
                print(f"{idx:<5} {table:<35} ❌ Error")
    
    print("-" * 80)
    print(f"{'TOTAL':<5} {'All Tables':<35} {'📊 ' + str(total_rows):<15}")
    print("\n" + "=" * 80)
    
    print("\n📌 Legend:")
    print("  ⚪ Empty (0 rows)")
    print("  🟡 Few records (1-9 rows)")
    print("  🟢 Some records (10-99 rows)")
    print("  🔵 Many records (100+ rows)")
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
