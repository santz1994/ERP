/**
 * Permission Hooks - PBAC Frontend Integration
 * Phase 16 Week 4
 * 
 * React hooks for permission-based UI rendering.
 * Simplifies permission checks in components.
 */

import { usePermissionStore } from '../store/permissionStore'

/**
 * Check if user has a specific permission
 * 
 * @param permissionCode - Permission code (e.g., 'cutting.allocate_material')
 * @returns true if user has permission
 * 
 * @example
 * ```tsx
 * const canAllocateMaterial = usePermission('cutting.allocate_material')
 * 
 * return (
 *   <>
 *     {canAllocateMaterial && (
 *       <Button onClick={handleAllocate}>Allocate Material</Button>
 *     )}
 *   </>
 * )
 * ```
 */
export const usePermission = (permissionCode: string): boolean => {
  const hasPermission = usePermissionStore(state => state.hasPermission)
  return hasPermission(permissionCode)
}

/**
 * Check if user has ANY of the specified permissions (OR logic)
 * 
 * @param permissionCodes - Array of permission codes
 * @returns true if user has at least one permission
 * 
 * @example
 * ```tsx
 * // User needs either permission to see the section
 * const canViewCutting = useAnyPermission([
 *   'cutting.view_status',
 *   'cutting.allocate_material'
 * ])
 * 
 * return (
 *   <>
 *     {canViewCutting && <CuttingDashboard />}
 *   </>
 * )
 * ```
 */
export const useAnyPermission = (permissionCodes: string[]): boolean => {
  const hasAnyPermission = usePermissionStore(state => state.hasAnyPermission)
  return hasAnyPermission(permissionCodes)
}

/**
 * Check if user has ALL of the specified permissions (AND logic)
 * 
 * @param permissionCodes - Array of permission codes
 * @returns true if user has all permissions
 * 
 * @example
 * ```tsx
 * // User needs both permissions to see the section
 * const canManageUsers = useAllPermissions([
 *   'admin.manage_users',
 *   'admin.view_system_info'
 * ])
 * 
 * return (
 *   <>
 *     {canManageUsers && <AdminPanel />}
 *   </>
 * )
 * ```
 */
export const useAllPermissions = (permissionCodes: string[]): boolean => {
  const hasAllPermissions = usePermissionStore(state => state.hasAllPermissions)
  return hasAllPermissions(permissionCodes)
}

/**
 * Get all user permissions
 * Useful for debugging or showing user their permissions
 * 
 * @returns Array of permission codes
 * 
 * @example
 * ```tsx
 * const permissions = usePermissions()
 * 
 * return (
 *   <div>
 *     <h3>Your Permissions ({permissions.length})</h3>
 *     <ul>
 *       {permissions.map(p => (
 *         <li key={p}>{p}</li>
 *       ))}
 *     </ul>
 *   </div>
 * )
 * ```
 */
export const usePermissions = (): string[] => {
  const permissions = usePermissionStore(state => state.permissions)
  return permissions
}

/**
 * Get all permissions for a specific module
 * 
 * @param module - Module name (e.g., 'cutting')
 * @returns Array of permission codes for that module
 * 
 * @example
 * ```tsx
 * const cuttingPermissions = useModulePermissions('cutting')
 * // Returns: ['cutting.allocate_material', 'cutting.view_status', ...]
 * ```
 */
export const useModulePermissions = (module: string): string[] => {
  const getModulePermissions = usePermissionStore(state => state.getModulePermissions)
  return getModulePermissions(module)
}

/**
 * Get permission loading state
 * Useful for showing loading spinner while permissions are being fetched
 * 
 * @returns { loading: boolean, error: string | null }
 * 
 * @example
 * ```tsx
 * const { loading, error } = usePermissionState()
 * 
 * if (loading) return <Spinner />
 * if (error) return <Alert>{error}</Alert>
 * ```
 */
export const usePermissionState = (): { loading: boolean; error: string | null } => {
  const loading = usePermissionStore(state => state.loading)
  const error = usePermissionStore(state => state.error)
  return { loading, error }
}
