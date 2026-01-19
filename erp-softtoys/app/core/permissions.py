"""
User Access Control (UAC) and Module Permissions System
Role-Based Access Control (RBAC) for ERP modules
"""

from enum import Enum
from typing import List, Set
from fastapi import HTTPException, status
from app.core.models.users import User, UserRole


class ModuleName(str, Enum):
    """ERP Modules"""
    DASHBOARD = "dashboard"
    PPIC = "ppic"
    PURCHASING = "purchasing"
    WAREHOUSE = "warehouse"
    CUTTING = "cutting"
    EMBROIDERY = "embroidery"
    SEWING = "sewing"
    FINISHING = "finishing"
    PACKING = "packing"
    FINISHGOODS = "finishgoods"
    QC = "qc"
    KANBAN = "kanban"
    REPORTS = "reports"
    ADMIN = "admin"
    IMPORT_EXPORT = "import_export"
    MASTERDATA = "masterdata"


class Permission(str, Enum):
    """Access permissions"""
    VIEW = "view"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    APPROVE = "approve"
    EXECUTE = "execute"


# Module Access Control Matrix
# Format: {Role: {Module: [Permissions]}}
ROLE_PERMISSIONS = {
    UserRole.ADMIN: {
        # Admin has full access to all modules
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.PPIC: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.DELETE, Permission.APPROVE],
        ModuleName.PURCHASING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.DELETE, Permission.APPROVE],
        ModuleName.WAREHOUSE: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.DELETE, Permission.EXECUTE],
        ModuleName.CUTTING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.EMBROIDERY: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.SEWING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.FINISHING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.PACKING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.FINISHGOODS: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.QC: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.APPROVE],
        ModuleName.KANBAN: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.APPROVE],
        ModuleName.REPORTS: [Permission.VIEW, Permission.CREATE],
        ModuleName.ADMIN: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.DELETE],
        ModuleName.IMPORT_EXPORT: [Permission.VIEW, Permission.CREATE, Permission.UPDATE],
        ModuleName.MASTERDATA: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.DELETE],
    },
    
    UserRole.PPIC_MANAGER: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.PPIC: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.APPROVE],
        ModuleName.PURCHASING: [Permission.VIEW, Permission.APPROVE],
        ModuleName.WAREHOUSE: [Permission.VIEW],
        ModuleName.CUTTING: [Permission.VIEW],
        ModuleName.EMBROIDERY: [Permission.VIEW],
        ModuleName.SEWING: [Permission.VIEW],
        ModuleName.FINISHING: [Permission.VIEW],
        ModuleName.PACKING: [Permission.VIEW],
        ModuleName.FINISHGOODS: [Permission.VIEW],
        ModuleName.QC: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW, Permission.CREATE],
        ModuleName.MASTERDATA: [Permission.VIEW],
    },
    
    UserRole.PPIC_ADMIN: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.PPIC: [Permission.VIEW, Permission.CREATE, Permission.UPDATE],
        ModuleName.WAREHOUSE: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW, Permission.CREATE],
        ModuleName.MASTERDATA: [Permission.VIEW],
    },
    
    UserRole.PURCHASING: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.PURCHASING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE],
        ModuleName.WAREHOUSE: [Permission.VIEW],
        ModuleName.MASTERDATA: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW],
    },
    
    UserRole.SPV_CUTTING: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.CUTTING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE, Permission.APPROVE],
        ModuleName.WAREHOUSE: [Permission.VIEW],
        ModuleName.QC: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW],
    },
    
    UserRole.SPV_SEWING: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.SEWING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE, Permission.APPROVE],
        ModuleName.EMBROIDERY: [Permission.VIEW],
        ModuleName.QC: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW],
    },
    
    UserRole.SPV_FINISHING: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.FINISHING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE, Permission.APPROVE],
        ModuleName.PACKING: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE],
        ModuleName.QC: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW],
    },
    
    UserRole.OPERATOR_CUT: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.CUTTING: [Permission.VIEW, Permission.EXECUTE],
    },
    
    UserRole.OPERATOR_EMBRO: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.EMBROIDERY: [Permission.VIEW, Permission.EXECUTE],
    },
    
    UserRole.OPERATOR_SEW: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.SEWING: [Permission.VIEW, Permission.EXECUTE],
    },
    
    UserRole.OPERATOR_FINISH: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.FINISHING: [Permission.VIEW, Permission.EXECUTE],
    },
    
    UserRole.OPERATOR_PACK: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.PACKING: [Permission.VIEW, Permission.EXECUTE],
        ModuleName.KANBAN: [Permission.VIEW, Permission.CREATE],
    },
    
    UserRole.QC_INSPECTOR: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.QC: [Permission.VIEW, Permission.CREATE, Permission.UPDATE],
        ModuleName.CUTTING: [Permission.VIEW],
        ModuleName.SEWING: [Permission.VIEW],
        ModuleName.FINISHING: [Permission.VIEW],
        ModuleName.PACKING: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW],
    },
    
    UserRole.QC_LAB: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.QC: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.APPROVE],
        ModuleName.REPORTS: [Permission.VIEW, Permission.CREATE],
    },
    
    UserRole.WAREHOUSE_ADMIN: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.WAREHOUSE: [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.EXECUTE, Permission.APPROVE],
        ModuleName.PURCHASING: [Permission.VIEW],
        ModuleName.FINISHGOODS: [Permission.VIEW, Permission.CREATE, Permission.UPDATE],
        ModuleName.MASTERDATA: [Permission.VIEW, Permission.CREATE, Permission.UPDATE],
        ModuleName.REPORTS: [Permission.VIEW],
        ModuleName.IMPORT_EXPORT: [Permission.VIEW, Permission.CREATE],
    },
    
    UserRole.WAREHOUSE_OP: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.WAREHOUSE: [Permission.VIEW, Permission.EXECUTE],
        ModuleName.FINISHGOODS: [Permission.VIEW],
    },
    
    UserRole.SECURITY: {
        ModuleName.DASHBOARD: [Permission.VIEW],
        ModuleName.FINISHGOODS: [Permission.VIEW],
        ModuleName.REPORTS: [Permission.VIEW],
    },
}


class AccessControl:
    """Access control utility functions"""
    
    @staticmethod
    def has_module_access(user: User, module: ModuleName) -> bool:
        """Check if user has access to a module"""
        if user.role == UserRole.ADMIN:
            return True
        
        role_permissions = ROLE_PERMISSIONS.get(user.role, {})
        return module in role_permissions
    
    @staticmethod
    def has_permission(user: User, module: ModuleName, permission: Permission) -> bool:
        """Check if user has specific permission for a module"""
        if user.role == UserRole.ADMIN:
            return True
        
        role_permissions = ROLE_PERMISSIONS.get(user.role, {})
        module_permissions = role_permissions.get(module, [])
        return permission in module_permissions
    
    @staticmethod
    def get_user_modules(user: User) -> List[ModuleName]:
        """Get list of modules accessible by user"""
        if user.role == UserRole.ADMIN:
            return list(ModuleName)
        
        role_permissions = ROLE_PERMISSIONS.get(user.role, {})
        return list(role_permissions.keys())
    
    @staticmethod
    def get_module_permissions(user: User, module: ModuleName) -> List[Permission]:
        """Get user's permissions for a specific module"""
        if user.role == UserRole.ADMIN:
            return [Permission.VIEW, Permission.CREATE, Permission.UPDATE, Permission.DELETE, Permission.APPROVE, Permission.EXECUTE]
        
        role_permissions = ROLE_PERMISSIONS.get(user.role, {})
        return role_permissions.get(module, [])
    
    @staticmethod
    def check_module_access(user: User, module: ModuleName) -> None:
        """Check module access and raise exception if denied"""
        if not AccessControl.has_module_access(user, module):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied to {module.value} module. Your role: {user.role.value}"
            )
    
    @staticmethod
    def check_permission(user: User, module: ModuleName, permission: Permission) -> None:
        """Check permission and raise exception if denied"""
        if not AccessControl.has_permission(user, module, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} on {module.value} module. Your role: {user.role.value}"
            )
    
    @staticmethod
    def get_user_permissions_summary(user: User) -> dict:
        """Get complete permissions summary for user"""
        modules = AccessControl.get_user_modules(user)
        summary = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "department": user.department,
            "modules": {}
        }
        
        for module in modules:
            permissions = AccessControl.get_module_permissions(user, module)
            summary["modules"][module.value] = [p.value for p in permissions]
        
        return summary


def require_module_access(module: ModuleName):
    """
    Dependency to require module access
    
    Usage:
    ```python
    @router.get("/cutting/status")
    async def get_status(user: User = Depends(require_module_access(ModuleName.CUTTING))):
        return {"status": "ok"}
    ```
    """
    from fastapi import Depends
    from app.core.dependencies import get_current_user
    
    async def check_access(user: User = Depends(get_current_user)) -> User:
        AccessControl.check_module_access(user, module)
        return user
    
    return check_access


def require_permission(module: ModuleName, permission: Permission):
    """
    Dependency to require specific permission on module
    
    Usage:
    ```python
    @router.post("/cutting/complete")
    async def complete_cutting(
        user: User = Depends(require_permission(ModuleName.CUTTING, Permission.EXECUTE))
    ):
        return {"message": "Cutting completed"}
    ```
    """
    from fastapi import Depends
    from app.core.dependencies import get_current_user
    
    async def check_perm(user: User = Depends(get_current_user)) -> User:
        AccessControl.check_permission(user, module, permission)
        return user
    
    return check_perm
