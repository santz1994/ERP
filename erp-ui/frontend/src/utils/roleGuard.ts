/**
 * Role-Based Route Guards
 * 
 * Provides utilities for protecting routes based on user roles and permissions
 * Implements Row-Level Security (RLS) and RBAC at the frontend layer
 */

import { UserRole } from '@/types'

/**
 * Module to Role Mapping
 * Defines which roles can access which modules
 * 
 * Based on ROLE_PERMISSIONS matrix from backend (permissions.py)
 */
export const MODULE_ACCESS_MATRIX: Record<string, UserRole[]> = {
  dashboard: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.FINANCE_MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.PPIC_ADMIN,
    UserRole.PURCHASING_HEAD,
    UserRole.PURCHASING,
    UserRole.SPV_CUTTING,
    UserRole.SPV_SEWING,
    UserRole.SPV_FINISHING,
    UserRole.WAREHOUSE_ADMIN,
    UserRole.QC_LAB,
    UserRole.QC_INSPECTOR,
    UserRole.OPERATOR_CUT,
    UserRole.OPERATOR_EMBRO,
    UserRole.OPERATOR_SEW,
    UserRole.OPERATOR_FINISH,
    UserRole.OPERATOR_PACK,
    UserRole.WAREHOUSE_OP,
    UserRole.SECURITY,
  ],
  ppic: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.PPIC_ADMIN,
  ],
  purchasing: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.FINANCE_MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.PURCHASING_HEAD,
    UserRole.PURCHASING,
  ],
  warehouse: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.WAREHOUSE_ADMIN,
    UserRole.WAREHOUSE_OP,
    UserRole.PURCHASING,
    UserRole.SPV_CUTTING,
    UserRole.SPV_SEWING,
    UserRole.SPV_FINISHING,
  ],
  cutting: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.SPV_CUTTING,
    UserRole.OPERATOR_CUT,
  ],
  embroidery: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.SPV_SEWING,
    UserRole.OPERATOR_EMBRO,
  ],
  sewing: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.SPV_SEWING,
    UserRole.OPERATOR_SEW,
  ],
  finishing: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.SPV_FINISHING,
    UserRole.OPERATOR_FINISH,
  ],
  packing: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.SPV_FINISHING,
    UserRole.OPERATOR_PACK,
  ],
  finishgoods: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.WAREHOUSE_ADMIN,
    UserRole.WAREHOUSE_OP,
  ],
  qc: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.QC_LAB,
    UserRole.QC_INSPECTOR,
    UserRole.SPV_CUTTING,
    UserRole.SPV_SEWING,
    UserRole.SPV_FINISHING,
  ],
  kanban: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.ADMIN,
    UserRole.WAREHOUSE_ADMIN,
    UserRole.OPERATOR_PACK,
  ],
  reports: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.MANAGER,
    UserRole.FINANCE_MANAGER,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.PPIC_ADMIN,
    UserRole.PURCHASING_HEAD,
    UserRole.PURCHASING,
    UserRole.WAREHOUSE_ADMIN,
    UserRole.SPV_CUTTING,
    UserRole.SPV_SEWING,
    UserRole.SPV_FINISHING,
    UserRole.QC_LAB,
  ],
  admin: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.ADMIN,
  ],
  masterdata: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.ADMIN,
    UserRole.PPIC_MANAGER,
    UserRole.PPIC_ADMIN,
  ],
  import_export: [
    UserRole.DEVELOPER,
    UserRole.SUPERADMIN,
    UserRole.ADMIN,
  ],
}

/**
 * Check if user has access to a specific module
 * 
 * @param userRole - The user's role
 * @param module - The module to check access for
 * @returns true if user has access, false otherwise
 */
export const hasModuleAccess = (
  userRole: UserRole,
  module: keyof typeof MODULE_ACCESS_MATRIX
): boolean => {
  const allowedRoles = MODULE_ACCESS_MATRIX[module]
  return allowedRoles ? allowedRoles.includes(userRole) : false
}

/**
 * Check if user has any of the specified roles
 * 
 * @param userRole - The user's role
 * @param allowedRoles - Array of allowed roles
 * @returns true if user has one of the allowed roles
 */
export const hasAnyRole = (
  userRole: UserRole,
  allowedRoles: UserRole[]
): boolean => {
  return allowedRoles.includes(userRole)
}

/**
 * Get all accessible modules for a user role
 * 
 * @param userRole - The user's role
 * @returns Array of module names the user can access
 */
export const getAccessibleModules = (
  userRole: UserRole
): string[] => {
  const modules: string[] = []
  
  Object.entries(MODULE_ACCESS_MATRIX).forEach(([module, roles]) => {
    if (roles.includes(userRole)) {
      modules.push(module)
    }
  })
  
  return modules
}

/**
 * Role hierarchy levels
 * Used for comparing role authority
 */
export const ROLE_HIERARCHY: Record<UserRole, number> = {
  [UserRole.DEVELOPER]: 0,
  [UserRole.SUPERADMIN]: 1,
  [UserRole.MANAGER]: 2,
  [UserRole.FINANCE_MANAGER]: 2,
  [UserRole.ADMIN]: 3,
  [UserRole.PPIC_MANAGER]: 4,
  [UserRole.PPIC_ADMIN]: 4,
  [UserRole.PURCHASING_HEAD]: 4,
  [UserRole.SPV_CUTTING]: 4,
  [UserRole.SPV_SEWING]: 4,
  [UserRole.SPV_FINISHING]: 4,
  [UserRole.WAREHOUSE_ADMIN]: 4,
  [UserRole.QC_LAB]: 4,
  [UserRole.PURCHASING]: 5,
  [UserRole.OPERATOR_CUT]: 5,
  [UserRole.OPERATOR_EMBRO]: 5,
  [UserRole.OPERATOR_SEW]: 5,
  [UserRole.OPERATOR_FINISH]: 5,
  [UserRole.OPERATOR_PACK]: 5,
  [UserRole.QC_INSPECTOR]: 5,
  [UserRole.WAREHOUSE_OP]: 5,
  [UserRole.SECURITY]: 5,
}

/**
 * Check if user has minimum role level
 * 
 * @param userRole - The user's role
 * @param minimumLevel - Minimum hierarchy level required
 * @returns true if user meets minimum level
 */
export const hasMinimumRoleLevel = (
  userRole: UserRole,
  minimumLevel: number
): boolean => {
  const userLevel = ROLE_HIERARCHY[userRole]
  return userLevel !== undefined && userLevel <= minimumLevel
}

/**
 * Check if user is a high-privilege role (Level 0-2)
 * These roles require MFA (future implementation)
 * 
 * @param userRole - The user's role
 * @returns true if user is high-privilege
 */
export const isHighPrivilegeRole = (userRole: UserRole): boolean => {
  const level = ROLE_HIERARCHY[userRole]
  return level !== undefined && level <= 2
}

/**
 * Check if user is an operator (Level 5)
 * Operators have limited UI with focus on execution
 * 
 * @param userRole - The user's role
 * @returns true if user is operator
 */
export const isOperatorRole = (userRole: UserRole): boolean => {
  const level = ROLE_HIERARCHY[userRole]
  return level === 5
}

/**
 * Get user role display name
 * 
 * @param role - User role enum
 * @returns Human-readable role name
 */
export const getRoleDisplayName = (role: UserRole): string => {
  return role.toString()
}

/**
 * Permission levels for UI elements
 * Maps to backend Permission enum
 */
export enum PermissionLevel {
  VIEW = 'view',
  CREATE = 'create',
  UPDATE = 'update',
  DELETE = 'delete',
  APPROVE = 'approve',
  EXECUTE = 'execute',
}

/**
 * Check if user can perform action on module
 * (Simplified - full implementation requires backend permission matrix)
 * 
 * @param userRole - The user's role
 * @param module - The module name
 * @param permission - The permission level required
 * @returns true if user has permission
 */
export const hasPermission = (
  userRole: UserRole,
  module: string,
  permission: PermissionLevel
): boolean => {
  // High-privilege roles have all permissions
  if (isHighPrivilegeRole(userRole)) {
    return true
  }
  
  // Operator roles: only VIEW and EXECUTE on their department
  if (isOperatorRole(userRole)) {
    return permission === PermissionLevel.VIEW || permission === PermissionLevel.EXECUTE
  }
  
  // Supervisor roles: VIEW, CREATE, UPDATE, EXECUTE, APPROVE on their modules
  const supervisorRoles = [
    UserRole.SPV_CUTTING,
    UserRole.SPV_SEWING,
    UserRole.SPV_FINISHING,
    UserRole.WAREHOUSE_ADMIN,
    UserRole.QC_LAB,
  ]
  
  if (supervisorRoles.includes(userRole)) {
    return [
      PermissionLevel.VIEW,
      PermissionLevel.CREATE,
      PermissionLevel.UPDATE,
      PermissionLevel.EXECUTE,
      PermissionLevel.APPROVE,
    ].includes(permission)
  }
  
  // Default: check module access
  return hasModuleAccess(userRole, module as keyof typeof MODULE_ACCESS_MATRIX)
}
