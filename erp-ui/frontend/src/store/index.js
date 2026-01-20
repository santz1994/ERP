import { create } from 'zustand';
import { apiClient } from '@/api/client';
export const useAuthStore = create((set) => ({
    user: null,
    token: null,
    loading: false,
    error: null,
    login: async (username, password) => {
        try {
            set({ loading: true, error: null });
            const response = await apiClient.login(username, password);
            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('user', JSON.stringify(response.user));
            set({
                user: response.user,
                token: response.access_token,
                loading: false,
            });
        }
        catch (error) {
            const message = error.response?.data?.detail || 'Login failed';
            set({ error: message, loading: false });
            throw error;
        }
    },
    logout: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        set({ user: null, token: null });
    },
    setUser: (user) => set({ user }),
    setToken: (token) => set({ token }),
    loadUserFromStorage: () => {
        const token = localStorage.getItem('access_token');
        const userStr = localStorage.getItem('user');
        if (token && userStr) {
            try {
                const user = JSON.parse(userStr);
                set({ user, token });
            }
            catch (e) {
                localStorage.removeItem('user');
                localStorage.removeItem('access_token');
            }
        }
    },
}));
export const useUIStore = create((set) => ({
    sidebarOpen: true,
    notifications: [],
    toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
    addNotification: (type, message) => set((state) => ({
        notifications: [
            ...state.notifications,
            { id: Date.now().toString(), type: type, message },
        ],
    })),
    removeNotification: (id) => set((state) => ({
        notifications: state.notifications.filter((n) => n.id !== id),
    })),
}));
