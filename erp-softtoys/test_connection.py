import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
try:
    db_url = os.getenv('DATABASE_URL', 'postgresql://postgres:password123@localhost:5432/erp_quty_karunia')
    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT version();')
            version = cur.fetchone()[0]
            print(f"âœ… PostgreSQL Connected: {version[:50]}")
except Exception as e:
    print(f"âŒ Connection Failed: {e}")
    exit(1)
