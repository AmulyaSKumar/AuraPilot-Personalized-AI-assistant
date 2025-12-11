import axios from 'axios';

const API_BASE = 'http://127.0.0.1:8001';
const API_V1 = '/api/v1';

const api = axios.create({
  baseURL: `${API_BASE}${API_V1}`,
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (email: string, username: string, password: string, fullName?: string) =>
    api.post('/auth/register', { email, username, password, full_name: fullName }),
  
  login: (username: string, password: string) =>
    api.post('/auth/login', { username, password }),
  
  getMe: () => api.get('/auth/me'),
  
  logout: () => {
    localStorage.removeItem('access_token');
  },
};

// Chat API
export const chatAPI = {
  query: (query: string, temperature: number = 0.7, includeSources: boolean = true) =>
    api.post('/chat/query', { query, temperature, include_sources: includeSources }),
  
  getMessages: (skip: number = 0, limit: number = 50) =>
    api.get(`/chat/messages?skip=${skip}&limit=${limit}`),
  
  clearHistory: () => api.delete('/chat/history'),
};

// Document API
export const documentAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  
  list: (skip: number = 0, limit: number = 50) =>
    api.get(`/documents/?skip=${skip}&limit=${limit}`),
  
  delete: (id: number) => api.delete(`/documents/${id}`),
  
  reindex: (id: number) => api.post(`/documents/${id}/reindex`, {}),
};

export default api;
