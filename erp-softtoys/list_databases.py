"""
List PostgreSQL Databases
Quick script to show all available databases
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Get database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:admin@localhost:5432/erp_quty_karunia")

# Parse to get connection to postgres database
parts = DATABASE_URL.rsplit('/', 1)
postgres_url = parts[0] + '/postgres'

print("=" * 60)
print("POSTGRESQL DATABASES")
print("=" * 60)
print(f"\nConnecting to: {parts[0]}/...")

try:
    # Connect to postgres database
    engine = create_engine(postgres_url)
    
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                datname as "Database",
                pg_size_pretty(pg_database_size(datname)) as "Size"
            FROM pg_database
            WHERE datistemplate = false
            ORDER BY datname;
        """))
        
        print(f"\n{'Database':<30} {'Size':<15}")
        print("-" * 45)
        
        for row in result:
            print(f"{row[0]:<30} {row[1]:<15}")
    
    print("\n" + "=" * 60)
    print(f"Current project database: {parts[1]}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Check if PostgreSQL is running")
    print("2. Verify DATABASE_URL in .env file")
    print("3. Ensure credentials are correct")
