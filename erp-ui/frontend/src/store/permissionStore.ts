/**
 * Permission Store - PBAC Frontend Integration
 * Phase 16 Week 4
 * 
 * Manages user permissions for UI-level access control.
 * Fetches permissions from backend /auth/permissions endpoint.
 */

import { create } from 'zustand'
import { apiClient } from '../api/client'

// Import auth store to check user role for bypass
const getUserRole = (): string | null => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      return user.role
    }
  } catch (e) {
    console.error('[PermissionStore] Error reading user role:', e)
  }
  return null
}

interface PermissionState {
  permissions: string[]
  loading: boolean
  error: string | null
  lastFetchedAt: Date | null
  
  // Actions
  loadPermissions: () => Promise<void>
  hasPermission: (code: string) => boolean
  hasAnyPermission: (codes: string[]) => boolean
  hasAllPermissions: (codes: string[]) => boolean
  clearPermissions: () => void
  
  // Utility
  getModulePermissions: (module: string) => string[]
}

/**
 * Permission store using Zustand
 * 
 * Usage:
 * ```tsx
 * const { permissions, loadPermissions, hasPermission } = usePermissionStore()
 * 
 * useEffect(() => {
 *   loadPermissions()
 * }, [])
 * 
 * if (hasPermission('cutting.allocate_material')) {
 *   // Show allocate button
 * }
 * ```
 */
export const usePermissionStore = create<PermissionState>((set, get) => ({
  permissions: [],
  loading: false,
  error: null,
  lastFetchedAt: null,
  
  /**
   * Load user permissions from backend
   * Automatically called after login
   */
  loadPermissions: async () => {
    try {
      set({ loading: true, error: null })
      
      const response = await apiClient.get('/auth/permissions')
      const responseData = response.data || { permissions: [] }
      const { permissions } = responseData
      
      set({ 
        permissions, 
        loading: false,
        lastFetchedAt: new Date()
      })
      
      console.log(`[PermissionStore] Loaded ${permissions.length} permissions`)
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to load permissions'
      
      set({ 
        error: errorMessage, 
        loading: false,
        permissions: [] 
      })
      
      console.error('[PermissionStore] Error loading permissions:', errorMessage)
    }
  },
  
  /**
   * Check if user has a specific permission
   * 
   * BYPASS: DEVELOPER, SUPERADMIN, and ADMIN roles have full access
   * 
   * @param code - Permission code (e.g., 'cutting.allocate_material')
   * @returns true if user has permission
   */
  hasPermission: (code: string): boolean => {
    // Check for bypass roles first
    const userRole = getUserRole()
    if (userRole) {
      const roleUpper = userRole.toUpperCase()
      if (roleUpper === 'DEVELOPER' || roleUpper === 'SUPERADMIN' || roleUpper === 'ADMIN') {
        return true // Full access bypass
      }
    }
    
    const { permissions } = get()
    return permissions.includes(code)
  },
  
  /**
   * Check if user has ANY of the specified permissions (OR logic)
   * 
   * BYPASS: DEVELOPER, SUPERADMIN, and ADMIN roles have full access
   * 
   * @param codes - Array of permission codes
   * @returns true if user has at least one permission
   * 
   * @example
   * hasAnyPermission(['cutting.view_status', 'cutting.allocate_material'])
   */
  hasAnyPermission: (codes: string[]): boolean => {
    // Check for bypass roles first
    const userRole = getUserRole()
    if (userRole) {
      const roleUpper = userRole.toUpperCase()
      if (roleUpper === 'DEVELOPER' || roleUpper === 'SUPERADMIN' || roleUpper === 'ADMIN') {
        return true // Full access bypass
      }
    }
    
    const { permissions } = get()
    return codes.some(code => permissions.includes(code))
  },
  
  /**
   * Check if user has ALL of the specified permissions (AND logic)
   * 
   * BYPASS: DEVELOPER, SUPERADMIN, and ADMIN roles have full access
   * 
   * @param codes - Array of permission codes
   * @returns true if user has all permissions
   * 
   * @example
   * hasAllPermissions(['cutting.allocate_material', 'cutting.complete_operation'])
   */
  hasAllPermissions: (codes: string[]): boolean => {
    // Check for bypass roles first
    const userRole = getUserRole()
    if (userRole) {
      const roleUpper = userRole.toUpperCase()
      if (roleUpper === 'DEVELOPER' || roleUpper === 'SUPERADMIN' || roleUpper === 'ADMIN') {
        return true // Full access bypass
      }
    }
    
    const { permissions } = get()
    return codes.every(code => permissions.includes(code))
  },
  
  /**
   * Clear all permissions (called on logout)
   */
  clearPermissions: () => {
    set({ 
      permissions: [], 
      error: null,
      lastFetchedAt: null
    })
    console.log('[PermissionStore] Permissions cleared')
  },
  
  /**
   * Get all permissions for a specific module
   * 
   * @param module - Module name (e.g., 'cutting')
   * @returns Array of permission codes for that module
   * 
   * @example
   * getModulePermissions('cutting') // ['cutting.allocate_material', 'cutting.view_status']
   */
  getModulePermissions: (module: string): string[] => {
    const { permissions } = get()
    return permissions.filter(p => p.startsWith(`${module}.`))
  }
}))

/**
 * Auto-refresh permissions if stale (older than 5 minutes)
 * Call this in App.tsx or layout component
 */
export const useAutoRefreshPermissions = () => {
  const { lastFetchedAt, loadPermissions } = usePermissionStore()
  
  // Check if permissions are stale (>5 minutes old)
  if (lastFetchedAt) {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000)
    if (lastFetchedAt < fiveMinutesAgo) {
      console.log('[PermissionStore] Permissions stale, refreshing...')
      loadPermissions()
    }
  }
}
