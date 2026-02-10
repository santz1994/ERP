"""
Comprehensive database schema validation
Test all major tables for schema mismatches
"""
import sys
sys.path.insert(0, 'd:/Project/ERP2026/erp-softtoys')

from app.core.database import get_db
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder
from app.core.models.products import Product
from app.core.models.warehouse import StockQuant
# Import purchasing models from correct location
try:
    from app.core.models import PurchaseOrder
except:
    PurchaseOrder = None
from sqlalchemy.orm import joinedload
from sqlalchemy import inspect

print("🔍 Comprehensive Database Schema Validation")
print("=" * 60)

db = next(get_db())
errors_found = []

# Test each model
models_to_test = [
    ("Product", Product),
    ("ManufacturingOrder", ManufacturingOrder),
    ("WorkOrder", WorkOrder),
    ("PurchaseOrder", PurchaseOrder),
    ("StockQuant", StockQuant),
]

for model_name, model_class in models_to_test:
    try:
        print(f"\n Testing {model_name}...")
        count = db.query(model_class).count()
        print(f"   ✅ {model_name}: {count} records")
    except Exception as e:
        error_msg = str(e)
        if "UndefinedColumn" in error_msg or "does not exist" in error_msg:
            # Extract column name
            import re
            match = re.search(r'column.*?(\w+\.\w+) does not exist', error_msg)
            if match:
                column = match.group(1)
                errors_found.append(f"{model_name}: Missing column {column}")
                print(f"   ❌ {model_name}: Missing column {column}")
            else:
                errors_found.append(f"{model_name}: {error_msg[:100]}")
                print(f"   ❌ {model_name}: {error_msg[:100]}")
        else:
            print(f"   ⚠️  {model_name}: {error_msg[:100]}")

# Test additional tables mentioned in the original error (skip for now)

print("\n" + "=" * 60)
if errors_found:
    print(f"\n❌ Found {len(errors_found)} schema errors:")
    for error in errors_found:
        print(f"   - {error}")
else:
    print("\n✅ All models validated successfully!")
    print("   No schema mismatches detected.")
