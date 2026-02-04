"""Test password verification"""
from app.core.database import SessionLocal
from app.core.models import User
from app.core.security import PasswordUtils

db = SessionLocal()

# Get admin user
admin = db.query(User).filter(User.username == 'admin').first()

if admin:
    print(f'✅ Found admin: {admin.username}')
    print(f'   Stored hash: {admin.hashed_password[:60]}...')
    
    # Test password verification
    test_password = "admin123"
    is_valid = PasswordUtils.verify_password(test_password, admin.hashed_password)
    
    print(f'\n🔐 Testing password: "{test_password}"')
    print(f'   Result: {"✅ VALID" if is_valid else "❌ INVALID"}')
    
    # Try creating new hash for comparison
    new_hash = PasswordUtils.hash_password(test_password)
    print(f'\n🆕 New hash for "{test_password}":')
    print(f'   {new_hash[:60]}...')
else:
    print('❌ Admin not found')

db.close()
