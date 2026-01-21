import { create } from 'zustand'
import { User } from '@/types'
import { apiClient } from '@/api/client'
import { usePermissionStore } from './permissionStore'

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
  initialized: boolean
  
  // Actions
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  loadUserFromStorage: () => void
}

// Initialize auth state from localStorage
const initializeAuth = () => {
  try {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      const user = JSON.parse(userStr)
      return { user, token, initialized: true }
    }
  } catch (e) {
    console.error('Failed to load auth from storage:', e)
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
  }
  return { user: null, token: null, initialized: true }
}

export const useAuthStore = create<AuthState>((set) => ({
  ...initializeAuth(),
  loading: false,
  error: null,

  login: async (username: string, password: string) => {
    try {
      set({ loading: true, error: null })
      console.log('[AuthStore] Starting login for:', username)
      
      const response = await apiClient.login(username, password)
      console.log('[AuthStore] Login response received:', { 
        hasToken: !!response.access_token, 
        hasUser: !!response.user,
        userRole: response.user?.role 
      })
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      console.log('[AuthStore] Tokens saved to localStorage')
      
      set({
        user: response.user,
        token: response.access_token,
        loading: false,
        initialized: true,
      })
      console.log('[AuthStore] State updated with user data')
      
      // Load permissions after successful login
      const permStore = usePermissionStore.getState()
      await permStore.loadPermissions()
      console.log('[AuthStore] Login successful, permissions loaded')
      
    } catch (error: any) {
      console.error('[AuthStore] Login error:', error)
      const message = error.response?.data?.detail || 'Login failed'
      set({ error: message, loading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    
    // Clear permissions on logout
    const permStore = usePermissionStore.getState()
    permStore.clearPermissions()
    
    set({ user: null, token: null })
    console.log('[AuthStore] Logged out, permissions cleared')
  },

  setUser: (user: User | null) => set({ user }),
  setToken: (token: string | null) => set({ token }),

  loadUserFromStorage: () => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        set({ user, token, initialized: true })
        
        // Load permissions when rehydrating from storage
        const permStore = usePermissionStore.getState()
        permStore.loadPermissions()
        console.log('[AuthStore] User loaded from storage, fetching permissions')
        
      } catch (e) {
        localStorage.removeItem('user')
        localStorage.removeItem('access_token')
        set({ initialized: true })
      }
    } else {
      set({ initialized: true })
    }
  },
}))

interface UIState {
  sidebarOpen: boolean
  notifications: Array<{
    id: string
    type: 'success' | 'error' | 'warning' | 'info'
    message: string
  }>
  
  toggleSidebar: () => void
  addNotification: (type: string, message: string) => void
  removeNotification: (id: string) => void
}

export const useUIStore = create<UIState>((set) => ({
  sidebarOpen: true,
  notifications: [],

  toggleSidebar: () =>
    set((state) => ({ sidebarOpen: !state.sidebarOpen })),

  addNotification: (type: string, message: string) =>
    set((state) => ({
      notifications: [
        ...state.notifications,
        { id: Date.now().toString(), type: type as any, message },
      ],
    })),

  removeNotification: (id: string) =>
    set((state) => ({
      notifications: state.notifications.filter((n) => n.id !== id),
    })),
}))
