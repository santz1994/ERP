import sys
sys.path.insert(0, r'd:\Project\ERP2026\erp-softtoys')

from app.core.database import SessionLocal
from app.core.models.warehouse import StockQuant
from app.core.models.products import Product

db = SessionLocal()

total = db.query(StockQuant).count()
print(f'Total stock_quants rows: {total}')

if total > 0:
    samples = db.query(StockQuant).limit(5).all()
    for sq in samples:
        p = db.query(Product).filter(Product.id == sq.product_id).first()
        pname = p.code if p else 'UNKNOWN'
        print(f'  id={sq.id} product_id={sq.product_id} ({pname}) qty_on_hand={sq.qty_on_hand} qty_reserved={sq.qty_reserved}')
else:
    # Check products table
    prod_count = db.query(Product).count()
    print(f'Products table has {prod_count} products')
    print('stock_quants table is EMPTY - no inventory data exists yet')

db.close()
