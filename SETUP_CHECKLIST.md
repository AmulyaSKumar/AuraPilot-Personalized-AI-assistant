# AuraPilot Complete Setup Checklist

## Phase 1: Environment & Dependencies ✅

### 1.1 Python Environment
- [x] Python 3.8+ installed (you have 3.12.6)
- [ ] Virtual environment created: `python -m venv venv`
- [ ] Virtual environment activated: `venv\Scripts\activate` (Windows)
- [ ] Install dependencies: `pip install -r requirements.txt`

**Command to run:**
```powershell
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

---

## Phase 2: External Services Setup ⏳

### 2.1 Ollama (Self-Hosted LLM)
**Status:** REQUIRED - Not yet installed

1. [ ] Download Ollama: https://ollama.ai/download
2. [ ] Install Ollama
3. [ ] Open terminal and run: `ollama serve`
4. [ ] In another terminal, pull LLaMA2: `ollama pull llama2`
5. [ ] Verify it works: `curl http://localhost:11434/api/tags`

**Expected output when working:**
```json
{"models":[{"name":"llama2:latest"}]}
```

### 2.2 Supabase (Database & Auth)
**Status:** REQUIRED - Account needed, schema not created

1. [ ] Create Supabase account: https://app.supabase.com/sign-up
2. [ ] Create new project named "aura-pilot"
3. [ ] Wait for project initialization (2-3 minutes)
4. [ ] Go to Settings → API
5. [ ] Copy these values to `.env`:
   - **SUPABASE_URL** ← Project URL
   - **SUPABASE_KEY** ← anon public key
   - **SUPABASE_SERVICE_ROLE_KEY** ← service_role secret

**File to update:** `C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend\.env`

Example:
```
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 2.3 Create Supabase Database Schema
**Status:** REQUIRED - Not yet created

1. [ ] Go to Supabase Dashboard → SQL Editor
2. [ ] Click "New Query"
3. [ ] Copy contents from: `C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend\migrations\supabase_schema.sql`
4. [ ] Paste into SQL editor
5. [ ] Click "Run"
6. [ ] Verify these tables exist:
   - `users`
   - `chat_messages`
   - `documents`

**Verify tables exist:**
- Go to Supabase Dashboard → Tables
- Should see: users, chat_messages, documents

### 2.4 Pinecone (Vector Database)
**Status:** REQUIRED - Account needed, index not created

1. [ ] Create Pinecone account: https://app.pinecone.io/sign-up
2. [ ] Create a new index with these settings:
   - **Name:** `aura-pilot`
   - **Dimension:** 384
   - **Metric:** cosine
   - **Pod Type:** starter
3. [ ] Wait for index to be ready (1-2 minutes)
4. [ ] Go to API Keys section
5. [ ] Copy API key and environment to `.env`:
   - **PINECONE_API_KEY** ← Your API key
   - **PINECONE_ENVIRONMENT** ← Your region (e.g., us-west1-gcp)

**File to update:** `C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend\.env`

Example:
```
PINECONE_API_KEY=your-api-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=aura-pilot
PINECONE_INDEX_DIMENSION=384
```

---

## Phase 3: Configuration Files ⏳

### 3.1 Create .env File
**Status:** REQUIRED - File doesn't exist yet

1. [ ] Copy template: `C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend\.env.example`
2. [ ] Save as: `C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend\.env`
3. [ ] Fill in ALL values (see below)

**Generate SECRET_KEY (required):**

On Windows PowerShell:
```powershell
[System.Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)).ToLower()
```

**Complete .env file template:**
```
# Supabase Configuration
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...

# Pinecone Configuration
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=aura-pilot
PINECONE_INDEX_DIMENSION=384

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# RAG Configuration
RAG_CHUNK_SIZE=512
RAG_CHUNK_OVERLAP=50
RAG_TOP_K=5
RAG_MIN_RELEVANCE_SCORE=0.5

# JWT Security (GENERATE USING COMMAND ABOVE)
SECRET_KEY=your-generated-hex-string-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_V1_STR=/api/v1
PROJECT_NAME=AuraPilot
PROJECT_VERSION=0.1.0

# CORS
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Logging
LOG_LEVEL=INFO
```

---

## Phase 4: Backend Startup ⏳

### 4.1 Verify All Imports Work
**Status:** PENDING

Run this command to check for import errors:
```powershell
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend
python -c "from app.main import app; print('✓ All imports successful')"
```

### 4.2 Start FastAPI Server
**Status:** PENDING

```powershell
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

**Access points:**
- API: http://localhost:8000
- API Docs (Swagger): http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Phase 5: Test the Application ⏳

### 5.1 Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "service": "AuraPilot"}
```

### 5.2 Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "StrongPassword123!",
    "full_name": "Test User"
  }'
```

Expected response:
```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "is_active": true,
  "created_at": "2025-12-10T...",
  "updated_at": "2025-12-10T..."
}
```

### 5.3 Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=StrongPassword123!"
```

Expected response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Save the access_token from response - you'll need it for next steps!**

### 5.4 Get Current User (Verify JWT Works)
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

Expected response:
```json
{
  "id": 1,
  "email": "test@example.com",
  "username": "testuser",
  ...
}
```

### 5.5 Upload a Document
1. [ ] Create a test file: `test.txt` with some content
2. [ ] Run:
```bash
curl -X POST http://localhost:8000/api/v1/documents/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -F "file=@test.txt"
```

Expected response:
```json
{
  "id": 1,
  "user_id": 1,
  "filename": "test.txt",
  "file_size": 1234,
  "status": "processing",
  "created_at": "2025-12-10T..."
}
```

**Note:** Wait 5-10 seconds for document to be indexed

### 5.6 Query with RAG
```bash
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is in my document?",
    "include_sources": true,
    "temperature": 0.7
  }'
```

Expected response:
```json
{
  "message_id": 1,
  "query": "What is in my document?",
  "response": "Based on your document, ...",
  "sources": [
    {
      "document_id": 1,
      "filename": "test.txt",
      "relevance_score": 0.85
    }
  ]
}
```

---

## Phase 6: Troubleshooting ⚠️

### Issue: "Connection refused" to Ollama
**Solution:**
1. Check if Ollama is running: `curl http://localhost:11434/api/tags`
2. If not, run: `ollama serve`
3. Pull model: `ollama pull llama2`

### Issue: Supabase connection error
**Solution:**
1. Check `.env` has correct `SUPABASE_URL` and `SUPABASE_KEY`
2. Verify Supabase project is active (check dashboard)
3. Verify tables exist in Supabase (SQL Editor)

### Issue: Import errors (pinecone, supabase, etc.)
**Solution:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: "Module not found: supabase"
**Solution:**
```powershell
pip install supabase==2.0.6 postgrest-py==0.15.0
```

### Issue: JWT token validation fails
**Solution:**
1. Generate new SECRET_KEY using command above
2. Update `.env` file
3. Restart FastAPI server

### Issue: Document indexing fails (status: "failed")
**Solution:**
1. Check error message: `GET /api/v1/documents/1`
2. Verify Pinecone index exists and is ready
3. Check `PINECONE_API_KEY` and `PINECONE_ENVIRONMENT` in `.env`

---

## Quick Start Summary (Step-by-Step)

If you just want to get it running:

### Step 1: Install Dependencies (5 minutes)
```powershell
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Setup Ollama (10 minutes)
```powershell
# Download from https://ollama.ai/download and install
# Then run:
ollama serve
# In another terminal:
ollama pull llama2
```

### Step 3: Setup Supabase (5 minutes)
- Go to https://app.supabase.com
- Create project "aura-pilot"
- Get credentials from Settings → API
- Paste into `.env` file

### Step 4: Create Database Schema (2 minutes)
- Go to Supabase SQL Editor
- Copy contents of `migrations/supabase_schema.sql`
- Click Run

### Step 5: Setup Pinecone (5 minutes)
- Go to https://app.pinecone.io
- Create index: name=`aura-pilot`, dimension=384, metric=cosine
- Get API key and environment
- Paste into `.env` file

### Step 6: Generate SECRET_KEY (1 minute)
```powershell
[System.Convert]::ToHexString([System.Security.Cryptography.RandomNumberGenerator]::GetBytes(32)).ToLower()
```
- Copy output to `.env` as `SECRET_KEY`

### Step 7: Start Backend (1 minute)
```powershell
cd C:\Users\rashm\OneDrive\Desktop\Javis-Bot\backend
venv\Scripts\activate
uvicorn app.main:app --reload
```

### Step 8: Test API (2 minutes)
- Go to http://localhost:8000/docs
- Test endpoints using Swagger UI
- Or use curl commands from Phase 5 above

---

## File Locations Reference

| File | Location | Purpose |
|------|----------|---------|
| `.env` | `backend/.env` | Environment variables (CREATE THIS) |
| `.env.example` | `backend/.env.example` | Template for .env |
| `requirements.txt` | `backend/requirements.txt` | Python dependencies |
| `supabase_schema.sql` | `backend/migrations/supabase_schema.sql` | Database schema |
| `main.py` | `backend/app/main.py` | FastAPI app entry point |
| `config.py` | `backend/app/core/config.py` | Settings & configuration |
| API docs | http://localhost:8000/docs | Interactive API documentation |

---

## Architecture Reminder

```
User Request
    ↓
FastAPI Server (localhost:8000)
    ↓
Supabase (PostgreSQL) ← User data, chat history, documents
    ↓
Pinecone (Vector DB) ← Document embeddings
    ↓
Ollama (LLaMA2) ← AI model for generation
```

---

## Success Criteria

✅ You know AuraPilot is working when:

1. [ ] Ollama is running and responds to health check
2. [ ] Supabase project is created and schema is initialized
3. [ ] Pinecone index is created and ready
4. [ ] `.env` file exists with all values filled
5. [ ] FastAPI starts without errors: `uvicorn app.main:app --reload`
6. [ ] Can register a user at `/api/v1/auth/register`
7. [ ] Can login and get JWT token at `/api/v1/auth/login`
8. [ ] Can upload a document at `/api/v1/documents/upload`
9. [ ] Can query with RAG at `/api/v1/chat/query`
10. [ ] API documentation loads at http://localhost:8000/docs

---

## Next Steps After Getting It Working

- [ ] Build frontend (React/Next.js) to consume API
- [ ] Add more document types (Word, Excel, etc.)
- [ ] Implement streaming responses
- [ ] Add rate limiting
- [ ] Deploy to production (Render, Railway, Heroku, etc.)
- [ ] Setup monitoring and logging
- [ ] Add user preferences and settings
- [ ] Implement conversation threading

---

**Questions? Check:**
- `SUPABASE_SETUP.md` - Detailed Supabase guide
- `ARCHITECTURE.md` - System architecture details
- `README.md` - Project overview
- API docs at http://localhost:8000/docs (when running)
