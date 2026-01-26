import React, { createContext, useState, useContext, useEffect } from 'react';
import * as SecureStore from 'expo-secure-store';
import { apiClient } from '../api/client';

interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  department: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isSignout: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  restoreToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useState<{
    isLoading: boolean;
    isSignout: boolean;
    user: User | null;
  }>({
    isLoading: true,
    isSignout: false,
    user: null,
  });

  useEffect(() => {
    const bootstrapAsync = async () => {
      try {
        const token = await SecureStore.getItemAsync('authToken');
        if (token) {
          const user = await apiClient.getMe();
          dispatch({
            type: 'RESTORE_TOKEN',
            payload: { user },
          } as any);
        } else {
          dispatch({ type: 'SIGN_OUT' } as any);
        }
      } catch (e) {
        dispatch({ type: 'SIGN_OUT' } as any);
      }
    };

    bootstrapAsync();
  }, []);

  const authContext = {
    ...state,
    login: async (username: string, password: string) => {
      try {
        const response = await apiClient.login(username, password);
        await SecureStore.setItemAsync('authToken', response.token);
        dispatch({
          type: 'SIGN_IN',
          payload: { user: response.user },
        } as any);
      } catch (error) {
        throw error;
      }
    },
    logout: async () => {
      try {
        await apiClient.logout();
      } catch (error) {
        console.error('Logout error:', error);
      }
      await SecureStore.deleteItemAsync('authToken');
      dispatch({ type: 'SIGN_OUT' } as any);
    },
    register: async (username: string, email: string, password: string) => {
      // Implement if needed
      throw new Error('Registration not implemented in mobile app');
    },
    restoreToken: async () => {
      try {
        const token = await SecureStore.getItemAsync('authToken');
        if (token) {
          const user = await apiClient.getMe();
          dispatch({
            type: 'RESTORE_TOKEN',
            payload: { user },
          } as any);
        }
      } catch (error) {
        console.error('Restore token error:', error);
      }
    },
  };

  return <AuthContext.Provider value={authContext}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
