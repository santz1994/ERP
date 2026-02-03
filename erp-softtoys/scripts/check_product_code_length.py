"""Check products.code column length"""
from app.core.database import engine
from sqlalchemy import inspect

insp = inspect(engine)
cols = insp.get_columns('products')
code_col = [c for c in cols if c['name'] == 'code'][0]
name_col = [c for c in cols if c['name'] == 'name'][0]

print(f"products.code: {code_col['type']}")
print(f"products.name: {name_col['type']}")
