import { create } from 'zustand'
import { User } from '@/types'
import { apiClient } from '@/api/client'
import { usePermissionStore } from './permissionStore'

/**
 * UI Store Type Definition v2.0.1
 * Manages theme, language, layout, notifications, and visual preferences
 */
export interface UIStore {
  // Display Preference State
  readonly theme: 'light' | 'dark' | 'auto'
  readonly language: string
  readonly compactMode: boolean
  readonly sidebarPosition: 'left' | 'right'
  readonly fontSize: 'small' | 'normal' | 'large'
  readonly colorScheme: 'blue' | 'green' | 'purple' | 'orange'
  
  // Notification State
  readonly sidebarOpen: boolean
  readonly notifications: ReadonlyArray<{
    readonly id: string
    readonly type: 'success' | 'error' | 'warning' | 'info'
    readonly message: string
  }>
  
  // Display Preference Setters
  readonly setTheme: (theme: 'light' | 'dark' | 'auto') => void
  readonly setLanguage: (lang: string) => void
  readonly setCompactMode: (compact: boolean) => void
  readonly setSidebarPosition: (pos: 'left' | 'right') => void
  readonly setFontSize: (size: 'small' | 'normal' | 'large') => void
  readonly setColorScheme: (scheme: 'blue' | 'green' | 'purple' | 'orange') => void
  
  // Notification Setters
  readonly toggleSidebar: () => void
  readonly addNotification: (type: string, message: string) => void
  readonly removeNotification: (id: string) => void
  
  // Batch operations
  readonly updateSettings: (settings: {
    theme?: 'light' | 'dark' | 'auto'
    language?: string
    compactMode?: boolean
    sidebarPosition?: 'left' | 'right'
    fontSize?: 'small' | 'normal' | 'large'
    colorScheme?: 'blue' | 'green' | 'purple' | 'orange'
  }) => void
  readonly loadSettings: () => void
}

// Backward compatibility aliases
export type UIDisplayPreferences = UIStore
export type UIState = UIStore

export const useUIStore = create<UIStore>((set) => ({
  // Initial state - Display Preferences
  theme: 'light',
  language: 'en',
  compactMode: false,
  sidebarPosition: 'left',
  fontSize: 'normal',
  colorScheme: 'blue',
  
  // Initial state - Notifications/UI
  sidebarOpen: true,
  notifications: [],
  
  // Display Preference Setters
  setTheme: (theme) => {
    set({ theme })
    applyTheme(theme)
    saveUISettings()
  },
  setLanguage: (language) => {
    set({ language })
    applyLanguage(language)
    saveUISettings()
  },
  setCompactMode: (compactMode) => {
    set({ compactMode })
    applyCompactMode(compactMode)
    saveUISettings()
  },
  setSidebarPosition: (sidebarPosition) => {
    set({ sidebarPosition })
    saveUISettings()
  },
  setFontSize: (fontSize) => {
    set({ fontSize })
    applyFontSize(fontSize)
    saveUISettings()
  },
  setColorScheme: (colorScheme) => {
    set({ colorScheme })
    saveUISettings()
  },
  
  // Notification Setters
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
  
  // Batch update
  updateSettings: (settings) => {
    set((state) => ({
      theme: settings.theme ?? state.theme,
      language: settings.language ?? state.language,
      compactMode: settings.compactMode ?? state.compactMode,
      sidebarPosition: settings.sidebarPosition ?? state.sidebarPosition,
      fontSize: settings.fontSize ?? state.fontSize,
      colorScheme: settings.colorScheme ?? state.colorScheme,
    }))
    
    const state = useUIStore.getState()
    applyTheme(state.theme)
    applyLanguage(state.language)
    applyCompactMode(state.compactMode)
    applyFontSize(state.fontSize)
    saveUISettings()
  },
  
  // Load from localStorage
  loadSettings: () => {
    try {
      const saved = localStorage.getItem('uiSettings')
      if (saved) {
        const settings = JSON.parse(saved)
        set((state) => ({
          theme: settings.theme ?? state.theme,
          language: settings.language ?? state.language,
          compactMode: settings.compactMode ?? state.compactMode,
          sidebarPosition: settings.sidebarPosition ?? state.sidebarPosition,
          fontSize: settings.fontSize ?? state.fontSize,
          colorScheme: settings.colorScheme ?? state.colorScheme,
        }))
        
        const newState = useUIStore.getState()
        applyTheme(newState.theme)
        applyLanguage(newState.language)
        applyCompactMode(newState.compactMode)
        applyFontSize(newState.fontSize)
      }
    } catch (e) {
      console.error('Failed to load UI settings:', e)
    }
  }
}))

// Helper functions to apply settings to DOM
function applyTheme(theme: string) {
  const root = document.documentElement
  if (theme === 'dark') {
    root.classList.add('dark')
  } else if (theme === 'light') {
    root.classList.remove('dark')
  } else if (theme === 'auto') {
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      root.classList.add('dark')
    } else {
      root.classList.remove('dark')
    }
  }
}

function applyLanguage(lang: string) {
  document.documentElement.lang = lang
  localStorage.setItem('language', lang)
}

function applyCompactMode(compact: boolean) {
  const root = document.documentElement
  if (compact) {
    root.classList.add('compact-mode')
  } else {
    root.classList.remove('compact-mode')
  }
}

function applyFontSize(size: string) {
  const root = document.documentElement
  root.classList.remove('text-sm', 'text-base', 'text-lg')
  if (size === 'small') root.classList.add('text-sm')
  else if (size === 'large') root.classList.add('text-lg')
  else root.classList.add('text-base')
}

function saveUISettings() {
  try {
    const state = useUIStore.getState()
    localStorage.setItem('uiSettings', JSON.stringify({
      theme: state.theme,
      language: state.language,
      compactMode: state.compactMode,
      sidebarPosition: state.sidebarPosition,
      fontSize: state.fontSize,
      colorScheme: state.colorScheme,
      savedAt: new Date().toISOString()
    }))
  } catch (e) {
    console.error('Failed to save UI settings:', e)
  }
}

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

// Initialize auth state from localStorage SYNCHRONOUSLY
const initializeAuth = () => {
  try {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    
    // IMPORTANT: Must initialize before React renders
    console.log('[AuthStore] Initialization: token exists?', !!token, 'user exists?', !!userStr)
    
    if (token && userStr) {
      const user = JSON.parse(userStr)
      console.log('[AuthStore] Loaded user from storage:', user.username, 'role:', user.role)
      return { user, token, initialized: true }
    }
  } catch (e) {
    console.error('[AuthStore] Storage error:', e)
    localStorage.removeItem('user')
    localStorage.removeItem('access_token')
  }
  console.log('[AuthStore] No valid auth data in storage')
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
    console.log('[AuthStore.loadUserFromStorage] Called - DEPRECATED, using initializeAuth instead')
    // This is kept for backward compatibility but shouldn't be called
  },
}))

export { usePermissionStore } from './permissionStore'
