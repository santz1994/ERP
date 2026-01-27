"""FastAPI Dependencies
Reusable dependency injection for routes.

ACCESS CONTROL STRATEGY (Session 13.1 - Week 3):
==================================================

✅ PRIMARY: PBAC (Permission-Based Access Control)
   - Use: require_permission('module.action')
   - Granular control: specific actions per user
   - Redis cached (5-min TTL)
   - Example: require_permission('cutting.create_wo')

🔄 FALLBACK: RBAC (Role-Based Access Control)
   - Use: require_role('role_name') or require_any_role()
   - Backward compatible for legacy endpoints
   - Example: require_role('admin')

🚫 BYPASS ROLES (full system access):
   - UserRole.DEVELOPER: System development & debugging
   - UserRole.SUPERADMIN: System administration

MIGRATION PATH:
   - New endpoints: Use require_permission() (PBAC)
   - Legacy endpoints: Keep require_role() until migration
   - Mixed: Use require_any_permission() for OR logic
"""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.models.users import User, UserRole
from app.core.security import TokenUtils
from app.services.permission_service import get_permission_service


# Database session dependency
def get_db() -> Generator[Session, None, None]:
    """Database session dependency
    Provides SQLAlchemy session to routes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# HTTP Bearer token scheme
security = HTTPBearer()


async def get_current_user(
    token: str = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token.

    Args:
        token: HTTP Bearer token
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If token invalid or user not found

    """
    # For FastAPI 0.95.1 compatibility, extract token from security scheme
    actual_token = token.credentials if hasattr(token, 'credentials') else token

    # Decode token
    token_data = TokenUtils.decode_token(actual_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_optional_user(
    token: str | None = Depends(security),
    db: Session = Depends(get_db)
) -> User | None:
    """Get current user (optional, returns None if not authenticated)."""
    if not token:
        return None

    return await get_current_user(token, db)


def require_role(required_role: str):
    """Dependency to require specific role.

    Args:
        required_role: Role name required (e.g., "admin", "ppic_manager")

    Returns:
        Async function that validates role

    **Example**:
    ```python
    @router.get("/admin-only")
    def admin_endpoint(user: User = Depends(require_role("admin"))):
        return {"message": "Admin only endpoint"}
    ```

    """
    async def check_role(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has required role."""
        user_role = current_user.role.value

        if user_role == "Admin" or user_role == required_role:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{required_role}' is required. Your role: {user_role}"
        )

    return check_role


def require_any_role(*allowed_roles: str):
    """Dependency to require any of multiple roles.

    Args:
        allowed_roles: Role names allowed (e.g., "admin", "ppic_manager")

    Returns:
        Async function that validates role

    **Example**:
    ```python
    @router.post("/create-order")
    def create_order(
        user: User = Depends(require_any_role("ppic_manager", "admin"))
    ):
        return {"message": "Order created"}
    ```

    """
    async def check_any_role(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has any allowed role."""
        user_role = current_user.role.value

        if user_role == "Admin":
            return current_user

        for allowed_role in allowed_roles:
            if user_role == allowed_role:
                return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of these roles is required: {', '.join(allowed_roles)}. Your role: {user_role}"
        )

    return check_any_role


def require_roles(allowed_roles: list[UserRole]):
    """Dependency to require any role from UserRole enum list.

    Args:
        allowed_roles: List of UserRole enums allowed

    Returns:
        Async function that validates role

    **Example**:
    ```python
    from app.core.role_requirements import EndpointRoleRequirements

    @router.post("/create-order")
    def create_order(
        user: User = Depends(require_roles(EndpointRoleRequirements.PPIC_CREATE))
    ):
        return {"message": "Order created"}
    ```

    """
    async def check_roles(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has any of the allowed roles."""
        if current_user.role in allowed_roles:
            return current_user

        # Format role names for error message
        role_names = [role.value for role in allowed_roles]

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required roles: {', '.join(role_names)}. Your role: {current_user.role.value}"
        )

    return check_roles


def require_permission(permission_code: str = None, permission_type: str = None):
    """PBAC Dependency: Require specific permission code.

    NEW in Week 3 - Replaces role-based access with fine-grained permissions

    Args:
        permission_code: Permission code (e.g., "cutting.create_wo", "admin.manage_users")
                        OR ModuleName enum (for backward compatibility)
        permission_type: Permission enum (VIEW, CREATE, etc.) - for backward compatibility only

    Returns:
        Async function that validates permission via PermissionService

    **Example (new format)**:
    ```python
    @router.post("/cutting/work-orders")
    def create_work_order(
        user: User = Depends(require_permission("cutting.create_wo")),
        db: Session = Depends(get_db)
    ):
        return {"message": "Work order created"}
    ```

    **Example (old format - backward compatible)**:
    ```python
    @router.post("/cutting/work-orders")
    def create_work_order(
        user: User = Depends(require_permission(ModuleName.CUTTING, Permission.CREATE)),
        db: Session = Depends(get_db)
    ):
        return {"message": "Work order created"}
    ```

    **Benefits**:
    - Fine-grained access control (specific actions, not just roles)
    - Redis caching (5-minute TTL for performance)
    - Role hierarchy support (supervisors can perform operator actions)
    - Custom user permissions (temporary elevated access)

    """
    # Backward compatibility: convert old format to new format
    if permission_type is not None:
        # Old format: require_permission(ModuleName.X, Permission.Y)
        module_name = str(permission_code.value if hasattr(permission_code, 'value') else permission_code).lower()
        perm_name = str(permission_type.value if hasattr(permission_type, 'value') else permission_type).lower()
        final_permission_code = f"{module_name}.{perm_name}"
    else:
        # New format: require_permission("module.action")
        final_permission_code = permission_code

    async def check_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check if user has required permission."""
        perm_service = get_permission_service()

        # Check permission with caching
        if perm_service.has_permission(db, current_user, final_permission_code):
            return current_user

        # Permission denied
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required: {final_permission_code}. User: {current_user.username} ({current_user.role.value})"
        )

    return check_permission


def require_any_permission(permission_codes: list[str]):
    """PBAC Dependency: Require ANY of the specified permissions (OR logic).

    Args:
        permission_codes: List of permission codes

    Returns:
        Async function that validates if user has at least one permission

    **Example**:
    ```python
    @router.get("/production/work-orders")
    def list_work_orders(
        user: User = Depends(require_any_permission([
            "cutting.view_wo",
            "sewing.view_wo",
            "finishing.view_wo"
        ])),
        db: Session = Depends(get_db)
    ):
        return {"work_orders": [...]}
    ```

    """
    async def check_any_permission(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        """Check if user has any of the required permissions."""
        perm_service = get_permission_service()

        if perm_service.has_any_permission(db, current_user, permission_codes):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Insufficient permissions. Required one of: {', '.join(permission_codes)}"
        )

    return check_any_permission


def require_supervisor_or_admin():
    """Require supervisor or admin role."""
    async def check_supervisor(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_supervisor() or current_user.role.value == "Admin":
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor or Admin role required"
        )

    return check_supervisor


def require_operator():
    """Require operator role."""
    async def check_operator(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_operator() or current_user.role.value == "Admin":
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operator role required"
        )

    return check_operator


# Pagination dependency
class PaginationParams:
    """Pagination parameters."""

    def __init__(self, skip: int = 0, limit: int = 100):
        self.skip = max(0, skip)
        self.limit = min(limit, 1000)  # Max 1000 items per page


def get_pagination(
    skip: int = 0,
    limit: int = 100
) -> PaginationParams:
    """Pagination dependency."""
    return PaginationParams(skip=skip, limit=limit)


async def get_current_user_ws(token: str) -> User:
    """Get current authenticated user from JWT token (WebSocket version)
    Used in WebSocket endpoints where we can't use HTTPBearer.

    Args:
        token: JWT token string

    Returns:
        User object

    Raises:
        HTTPException: If token invalid or user not found

    """
    from app.core.database import SessionLocal

    # Decode token
    token_data = TokenUtils.decode_token(token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    # Get user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == token_data.user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )

        return user
    finally:
        db.close()


async def check_permission(user: User, module: str, action: str, db: Session) -> None:
    """Check permission for user action on module.
    
    Args:
        user: Current user
        module: Module name (PPIC, PRODUCTION, WAREHOUSE, etc.)
        action: Action type (INPUT, VIEW, EDIT, COMPLETE, APPROVE, etc.)
        db: Database session
        
    Raises:
        HTTPException: If permission denied
    """
    from app.core.permissions import ModuleName, Permission, AccessControl
    
    try:
        # Map string to enum values
        module_enum = ModuleName[module.upper()]
        permission_enum = Permission[action.upper()]
        
        # Check permission
        AccessControl.check_permission(user, module_enum, permission_enum)
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid module or action: {e}"
        )
