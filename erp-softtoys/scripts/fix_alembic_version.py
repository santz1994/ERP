"""Fix alembic_version table column length"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def fix_alembic_version():
    """Increase version_num column length to support longer migration names"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check current structure
        print("Checking current alembic_version table structure...")
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'alembic_version'
        """))
        
        for row in result:
            print(f"  {row[0]}: {row[1]}({row[2]})")
        
        # Alter column to VARCHAR(100)
        print("\nAltering version_num column to VARCHAR(100)...")
        conn.execute(text("""
            ALTER TABLE alembic_version 
            ALTER COLUMN version_num TYPE VARCHAR(100)
        """))
        conn.commit()
        
        print("✅ Column altered successfully!")
        
        # Verify new structure
        print("\nVerifying new structure...")
        result = conn.execute(text("""
            SELECT column_name, data_type, character_maximum_length 
            FROM information_schema.columns 
            WHERE table_name = 'alembic_version'
        """))
        
        for row in result:
            print(f"  {row[0]}: {row[1]}({row[2]})")

if __name__ == '__main__':
    fix_alembic_version()
