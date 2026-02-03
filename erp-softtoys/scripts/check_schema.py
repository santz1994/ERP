"""Check database schema for existing WIP routing fields"""

from app.core.database import engine
from sqlalchemy import inspect

insp = inspect(engine)

print("\n" + "="*80)
print("WORK_ORDERS TABLE COLUMNS")
print("="*80)
for col in insp.get_columns('work_orders'):
    print(f"  {col['name']:<30} {col['type']}")

print("\n" + "="*80)
print("MANUFACTURING_ORDERS TABLE COLUMNS")  
print("="*80)
for col in insp.get_columns('manufacturing_orders'):
    print(f"  {col['name']:<30} {col['type']}")

print("\n" + "="*80)
print("EXISTING TABLES")
print("="*80)
tables = insp.get_table_names()
for table in sorted(tables):
    print(f"  - {table}")

print("\n✅ Schema check complete!")
