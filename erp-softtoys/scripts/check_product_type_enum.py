"""Check producttype enum values"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_product_type_enum():
    """Check what values are in the producttype enum"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check enum values
        result = conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'producttype'
            ORDER BY enumsortorder
        """))
        
        enum_values = [row[0] for row in result]
        
        print("Product Type ENUM values:")
        for val in enum_values:
            print(f"  - {val}")
        
        # Check what values are actually used in products table
        result = conn.execute(text("""
            SELECT type, COUNT(*) as count
            FROM products
            GROUP BY type
            ORDER BY count DESC
        """))
        
        print("\nActual values in products.type column:")
        for row in result:
            print(f"  - {row[0]}: {row[1]} products")

if __name__ == '__main__':
    check_product_type_enum()
