"""Permission Service for PBAC (Permission-Based Access Control)
Provides efficient permission checking with Redis caching and role hierarchy support.

Session 13.1 - Week 3: PBAC Implementation
"""

import json
import logging

import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.models.users import User, UserRole

logger = logging.getLogger(__name__)


class PermissionService:
    """Centralized permission checking service with caching
    Supports PBAC with role hierarchy and custom permissions.
    """

    def __init__(self, redis_client: redis.Redis | None = None):
        """Initialize PermissionService with optional Redis caching.

        Args:
            redis_client: Redis connection for caching (optional)

        """
        self.redis_client = redis_client
        self.cache_ttl = 300  # 5 minutes cache TTL

        # Role hierarchy: higher roles inherit permissions from lower roles
        # 22 roles total (Session 13.1 - PBAC Implementation)
        self.role_hierarchy = {
            # Level 0: System Development (bypass all checks in has_permission)
            UserRole.DEVELOPER: [UserRole.DEVELOPER],

            # Level 1: System Administration (bypass all checks in has_permission)
            UserRole.SUPERADMIN: [UserRole.SUPERADMIN],

            # Level 2: Top Management (Approvers - inherit all operational permissions)
            UserRole.MANAGER: [UserRole.MANAGER],
            UserRole.FINANCE_MANAGER: [UserRole.FINANCE_MANAGER],

            # Level 3: System Admin (inherits all operational permissions)
            UserRole.ADMIN: [UserRole.ADMIN],

            # Level 4: Department Management
            UserRole.PPIC_MANAGER: [UserRole.PPIC_MANAGER, UserRole.PPIC_ADMIN],
            UserRole.PPIC_ADMIN: [UserRole.PPIC_ADMIN],
            UserRole.SPV_CUTTING: [UserRole.SPV_CUTTING, UserRole.OPERATOR_CUT, UserRole.OPERATOR_EMBRO],
            UserRole.SPV_SEWING: [UserRole.SPV_SEWING, UserRole.OPERATOR_SEW],
            UserRole.SPV_FINISHING: [UserRole.SPV_FINISHING, UserRole.OPERATOR_FINISH, UserRole.OPERATOR_PACK],
            UserRole.WAREHOUSE_ADMIN: [UserRole.WAREHOUSE_ADMIN, UserRole.WAREHOUSE_OP],
            UserRole.QC_LAB: [UserRole.QC_LAB, UserRole.QC_INSPECTOR],
            UserRole.PURCHASING_HEAD: [UserRole.PURCHASING_HEAD, UserRole.PURCHASING],
            UserRole.PURCHASING: [UserRole.PURCHASING],

            # Level 5: Operations (no inheritance)
            UserRole.OPERATOR_CUT: [UserRole.OPERATOR_CUT],
            UserRole.OPERATOR_EMBRO: [UserRole.OPERATOR_EMBRO],
            UserRole.OPERATOR_SEW: [UserRole.OPERATOR_SEW],
            UserRole.OPERATOR_FINISH: [UserRole.OPERATOR_FINISH],
            UserRole.OPERATOR_PACK: [UserRole.OPERATOR_PACK],
            UserRole.QC_INSPECTOR: [UserRole.QC_INSPECTOR],
            UserRole.WAREHOUSE_OP: [UserRole.WAREHOUSE_OP],
            UserRole.SECURITY: [UserRole.SECURITY]
        }

    def _get_cache_key(self, user_id: int, permission_code: str) -> str:
        """Generate Redis cache key for permission check."""
        return f"pbac:user:{user_id}:perm:{permission_code}"

    def _get_user_permissions_cache_key(self, user_id: int) -> str:
        """Generate Redis cache key for user's all permissions."""
        return f"pbac:user:{user_id}:all_perms"

    def _check_cache(self, cache_key: str) -> bool | None:
        """Check Redis cache for permission result.

        Returns:
            True if allowed, False if denied, None if not cached

        """
        if not self.redis_client:
            return None

        try:
            cached_value = self.redis_client.get(cache_key)
            if cached_value:
                return cached_value.decode() == "1"
        except Exception as e:
            logger.warning(f"Redis cache read failed: {e}")

        return None

    def _set_cache(self, cache_key: str, value: bool):
        """Store permission check result in Redis cache."""
        if not self.redis_client:
            return

        try:
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                "1" if value else "0"
            )
        except Exception as e:
            logger.warning(f"Redis cache write failed: {e}")

    def get_effective_roles(self, user_role: UserRole) -> list[UserRole]:
        """Get all roles that this user effectively has (including inherited).

        Example: SPV_CUTTING can also perform OPERATOR_CUTTING actions
        """
        return self.role_hierarchy.get(user_role, [user_role])

    def get_user_permissions_from_db(
        self,
        db: Session,
        user_id: int
    ) -> set[str]:
        """Fetch all permissions for a user from database
        Combines role-based + custom user permissions.

        Returns:
            Set of permission codes (e.g., {"cutting.create_wo", "admin.view_users"})

        """
        # Query permissions from PBAC tables
        query = text("""
            SELECT DISTINCT p.code
            FROM permissions p
            LEFT JOIN role_permissions rp ON p.id = rp.permission_id
            LEFT JOIN user_custom_permissions ucp ON p.id = ucp.permission_id
            LEFT JOIN users u ON u.role = rp.role OR u.id = ucp.user_id
            WHERE u.id = :user_id
              AND u.is_active = TRUE
              AND (
                  rp.is_granted = TRUE
                  OR (ucp.is_granted = TRUE AND (ucp.expires_at IS NULL OR ucp.expires_at > NOW()))
              )
        """)

        result = db.execute(query, {"user_id": user_id})
        permissions = {row[0] for row in result.fetchall()}

        return permissions

    def _map_permission_code_to_role_permissions(
        self, permission_code: str
    ) -> tuple[str | None, str | None]:
        """Convert permission code to (module, permission) for ROLE_PERMISSIONS lookup.
        
        Args:
            permission_code: Permission code in format "module.action"
        
        Returns:
            Tuple of (ModuleName enum name, Permission enum name) or (None, None)
        """
        # Parse permission code: "admin.manage_users" -> ("admin", "manage_users")
        if '.' not in permission_code:
            return permission_code, None
        
        module_str, action_str = permission_code.split('.', 1)
        
        # Map module string to ModuleName enum
        module_mapping = {
            'dashboard': 'DASHBOARD',
            'ppic': 'PPIC',
            'purchasing': 'PURCHASING',
            'warehouse': 'WAREHOUSE',
            'cutting': 'CUTTING',
            'embroidery': 'EMBROIDERY',
            'sewing': 'SEWING',
            'finishing': 'FINISHING',
            'packing': 'PACKING',
            'finishgoods': 'FINISHGOODS',
            'qc': 'QC',
            'kanban': 'KANBAN',
            'reports': 'REPORTS',
            'admin': 'ADMIN',
            'import_export': 'IMPORT_EXPORT',
            'masterdata': 'MASTERDATA',
            'audit': 'AUDIT',
            'barcode': 'BARCODE'
        }
        
        # Map action to Permission enum
        action_mapping = {
            'view': 'VIEW',
            'view_logs': 'VIEW',
            'view_summary': 'VIEW',
            'view_security_logs': 'VIEW',
            'view_user_activity': 'VIEW',
            'create': 'CREATE',
            'create_wo': 'CREATE',
            'create_mo': 'CREATE',
            'manage_users': 'UPDATE',
            'manage_permissions': 'UPDATE',
            'manage_system': 'UPDATE',
            'update': 'UPDATE',
            'delete': 'DELETE',
            'approve': 'APPROVE',
            'approve_mo': 'APPROVE',
            'execute': 'EXECUTE',
            'refresh_views': 'CREATE',
            'export_logs': 'CREATE',
            'schedule_production': 'VIEW',
            'request_material': 'CREATE',
            'approve_material': 'APPROVE'
        }
        
        module_enum_name = module_mapping.get(module_str.lower())
        perm_enum_name = action_mapping.get(action_str.lower(), 'VIEW')
        
        return module_enum_name, perm_enum_name

    def has_permission(
        self,
        db: Session,
        user: User,
        permission_code: str,
        use_cache: bool = True
    ) -> bool:
        """Check if user has a specific permission.

        Args:
            db: Database session
            user: User object
            permission_code: Permission code (e.g., "cutting.create_wo")
            use_cache: Whether to use Redis cache (default: True)

        Returns:
            True if user has permission, False otherwise

        """
        # Check cache first
        cache_key = None
        if use_cache:
            cache_key = self._get_cache_key(int(user.id), permission_code)
            cached_result = self._check_cache(cache_key)
            if cached_result is not None:
                return cached_result

        # SUPERADMIN, DEVELOPER, MANAGER and Admin have all permissions
        user_role = user.role
        if user_role in [UserRole.SUPERADMIN, UserRole.DEVELOPER, 
                         UserRole.ADMIN, UserRole.MANAGER]:
            if use_cache and cache_key:
                self._set_cache(cache_key, True)
            return True

        # Import ROLE_PERMISSIONS from permissions module
        from app.core.permissions import ROLE_PERMISSIONS, ModuleName, Permission
        
        # Map permission code to (module, permission) enums
        module_enum_name, perm_enum_name = self._map_permission_code_to_role_permissions(
            permission_code)
        
        if not module_enum_name or not perm_enum_name:
            if use_cache and cache_key:
                self._set_cache(cache_key, False)
            return False
        
        # Get ModuleName and Permission enums
        try:
            module_enum = ModuleName[module_enum_name]
            perm_enum = Permission[perm_enum_name]
        except (KeyError, ValueError):
            if use_cache and cache_key:
                self._set_cache(cache_key, False)
            return False
        
        # Check if user's role has this permission in ROLE_PERMISSIONS dict
        has_perm = False
        if user_role in ROLE_PERMISSIONS:
            role_perms = ROLE_PERMISSIONS[user_role]
            if module_enum in role_perms:
                has_perm = perm_enum in role_perms[module_enum]

        # Cache the result
        if use_cache and cache_key:
            self._set_cache(cache_key, has_perm)

        return has_perm

    def has_any_permission(
        self,
        db: Session,
        user: User,
        permission_codes: list[str],
        use_cache: bool = True
    ) -> bool:
        """Check if user has ANY of the specified permissions (OR logic).

        Args:
            db: Database session
            user: User object
            permission_codes: List of permission codes
            use_cache: Whether to use Redis cache

        Returns:
            True if user has at least one permission

        """
        for perm_code in permission_codes:
            if self.has_permission(db, user, perm_code, use_cache):
                return True
        return False

    def has_all_permissions(
        self,
        db: Session,
        user: User,
        permission_codes: list[str],
        use_cache: bool = True
    ) -> bool:
        """Check if user has ALL specified permissions (AND logic).

        Args:
            db: Database session
            user: User object
            permission_codes: List of permission codes
            use_cache: Whether to use Redis cache

        Returns:
            True if user has all permissions

        """
        for perm_code in permission_codes:
            if not self.has_permission(db, user, perm_code, use_cache):
                return False
        return True

    def check_role_access(
        self,
        user: User,
        required_roles: list[UserRole]
    ) -> bool:
        """Legacy role-based access check with hierarchy support
        Used during migration period for backward compatibility.

        Args:
            user: User object
            required_roles: List of allowed roles

        Returns:
            True if user's role (or inherited roles) matches any required role

        """
        if not user.is_active:
            return False

        # Get effective roles (including inherited)
        effective_roles = self.get_effective_roles(user.role)

        # Check if any effective role matches required roles
        return any(role in required_roles for role in effective_roles)

    def invalidate_user_cache(self, user_id: int):
        """Invalidate all cached permissions for a user
        Call this when user permissions change.
        """
        if not self.redis_client:
            return

        try:
            # Delete all permission cache keys for this user
            pattern = f"pbac:user:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Invalidated {len(keys)} cache entries for user {user_id}")
        except Exception as e:
            logger.warning(f"Cache invalidation failed: {e}")

    def get_user_all_permissions(
        self,
        db: Session,
        user_id: int,
        use_cache: bool = True
    ) -> list[dict]:
        """Get all permissions for a user (for admin UI).

        Returns:
            List of permission dicts with code, name, module, source

        """
        # Check cache
        if use_cache and self.redis_client:
            cache_key = self._get_user_permissions_cache_key(user_id)
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached.decode())
            except Exception as e:
                logger.warning(f"Cache read failed: {e}")

        # Query from database
        query = text("""
            SELECT DISTINCT
                p.code,
                p.name,
                p.module,
                p.description,
                CASE
                    WHEN rp.role IS NOT NULL THEN 'role'
                    WHEN ucp.user_id IS NOT NULL THEN 'custom'
                    ELSE 'unknown'
                END as source,
                ucp.expires_at
            FROM permissions p
            LEFT JOIN role_permissions rp ON p.id = rp.permission_id
            LEFT JOIN user_custom_permissions ucp ON p.id = ucp.permission_id
            LEFT JOIN users u ON u.role = rp.role OR u.id = ucp.user_id
            WHERE u.id = :user_id
              AND u.is_active = TRUE
              AND (
                  rp.is_granted = TRUE
                  OR (ucp.is_granted = TRUE AND (ucp.expires_at IS NULL OR ucp.expires_at > NOW()))
              )
            ORDER BY p.module, p.code
        """)

        result = db.execute(query, {"user_id": user_id})
        permissions = []
        for row in result.fetchall():
            permissions.append({
                "code": row[0],
                "name": row[1],
                "module": row[2],
                "description": row[3],
                "source": row[4],
                "expires_at": row[5].isoformat() if row[5] else None
            })

        # Cache the result
        if use_cache and self.redis_client:
            try:
                self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(permissions)
                )
            except Exception as e:
                logger.warning(f"Cache write failed: {e}")

        return permissions


# Singleton instance (initialized in dependencies.py)
_permission_service: PermissionService | None = None


def get_permission_service() -> PermissionService:
    """Get global PermissionService instance."""
    global _permission_service
    if _permission_service is None:
        # Initialize without Redis for now (will be configured in startup)
        _permission_service = PermissionService()
    return _permission_service


def init_permission_service(redis_client: redis.Redis | None = None):
    """Initialize PermissionService with Redis client
    Call this during app startup.
    """
    global _permission_service
    _permission_service = PermissionService(redis_client)
    logger.info("PermissionService initialized with Redis caching")
