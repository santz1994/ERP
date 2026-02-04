"""
Quick check to verify dummy data is in database
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.core.models.manufacturing import ManufacturingOrder, WorkOrder

db = SessionLocal()

# Check MOs
mos = db.query(ManufacturingOrder).all()
print(f"\n📊 Manufacturing Orders in Database: {len(mos)}")
for mo in mos:
    print(f"   MO #{mo.id}: {mo.batch_number} | State: {mo.state} | Qty: {mo.qty_planned}")

# Check WOs
wos = db.query(WorkOrder).all()
print(f"\n📊 Work Orders in Database: {len(wos)}")
for wo in wos:
    print(f"   WO #{wo.id}: MO-{wo.mo_id} | {wo.department.value if hasattr(wo.department, 'value') else wo.department} | Status: {wo.status.value if hasattr(wo.status, 'value') else wo.status}")

db.close()
