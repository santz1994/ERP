"""
Manual stamp database to mark migrations as complete without running them.
Use this when database already has the schema changes.
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def manual_stamp_database():
    """Manually stamp database to revision 002 (skip existing migrations)"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if alembic_version table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            )
        """))
        table_exists = result.scalar()
        
        if not table_exists:
            print("Creating alembic_version table...")
            conn.execute(text("""
                CREATE TABLE alembic_version (
                    version_num VARCHAR(100) NOT NULL PRIMARY KEY
                )
            """))
            print("✅ alembic_version table created")
        
        # Check current version
        result = conn.execute(text("SELECT version_num FROM alembic_version"))
        current_version = result.scalar()
        
        if current_version:
            print(f"Current database version: {current_version}")
        else:
            print("No current version (fresh database)")
        
        # Delete any existing version
        conn.execute(text("DELETE FROM alembic_version"))
        
        # Insert revision 002 (mark migrations 001 and 002 as done)
        conn.execute(text("INSERT INTO alembic_version (version_num) VALUES ('002')"))
        conn.commit()
        
        print("✅ Database stamped to revision '002'")
        print("   - Migration 001: ✅ Marked as complete")
        print("   - Migration 002: ✅ Marked as complete")
        print("   - Migration 003: Ready to run")

if __name__ == '__main__':
    manual_stamp_database()
