import sys
sys.path.insert(0, r'd:\Project\ERP2026\erp-softtoys')
from app.core.database import SessionLocal
import sqlalchemy as sa

db = SessionLocal()
q = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name='purchase_orders' ORDER BY ordinal_position"
result = db.execute(sa.text(q))
for row in result:
    print(row[0], '-', row[1])
db.close()
