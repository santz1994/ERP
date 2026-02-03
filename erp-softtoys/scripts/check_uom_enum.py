"""Check UOM enum values"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def check_uom_enum():
    """Check what values are in the uom enum"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check enum values
        result = conn.execute(text("""
            SELECT enumlabel 
            FROM pg_enum 
            JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
            WHERE pg_type.typname = 'uom'
            ORDER BY enumsortorder
        """))
        
        enum_values = [row[0] for row in result]
        
        print("UOM ENUM values:")
        for val in enum_values:
            print(f"  - {val}")

if __name__ == '__main__':
    check_uom_enum()
