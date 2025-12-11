import { create } from 'zustand';
import { authAPI } from './api';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

interface AuthStore {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  
  login: (username: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
  clearError: () => void;
}

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  token: typeof window !== 'undefined' ? localStorage.getItem('access_token') : null,
  isLoading: false,
  error: null,
  
  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authAPI.login(username, password);
      localStorage.setItem('access_token', data.access_token);
      set({ token: data.access_token });
      // User comes from login response
      if (data.user) {
        set({ user: data.user, isLoading: false });
      } else {
        const userRes = await authAPI.getMe();
        set({ user: userRes.data, isLoading: false });
      }
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Login failed', isLoading: false });
      throw err;
    }
  },
  
  register: async (email, username, password, fullName) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authAPI.register(email, username, password, fullName);
      // Save token from registration
      if (data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        set({ token: data.access_token, user: data.user, isLoading: false });
      } else {
        set({ user: data, isLoading: false });
      }
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Registration failed', isLoading: false });
      throw err;
    }
  },
  
  logout: () => {
    authAPI.logout();
    set({ user: null, token: null });
  },
  
  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    
    try {
      const { data } = await authAPI.getMe();
      set({ user: data, token });
    } catch {
      authAPI.logout();
      set({ user: null, token: null });
    }
  },
  
  clearError: () => set({ error: null }),
}));
