"""Check and fix alembic version"""
from sqlalchemy import create_engine, text

engine = create_engine('postgresql://postgres:password123@host.docker.internal:5432/erp_quty_karunia')

with engine.connect() as conn:
    # Check current version
    result = conn.execute(text('SELECT * FROM alembic_version'))
    rows = list(result)
    print("Current alembic version:", rows)
    
    # Update to 5e9925f3de45 (latest before our new migration)
    if rows and rows[0][0] == '511adb66c9c5':
        print("\nUpdating alembic version from 511adb66c9c5 to 5e9925f3de45...")
        conn.execute(text("UPDATE alembic_version SET version_num = '5e9925f3de45'"))
        conn.commit()
        print("✅ Updated!")
    else:
        print("No update needed")
