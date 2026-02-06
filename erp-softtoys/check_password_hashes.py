"""Check password hashes in database"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.core.models import User

db = SessionLocal()

print("=" * 100)
print("🔍 CHECKING PASSWORD HASHES IN DATABASE")
print("=" * 100)

users = db.query(User).order_by(User.username).all()

print(f"\nTotal users: {len(users)}\n")

for user in users:
    hash_val = user.hashed_password
    hash_len = len(hash_val)
    
    # Valid bcrypt hash format: $2b$10$ + 53 chars = 60 total
    is_valid = hash_len == 60 and hash_val.startswith("$2b$")
    status = "✅ VALID" if is_valid else "❌ INVALID"
    
    print(f"{status} | {user.username:20s} | Length: {hash_len:3d} | Hash: {hash_val[:30]}...")

db.close()

print("\n" + "=" * 100)
print("📊 SUMMARY")
print("=" * 100)

db = SessionLocal()
valid_count = sum(1 for u in db.query(User).all() if len(u.hashed_password) == 60)
total_count = db.query(User).count()
db.close()

print(f"Valid hashes: {valid_count}/{total_count}")

if valid_count < total_count:
    print(f"\n⚠️  {total_count - valid_count} users have INVALID password hashes!")
    print("\nFix needed: Regenerate password hashes with correct bcrypt format")
else:
    print("\n✅ All password hashes are valid format!")
