import { create } from 'zustand'
import { User } from '@/types'
import { apiClient } from '@/api/client'

interface AuthState {
  user: User | null
  token: string | null
  loading: boolean
  error: string | null
  
  // Actions
  login: (username: string, password: string) => Promise<void>
  logout: () => void
  setUser: (user: User | null) => void
  setToken: (token: string | null) => void
  loadUserFromStorage: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: null,
  loading: false,
  error: null,

  login: async (username: string, password: string) => {
    try {
      set({ loading: true, error: null })
      const response = await apiClient.login(username, password)
      
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('user', JSON.stringify(response.user))
      
      set({
        user: response.user,
        token: response.access_token,
        loading: false,
      })
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Login failed'
      set({ error: message, loading: false })
      throw error
    }
  },

  logout: () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    set({ user: null, token: null })
  },

  setUser: (user: User | null) => set({ user }),
  setToken: (token: string | null) => set({ token }),

  loadUserFromStorage: () => {
    const token = localStorage.getItem('access_token')
    const userStr = localStorage.getItem('user')
    
    if (token && userStr) {
      try {
        const user = JSON.parse(userStr)
        set({ user, token })
      } catch (e) {
        localStorage.removeItem('user')
        localStorage.removeItem('access_token')
      }
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
