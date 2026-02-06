"""Check password hash lengths for all users"""
from app.core.database import SessionLocal
from app.core.models.users import User
from app.core.security import PasswordUtils

db = SessionLocal()

users = db.query(User).all()

print(f"🔍 Checking {len(users)} user password hashes\n")
print("="*100)

invalid_users = []

for user in users:
    hash_len = len(user.hashed_password)
    # Valid bcrypt hash should be 60 chars: $2b$10$ (7) + 22 salt + 31 checksum
    is_valid = hash_len == 60
    
    status = "✅" if is_valid else "❌"
    print(f"{status} {user.username:20s} | Length: {hash_len:3d} | Hash: {user.hashed_password[:30]}...")
    
    if not is_valid:
        invalid_users.append(user)

print("="*100)

if invalid_users:
    print(f"\n⚠️ Found {len(invalid_users)} users with INVALID password hashes:")
    for user in invalid_users:
        print(f"   - {user.username} (length: {len(user.hashed_password)})")
    