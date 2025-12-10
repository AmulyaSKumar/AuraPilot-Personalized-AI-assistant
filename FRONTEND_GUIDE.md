# AuraPilot Frontend - Complete Build Guide

## Overview

This guide will help you build a **Next.js + React** frontend for AuraPilot that connects to your FastAPI backend.

---

## Prerequisites

- Node.js 18+ installed (https://nodejs.org/)
- npm or yarn
- Backend running on http://127.0.0.1:8001
- Basic React knowledge (optional but helpful)

---

## Step 1: Create Next.js Project

### Option A: Using create-next-app (Easiest)

```bash
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot
npx create-next-app@latest frontend --typescript --tailwind --eslint
```

When prompted, answer:
- **TypeScript?** → Yes
- **ESLint?** → Yes
- **Tailwind CSS?** → Yes
- **App Router?** → Yes
- **Use src directory?** → No
- **Import alias?** → Use @/*

### Option B: Manual Setup

```bash
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot
mkdir frontend
cd frontend
npm init -y
npm install next react react-dom axios zustand
npm install -D tailwindcss postcss autoprefixer typescript @types/react @types/node
npx tailwindcss init -p
```

---

## Step 2: Project Structure

After creation, your frontend folder should look like:

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Home page
│   ├── login/
│   │   └── page.tsx        # Login page
│   ├── register/
│   │   └── page.tsx        # Register page
│   ├── dashboard/
│   │   ├── page.tsx        # Dashboard (main)
│   │   ├── chat/
│   │   │   └── page.tsx    # Chat interface
│   │   └── documents/
│   │       └── page.tsx    # Documents page
│   ├── globals.css         # Global styles
│   ├── api/                # Optional: API routes
│   └── lib/                # Utilities
│       ├── api.ts          # API client
│       ├── auth.ts         # Auth helpers
│       └── store.ts        # Zustand store
├── components/             # React components
│   ├── Navbar.tsx
│   ├── ChatInterface.tsx
│   ├── DocumentUpload.tsx
│   └── AuthForm.tsx
├── public/                 # Static files
├── package.json
├── tsconfig.json
├── tailwind.config.ts
├── next.config.ts
└── .env.local             # Environment variables
```

---

## Step 3: Environment Configuration

Create `.env.local` in the `frontend/` directory:

```env
# Backend API
NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8001
NEXT_PUBLIC_API_V1_STR=/api/v1

# Feature flags
NEXT_PUBLIC_ENABLE_DOCS=true
```

---

## Step 4: Create API Client

Create `lib/api.ts`:

```typescript
import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL;
const API_V1 = process.env.NEXT_PUBLIC_API_V1_STR;

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
```

---

## Step 5: Create Auth Store (Zustand)

Create `lib/store.ts`:

```typescript
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
  
  // Actions
  login: (username: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,
  isLoading: false,
  error: null,
  
  login: async (username, password) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authAPI.login(username, password);
      localStorage.setItem('access_token', data.access_token);
      set({ token: data.access_token });
      // Fetch user data
      const userRes = await authAPI.getMe();
      set({ user: userRes.data, isLoading: false });
    } catch (err: any) {
      set({ error: err.response?.data?.detail || 'Login failed', isLoading: false });
      throw err;
    }
  },
  
  register: async (email, username, password, fullName) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await authAPI.register(email, username, password, fullName);
      set({ user: data, isLoading: false });
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
}));
```

---

## Step 6: Create Pages

### App Layout (`app/layout.tsx`):

```typescript
import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AuraPilot - AI Assistant',
  description: 'Your personalized AI co-pilot',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
      </body>
    </html>
  );
}
```

### Home Page (`app/page.tsx`):

```typescript
'use client';

import Link from 'next/link';
import { useAuth } from '@/lib/store';
import { useEffect } from 'react';

export default function Home() {
  const { user, checkAuth } = useAuth();
  
  useEffect(() => {
    checkAuth();
  }, []);
  
  if (user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="max-w-7xl mx-auto px-4 py-16 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome to AuraPilot, {user.full_name}! 👋
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Your personalized AI co-pilot for document intelligence
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/dashboard/chat" className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700">
              Start Chatting
            </Link>
            <Link href="/dashboard/documents" className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700">
              Upload Documents
            </Link>
          </div>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <h1 className="text-6xl font-bold text-gray-900 mb-4">
          AuraPilot ✨
        </h1>
        <p className="text-2xl text-gray-600 mb-8">
          Your personalized AI co-pilot that intelligently navigates your data
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/login" className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 text-lg">
            Login
          </Link>
          <Link href="/register" className="bg-indigo-600 text-white px-8 py-3 rounded-lg hover:bg-indigo-700 text-lg">
            Register
          </Link>
        </div>
      </div>
    </div>
  );
}
```

### Login Page (`app/login/page.tsx`):

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/store';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const { login, error, isLoading } = useAuth();
  const router = useRouter();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(username, password);
      router.push('/dashboard/chat');
    } catch (err) {
      // Error is handled by store
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Login</h1>
        
        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white font-medium py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </button>
        </form>
        
        <p className="text-center text-gray-600 mt-4">
          Don't have an account?{' '}
          <Link href="/register" className="text-blue-600 hover:underline">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}
```

### Register Page (`app/register/page.tsx`):

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/lib/store';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const { register, error, isLoading } = useAuth();
  const router = useRouter();
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await register(email, username, password, fullName);
      router.push('/login');
    } catch (err) {
      // Error is handled by store
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-md">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Register</h1>
        
        {error && (
          <div className="bg-red-50 text-red-700 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-gray-700 font-medium mb-2">Full Name</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 font-medium mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 font-medium mb-2">Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div>
            <label className="block text-gray-700 font-medium mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-blue-600 text-white font-medium py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Registering...' : 'Register'}
          </button>
        </form>
        
        <p className="text-center text-gray-600 mt-4">
          Already have an account?{' '}
          <Link href="/login" className="text-blue-600 hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
```

### Chat Page (`app/dashboard/chat/page.tsx`):

```typescript
'use client';

import { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/lib/store';
import { chatAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: any[];
}

export default function ChatPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!token) {
      router.push('/login');
    }
  }, [token, router]);
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  
  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: input }]);
    setInput('');
    setLoading(true);
    
    try {
      const { data } = await chatAPI.query(input, 0.7, true);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response,
        sources: data.sources
      }]);
    } catch (err) {
      console.error('Error sending message:', err);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your message.'
      }]);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">AuraPilot Chat</h1>
          <div className="flex items-center gap-4">
            <span className="text-gray-600">Welcome, {user?.full_name}</span>
            <button
              onClick={() => {
                // Add logout logic
              }}
              className="text-gray-600 hover:text-gray-900"
            >
              Logout
            </button>
          </div>
        </div>
      </header>
      
      {/* Chat Container */}
      <div className="max-w-4xl mx-auto h-[calc(100vh-200px)] flex flex-col">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 && (
            <div className="flex items-center justify-center h-full text-gray-400">
              <div className="text-center">
                <p className="text-xl mb-2">No messages yet</p>
                <p>Start by uploading a document and asking questions!</p>
              </div>
            </div>
          )}
          
          {messages.map((msg, idx) => (
            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-2xl p-4 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-900'
              }`}>
                <p>{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 text-sm border-t border-gray-300 pt-2">
                    <p className="font-semibold">Sources:</p>
                    {msg.sources.map((src, i) => (
                      <p key={i}>• {src.file_name}</p>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-200 text-gray-900 p-4 rounded-lg">
                <div className="flex gap-2">
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        {/* Input */}
        <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question about your documents..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              Send
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
```

### Documents Page (`app/dashboard/documents/page.tsx`):

```typescript
'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/store';
import { documentAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

interface Document {
  id: number;
  filename: string;
  file_size: number;
  status: 'processing' | 'indexed' | 'failed';
  chunk_count: number;
  error_message?: string;
  created_at: string;
}

export default function DocumentsPage() {
  const { user, token } = useAuth();
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  useEffect(() => {
    if (!token) {
      router.push('/login');
    } else {
      loadDocuments();
    }
  }, [token, router]);
  
  const loadDocuments = async () => {
    setLoading(true);
    try {
      const { data } = await documentAPI.list();
      setDocuments(data);
    } catch (err) {
      console.error('Error loading documents:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setUploading(true);
    try {
      const { data } = await documentAPI.upload(file);
      setDocuments(prev => [data, ...prev]);
      e.target.value = '';
    } catch (err) {
      console.error('Error uploading document:', err);
      alert('Error uploading document');
    } finally {
      setUploading(false);
    }
  };
  
  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure?')) return;
    try {
      await documentAPI.delete(id);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
    } catch (err) {
      console.error('Error deleting document:', err);
    }
  };
  
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">My Documents</h1>
        </div>
      </header>
      
      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Upload Section */}
        <div className="bg-white p-6 rounded-lg shadow mb-8">
          <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
          <label className="flex items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <p className="mb-2 text-sm text-gray-500">
                Click to upload PDF or TXT
              </p>
            </div>
            <input
              type="file"
              className="hidden"
              accept=".pdf,.txt,.docx"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
        </div>
        
        {/* Documents List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Filename</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Size</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-900">Chunks</th>
                <th className="px-6 py-3 text-right text-sm font-semibold text-gray-900">Actions</th>
              </tr>
            </thead>
            <tbody>
              {documents.map(doc => (
                <tr key={doc.id} className="border-b hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm text-gray-900">{doc.filename}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">{(doc.file_size / 1024).toFixed(2)} KB</td>
                  <td className="px-6 py-4 text-sm">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      doc.status === 'indexed'
                        ? 'bg-green-100 text-green-800'
                        : doc.status === 'processing'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {doc.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-600">{doc.chunk_count}</td>
                  <td className="px-6 py-4 text-right text-sm">
                    <button
                      onClick={() => handleDelete(doc.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {documents.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No documents yet. Upload one to get started!
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

---

## Step 7: Run Frontend

```bash
cd frontend
npm run dev
```

Frontend will be available at: **http://localhost:3000**

---

## Step 8: CORS Configuration

If you get CORS errors, update your backend `app/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing Checklist

- [ ] Register new user
- [ ] Login with credentials
- [ ] Upload a document
- [ ] Wait for "indexed" status
- [ ] Ask a question in chat
- [ ] See RAG response with sources
- [ ] Logout

---

## Troubleshooting

**Port 3000 already in use:**
```bash
npm run dev -- -p 3001
```

**API not responding:**
- Ensure backend is running on http://127.0.0.1:8001
- Check `.env.local` has correct API_BASE_URL

**Styling issues:**
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

---

That's it! You now have a complete frontend ready to build! 🚀

Would you like me to create all these files for you automatically?
