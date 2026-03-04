"""Debug login endpoint step by step."""
import sys
import traceback

sys.path.insert(0, '.')

# Redirect verbose startup output
import logging
logging.disable(logging.CRITICAL)

try:
    from app.core.database import SessionLocal
    from app.core.models.users import User
    from app.core.security import PasswordUtils, TokenUtils
    from app.api.v1.auth import AuthResponse, UserResponse

    db = SessionLocal()
    print("STEP 1: DB connected")

    user = db.query(User).first()
    if not user:
        print("ERROR: No users in database")
        sys.exit(1)
    print(f"STEP 2: User={user.username}, role_type={type(user.role).__name__}, role={user.role}")

    role_name = user.role.value
    print(f"STEP 3: role_name={role_name!r}")

    token = TokenUtils.create_access_token(
        user_id=user.id,
        username=user.username,
        email=user.email,
        roles=[role_name]
    )
    print(f"STEP 4: Token OK ({len(token)} chars)")

    refresh = TokenUtils.create_refresh_token(user_id=user.id, username=user.username)
    print(f"STEP 5: Refresh token OK")

    resp = AuthResponse(
        access_token=token,
        refresh_token=refresh,
        token_type="bearer",
        expires_in=86400,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )
    print(f"STEP 6: AuthResponse built OK")
    import json
    d = resp.dict()
    print(f"STEP 7: Serialization OK — user role in response: {d['user']['role']}")
    db.close()
    print("\nLOGIN SIMULATION: ALL STEPS PASSED")

except Exception:
    traceback.print_exc()
    try:
        db.close()
    except Exception:
        pass
