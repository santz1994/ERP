"""Test password verification directly with bcrypt"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.security import PasswordUtils, pwd_context
from app.core.database import SessionLocal
from app.core.models import User

print("=" * 80)
print("🧪 TESTING PASSWORD VERIFICATION")
print("=" * 80)

# Test 1: Direct bcrypt test
print("\n1. Testing bcrypt directly:")
test_password = "admin123"
test_hash = PasswordUtils.hash_password(test_password)
print(f"   Password: {test_password}")
print(f"   Hash: {test_hash[:50]}...")
print(f"   Hash length: {len(test_hash)}")

try:
    result = pwd_context.verify(test_password, test_hash)
    print(f"   ✅ Verification: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Using PasswordUtils
print("\n2. Testing PasswordUtils.verify_password:")
try:
    result = PasswordUtils.verify_password(test_password, test_hash)
    print(f"   ✅ Verification: {result}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Test with actual database hash
print("\n3. Testing with database hash (admin user):")
db = SessionLocal()
admin_user = db.query(User).filter(User.username == "admin").first()

if admin_user:
    print(f"   Username: {admin_user.username}")
    print(f"   Hash from DB: {admin_user.hashed_password[:50]}...")
    print(f"   Hash length: {len(admin_user.hashed_password)}")
    
    try:
        result = PasswordUtils.verify_password("admin123", admin_user.hashed_password)
        print(f"   ✅ Verification with 'admin123': {result}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("   ❌ Admin user not found in database")

db.close()

# Test 4: Check if hash is valid bcrypt format
print("\n4. Checking if database hashes are valid bcrypt format:")
db = SessionLocal()
users = db.query(User).limit(3).all()

for user in users:
    hash_val = user.hashed_password
    
    # Try to verify with the hash itself (should fail gracefully)
    print(f"\n   User: {user.username}")
    print(f"   Hash: {hash_val[:50]}...")
    
    # Check format
    if hash_val.startswith("$2b$") and len(hash_val) == 60:
        print(f"   ✅ Format: Valid bcrypt hash")
    else:
        print(f"   ❌ Format: INVALID (len={len(hash_val)})")
    
    # Try verification
    try:
        # This should return False (wrong password), not error
        result = pwd_context.verify("wrongpassword", hash_val)
        print(f"   ℹ️  Verify with wrong password: {result} (expected: False)")
    except Exception as e:
        print(f"   ❌ Verification error: {e}")

db.close()

print("\n" + "=" * 80)
