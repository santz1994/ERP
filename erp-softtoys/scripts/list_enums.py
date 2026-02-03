"""List all existing enum types in database"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def list_enums():
    """List all enum types in the database"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT typname
            FROM pg_type
            WHERE typtype = 'e'
            ORDER BY typname
        """))
        
        enums = [row[0] for row in result]
        
        if enums:
            print(f"Found {len(enums)} enum types:")
            for enum in enums:
                print(f"  - {enum}")
        else:
            print("No enum types found in database")
        
        return enums

if __name__ == '__main__':
    list_enums()
