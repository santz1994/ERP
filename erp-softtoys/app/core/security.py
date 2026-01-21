"""
Security & Authentication Module
JWT token generation, password hashing, and role-based access control
"""

from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from app.core.config import settings


# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenData(BaseModel):
    """JWT token payload"""
    user_id: int
    username: str
    email: str
    roles: list[str]
    exp: datetime
    iat: datetime


class PasswordUtils:
    """Password hashing utilities"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)


class TokenUtils:
    """JWT token utilities"""
    
    @staticmethod
    def create_access_token(
        user_id: int,
        username: str,
        email: str,
        roles: list[str],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create JWT access token using current SECRET_KEY
        
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
        """Create JWT refresh token (longer expiration) using current SECRET_KEY"""
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
    def decode_token(token: str) -> Optional[TokenData]:
        """
        Decode and validate JWT token using current + historical keys
        
        This supports SECRET_KEY rotation with grace period. If token was signed
        with an old key (during rotation period), it will still be validated.
        
        Args:
            token: JWT token string
        
        Returns:
            TokenData if valid, None if invalid
        """
        # Try decoding with current key first (fastest path)
        valid_keys = settings.all_valid_keys
        
        for secret_key in valid_keys:
            try:
                payload = jwt.decode(
                    token,
                    secret_key,
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
                # Try next key in history
                continue
        
        # Token invalid with all keys
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
    """
    Check if user has required role or higher
    
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
    """Check if user has any of the allowed roles"""
    for role in user_roles:
        if role in allowed_roles:
            return True
        # Check hierarchy
        if "admin" in user_roles:
            return True
    return False
