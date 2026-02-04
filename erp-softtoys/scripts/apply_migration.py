"""
Apply Dual Trigger & Flexible Target Migration via Python
Connects to PostgreSQL and executes the SQL migration directly.
"""

import os
from pathlib import Path
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_url():
    """Get database URL from environment."""
    return os.getenv("DATABASE_URL", "postgresql://erp_user:erp_password@localhost:5432/erp_quty_karunia")

def apply_migration():
    """Apply the SQL migration."""
    # Read SQL file
    sql_path = Path(__file__).parent / "apply_dual_trigger_migration.sql"
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Connect to database
    print("🔌 Connecting to database...")
    engine = create_engine(get_db_url(), echo=False)
    
    with engine.connect() as conn:
        print("📝 Executing migration SQL...")
        
        # Execute the SQL (PostgreSQL supports multi-statement execution)
        try:
            conn.execute(text(sql_content))
            conn.commit()
            print("\n🎉 Migration completed successfully!")
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            conn.rollback()
            raise
    
    print("\n✅ Database schema updated with:")
    print("   - Dual Trigger System (ManufacturingOrder)")
    print("   - Flexible Target System (SPK)")
    print("   - Backward Compatible Aliases (WorkOrder)")

if __name__ == "__main__":
    apply_migration()
