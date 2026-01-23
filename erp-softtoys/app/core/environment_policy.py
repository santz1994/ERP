"""Environment-Aware Permission Enforcement
Restricts DEVELOPER role to read-only in production

ISO 27001 A.12.1.2: Segregation of Duties
SOX 404: Production Access Control
"""
from fastapi import HTTPException, status

from app.core.config import Environment, settings
from app.core.models.users import User, UserRole
from app.core.permissions import Permission


class EnvironmentAccessControl:
    """Environment-aware access control

    Rules:
    1. DEVELOPER role is READ-ONLY in PRODUCTION environment
    2. DEVELOPER can CREATE/UPDATE/DELETE in DEVELOPMENT and TESTING
    3. Other roles are not affected by environment
    """

    # Permissions allowed for DEVELOPER in PRODUCTION
    DEVELOPER_PRODUCTION_PERMISSIONS = {
        Permission.VIEW,
        # DEVELOPER cannot CREATE, UPDATE, DELETE, APPROVE, EXECUTE in production
    }

    @staticmethod
    def is_developer_in_production(user: User) -> bool:
        """Check if user is DEVELOPER role in PRODUCTION environment"""
        return (
            user.role == UserRole.DEVELOPER and
            settings.ENVIRONMENT == Environment.PRODUCTION
        )

    @staticmethod
    def is_permission_allowed(user: User, permission: Permission) -> bool:
        """Check if permission is allowed based on environment

        Returns:
            True if permission allowed, False otherwise

        """
        # Non-DEVELOPER roles are not restricted by environment
        if user.role != UserRole.DEVELOPER:
            return True

        # DEVELOPER in non-production environments has full access
        if settings.ENVIRONMENT != Environment.PRODUCTION:
            return True

        # DEVELOPER in production is restricted to VIEW only
        return permission in EnvironmentAccessControl.DEVELOPER_PRODUCTION_PERMISSIONS

    @staticmethod
    def enforce_environment_restriction(user: User, permission: Permission):
        """Raise exception if permission not allowed

        Raises:
            HTTPException: 403 Forbidden if DEVELOPER tries write operation in production

        """
        if not EnvironmentAccessControl.is_permission_allowed(user, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "Environment Access Restriction",
                    "message": f"DEVELOPER role is READ-ONLY in PRODUCTION environment. {permission.value} operation not allowed.",
                    "current_environment": settings.ENVIRONMENT.value,
                    "user_role": user.role.value,
                    "attempted_permission": permission.value,
                    "allowed_permissions": ["VIEW"],
                    "help": "Use DEVELOPMENT or TESTING environment for write operations, or request elevated role access."
                }
            )


def enforce_environment_policy(user: User, permission: Permission):
    """Wrapper function for environment policy enforcement

    Usage in API endpoints:
        @router.post("/resource")
        def create_resource(user: User = Depends(get_current_user)):
            enforce_environment_policy(user, Permission.CREATE)
            # ... rest of endpoint logic
    """
    EnvironmentAccessControl.enforce_environment_restriction(user, permission)


def get_environment_info():
    """Get current environment information

    Returns:
        dict: Environment details including restrictions

    """
    return {
        "environment": settings.ENVIRONMENT.value,
        "developer_restrictions_active": settings.ENVIRONMENT == Environment.PRODUCTION,
        "developer_allowed_permissions": [
            perm.value for perm in EnvironmentAccessControl.DEVELOPER_PRODUCTION_PERMISSIONS
        ] if settings.ENVIRONMENT == Environment.PRODUCTION else ["all"],
        "developer_blocked_permissions": [
            Permission.CREATE.value,
            Permission.UPDATE.value,
            Permission.DELETE.value,
            Permission.APPROVE.value,
            Permission.EXECUTE.value
        ] if settings.ENVIRONMENT == Environment.PRODUCTION else []
    }
