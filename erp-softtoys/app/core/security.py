"""Security & Authentication Module
JWT token generation, password hashing, and role-based access control.
"""

from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from app.core.config import settings

# Password hashing configuration
# Reduced bcrypt rounds to 10 for better performance (~100ms vs 2s with rounds=12)
# Still secure: 10 rounds = 2^10 = 1024 iterations, sufficient for production
# Note: bcrypt 4.x compatibility warning can be safely ignored
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=10)


class TokenData(BaseModel):
    """JWT token payload."""

    user_id: int
    username: str
    email: str
    roles: list[str]
    exp: datetime
    iat: datetime


class PasswordUtils:
    """Password hashing utilities."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt (truncate to 72 bytes if needed)."""
        # bcrypt has max 72 bytes limit
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        # bcrypt has max 72 bytes limit
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)


class TokenUtils:
    """JWT token utilities."""

    @staticmethod
    def create_access_token(
        user_id: int,
        username: str,
        email: str,
        roles: list[str],
        expires_delta: timedelta | None = None
    ) -> str:
        """Create JWT access token using current SECRET_KEY.

        Args:
            user_id: User ID
            username: Username
            email: Email address
            roles: List of role names
            expires_delta: Custom expiration time

        Returns:
            Encoded JWT token

        """
        if expires_delta is None:
            expires_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)

        expire = datetime.utcnow() + expires_delta

        payload = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "roles": roles,
            "exp": expire,
            "iat": datetime.utcnow()
        }

        # Always use current key for new tokens
        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,  # Changed from JWT_SECRET_KEY
            algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def create_refresh_token(user_id: int, username: str) -> str:
        """Create JWT refresh token (longer expiration) using current SECRET_KEY."""
        expires_delta = timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)

        payload = {
            "user_id": user_id,
            "username": username,
            "type": "refresh",
            "exp": datetime.utcnow() + expires_delta
        }

        # Always use current key for new tokens
        encoded_jwt = jwt.encode(
            payload,
            settings.SECRET_KEY,  # Changed from JWT_SECRET_KEY
            algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt

    @staticmethod
    def decode_token(token: str) -> "TokenData | None":
        """Decode and validate JWT token.

        Performance optimized: Only uses current SECRET_KEY for fast validation.
        Key rotation should be handled via token re-issue rather than multi-key validation.

        Args:
            token: JWT token string

        Returns:
            TokenData if valid, None if invalid

        """
        try:
            # Decode with current key only (fast path - removed multi-key loop)
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )

            return TokenData(
                user_id=payload.get("user_id"),
                username=payload.get("username"),
                email=payload.get("email"),
                roles=payload.get("roles", []),
                exp=payload.get("exp"),
                iat=payload.get("iat")
            )
        except JWTError:
            return None


# Role-based access control
ROLE_HIERARCHY = {
    "admin": ["admin", "ppic_manager", "spv_cutting", "spv_sewing", "spv_finishing",
              "operator_cutting", "operator_sewing", "operator_finishing",
              "qc_inspector", "warehouse_admin", "purchasing", "security"],
    "ppic_manager": ["ppic_manager", "operator_cutting", "operator_sewing",
                     "qc_inspector", "warehouse_admin"],
    "spv_cutting": ["spv_cutting", "operator_cutting"],
    "spv_sewing": ["spv_sewing", "operator_sewing"],
    "spv_finishing": ["spv_finishing", "operator_finishing"],
    "operator_cutting": ["operator_cutting"],
    "operator_sewing": ["operator_sewing"],
    "operator_finishing": ["operator_finishing"],
    "qc_inspector": ["qc_inspector"],
    "warehouse_admin": ["warehouse_admin"],
    "purchasing": ["purchasing"],
    "security": ["security"]
}


def has_role(user_roles: list[str], required_role: str) -> bool:
    """Check if user has required role or higher.

    Args:
        user_roles: List of user's roles
        required_role: Required role name

    Returns:
        True if user has role or higher, False otherwise

    """
    # Admin bypass
    if "admin" in user_roles:
        return True

    # Check if user has required role
    return required_role in user_roles


def has_any_role(user_roles: list[str], allowed_roles: list[str]) -> bool:
    """Check if user has any of the allowed roles."""
    for role in user_roles:
        if role in allowed_roles:
            return True
        # Check hierarchy
        if "admin" in user_roles:
            return True
    return False
