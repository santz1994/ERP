"""Check Manufacturing Orders Schema"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv('DATABASE_URL'))
inspector = inspect(engine)

print("📋 Manufacturing Orders Table Schema:\n")
columns = inspector.get_columns('manufacturing_orders')
for col in columns:
    print(f"  - {col['name']}: {col['type']}")

print("\n🔑 Primary Keys:")
pk = inspector.get_pk_constraint('manufacturing_orders')
print(f"  {pk}")
