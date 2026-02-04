"""Direct test login logic"""
from datetime import datetime, timedelta
from app.core.database import SessionLocal
from app.core.models import User
from app.core.security import PasswordUtils, TokenUtils
from app.core.schemas import UserResponse, AuthResponse

db = SessionLocal()

# Find user
credentials_username = "admin"
credentials_password = "admin123"

user = db.query(User).filter(
    (User.username == credentials_username) | (User.email == credentials_username)
).first()

if not user:
    print("❌ User not found")
    exit()

print(f"✅ User found: {user.username}")

# Verify password
if not PasswordUtils.verify_password(credentials_password, user.hashed_password):
    print("❌ Password invalid")
    exit()

print("✅ Password valid")

# Reset login attempts
user.login_attempts = 0
user.locked_until = None
user.last_login = datetime.utcnow()

# Get role
role_name = user.role.value if hasattr(user.role, 'value') else str(user.role)
print(f"✅ Role: {role_name} (type: {type(role_name)})")

# Generate tokens
try:
    access_token = TokenUtils.create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        roles=[role_name]
    )
    print(f"✅ Access token generated: {access_token[:50]}...")
except Exception as e:
    print(f"❌ Token generation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit()

try:
    refresh_token = TokenUtils.create_refresh_token(
        user_id=user.id,
        username=user.username
    )
    print(f"✅ Refresh token generated: {refresh_token[:50]}...")
except Exception as e:
    print(f"❌ Refresh token generation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit()

# Create UserResponse
try:
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        role=user.role.value if hasattr(user.role, 'value') else str(user.role),
        is_active=user.is_active,
        created_at=user.created_at
    )
    print(f"✅ UserResponse created")
    print(f"   ID: {user_response.id}")
    print(f"   Username: {user_response.username}")
    print(f"   Role: {user_response.role}")
except Exception as e:
    print(f"❌ UserResponse creation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit()

# Create AuthResponse
try:
    auth_response = AuthResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=24 * 3600,
        user=user_response
    )
    print(f"✅ AuthResponse created successfully!")
    print(f"   Token type: {auth_response.token_type}")
    print(f"   Expires in: {auth_response.expires_in}s")
except Exception as e:
    print(f"❌ AuthResponse creation failed: {str(e)}")
    import traceback
    traceback.print_exc()
    exit()

db.commit()
db.close()

print("\n🎉 ALL CHECKS PASSED! Login logic works.")
