"""Update admin password via SQL"""
from sqlalchemy import text
from app.core.database import engine
from app.core.security import PasswordUtils

# Generate correct hash
correct_hash = PasswordUtils.hash_password("admin123")
print(f'✅ Generated hash: {correct_hash}')
print(f'   Length: {len(correct_hash)} chars')

# Update via SQL
with engine.connect() as conn:
    result = conn.execute(
        text("UPDATE users SET hashed_password = :hash, login_attempts = 0, locked_until = NULL WHERE username = 'admin'"),
        {"hash": correct_hash}
    )
    conn.commit()
    print(f'\n✅ Updated {result.rowcount} row(s)')
    
    # Verify
    verify = conn.execute(
        text("SELECT username, hashed_password, role, is_active FROM users WHERE username = 'admin'")
    ).fetchone()
    
    if verify:
        print(f'\n📋 Admin user verified:')
        print(f'   Username: {verify[0]}')
        print(f'   Hash (first 40 chars): {verify[1][:40]}...')
        print(f'   Role: {verify[2]}')
        print(f'   Active: {verify[3]}')
    
print('\n✅ Admin password reset complete!')
print('   Username: admin')
print('   Password: admin123')
