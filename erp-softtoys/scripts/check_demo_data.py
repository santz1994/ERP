"""
Check Demo Data Status
Shows current data in database for live demo
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

def check_data():
    """Check existing data"""
    print("🔍 Checking demo data status...\n")
    
    engine = create_engine(os.getenv('DATABASE_URL'))
    
    with engine.connect() as conn:
        # Users
        result = conn.execute(text('SELECT COUNT(*) FROM users'))
        users_count = result.scalar()
        print(f"✅ Users: {users_count}")
        
        # Products
        result = conn.execute(text('SELECT COUNT(*) FROM products'))
        products_count = result.scalar()
        print(f"✅ Products: {products_count}")
        
        # Manufacturing Orders
        result = conn.execute(text('SELECT COUNT(*) FROM manufacturing_orders'))
        mo_count = result.scalar()
        print(f"✅ Manufacturing Orders: {mo_count}")
        
        # Work Orders
        result = conn.execute(text('SELECT COUNT(*) FROM work_orders'))
        wo_count = result.scalar()
        print(f"✅ Work Orders: {wo_count}")
        
        # Categories
        result = conn.execute(text('SELECT COUNT(*) FROM categories'))
        cat_count = result.scalar()
        print(f"✅ Categories: {cat_count}")
        
        # Partners
        result = conn.execute(text('SELECT COUNT(*) FROM partners'))
        partner_count = result.scalar()
        print(f"✅ Partners: {partner_count}")
        
        print(f"\n📊 Summary:")
        print(f"  Total Users: {users_count}")
        print(f"  Total Products: {products_count}")
        print(f"  Total MOs: {mo_count}")
        print(f"  Total WOs: {wo_count}")
        
        if mo_count > 0:
            print("\n📦 Latest Manufacturing Orders:")
            result = conn.execute(text("""
                SELECT mo_number, target_qty, status 
                FROM manufacturing_orders 
                ORDER BY created_at DESC 
                LIMIT 5
            """))
            for row in result:
                print(f"  - {row[0]}: {row[1]} pcs ({row[2]})")
    
    engine.dispose()

if __name__ == "__main__":
    check_data()
