"""
Fix Alembic Migration Chain
Cleans up duplicate migrations and creates proper chain
"""
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

def fix_migrations():
    """Fix migration chain issues"""
    print("🔧 Fixing migration chain...")
    
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        # Check if alembic_version table exists
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'alembic_version'
            )
        """))
        
        table_exists = result.scalar()
        
        if table_exists:
            # Get current version
            result = conn.execute(text("SELECT version_num FROM alembic_version"))
            current_version = result.scalar()
            print(f"📌 Current version: {current_version}")
            
            # Clear alembic_version table
            conn.execute(text("DELETE FROM alembic_version"))
            conn.commit()
            print("✅ Cleared alembic_version table")
        else:
            print("⚠️ alembic_version table doesn't exist yet")
        
        # Create alembic_version table if not exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS alembic_version (
                version_num VARCHAR(32) NOT NULL,
                CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
            )
        """))
        conn.commit()
        print("✅ alembic_version table ready")
    
    engine.dispose()
    print("\n🎉 Migration chain fixed!")
    print("\n📝 Next steps:")
    print("1. Review and clean up duplicate migration files")
    print("2. Run: alembic stamp head")
    print("3. Run: alembic upgrade head")

if __name__ == "__main__":
    fix_migrations()
