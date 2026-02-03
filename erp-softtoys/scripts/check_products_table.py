"""Check products table structure"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_products_table():
    """Check products table structure"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check columns
        result = conn.execute(text("""
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = 'products'
            ORDER BY ordinal_position
        """))
        
        print("Products table columns:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} ({row[2]})")

if __name__ == '__main__':
    check_products_table()
