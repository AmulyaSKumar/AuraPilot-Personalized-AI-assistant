# AuraPilot (Javis-Bot)

🎯 **AuraPilot** is an AI-powered document intelligence assistant — upload documents, index them, and ask natural-language questions that are answered using Retrieval-Augmented Generation (RAG).

---

## 🚀 Quick Overview
- **Backend:** FastAPI (Python) serving REST endpoints and document processing, embeddings, and RAG flow.
- **Frontend:** Vite + React + shadcn/ui (TypeScript) providing a modern UI for login, document upload, and chat.
- **Vector DB:** Pinecone (serverless indices) for storing embeddings and performing semantic search.
- **Database:** Supabase for user and document metadata.
- **Embeddings:** `sentence-transformers` (model configurable via ENV); fallback to mock embeddings for local dev.
- **LLM:** Ollama (local LLM) used for generating responses using RAG contexts.

---

## 🧭 Architecture & Workflow
1. User uploads a document via the frontend.
2. Backend (`DocumentProcessor`) extracts and chunks text from the document.
3. Each chunk is embedded via `embedding_service`.
4. Vectors + metadata are upserted into Pinecone, partitioned by user namespace (e.g., `user_1`).
5. Document metadata is stored in Supabase for listing and tracking status.
6. When a user asks a query:
   - Query embedding is generated
   - Pinecone is queried for the top-K similar chunks
   - Chunks are concatenated into a context (bounded by `MAX_CONTEXT_LENGTH`)
   - The context and query are sent to the LLM (Ollama) to generate the final answer

---

## 🛠️ Getting Started (Local Development)
### Prerequisites
- Node.js (recommended), npm or bun
- Python 3.11+
- A Pinecone account (API key) — optional for local dev
- Supabase project (optional for metadata persistence)
- Ollama running locally for LLM (or configure alternative)

### Backend
1. Create a virtual env and activate it

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy `.env.example` (or create `.env`) and set environment variables (see ENV section below).
3. Start the backend:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Frontend
```bash
cd verdant-ai-chat
npm install
# or use bun: bun install
npx vite
# open http://localhost:8080
```

---

## ⚙️ Environment Variables (important ones)
- `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_ROLE_KEY`
- `PINECONE_API_KEY`, `PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`, `PINECONE_INDEX_DIMENSION`
- `OLLAMA_API_URL`, `OLLAMA_MODEL`
- `EMBEDDING_MODEL` (default `all-MiniLM-L6-v2`)

These are defined in `backend/.env` and loaded by `pydantic-settings`.

---

## 🔎 Useful Endpoints
- Document upload: `POST /api/v1/documents/upload`
- List documents: `GET /api/v1/documents?user_id=1`
- Pinecone health/status: `GET /api/v1/documents/health/pinecone-status`

---

## 🧪 Testing
Run backend tests with:

```bash
cd backend
pytest
```

---

## 🧑‍💻 Development Notes & Tips
- Pinecone initialization logs will indicate whether vectors are being stored (check `pinecone_service.initialized`).
- If `sentence-transformers` isn't installed or available, the app falls back to mock embeddings for local testing.
- When working with Pinecone, confirm index name and dimension match the embeddings.
- Use Supabase as the source of truth for document metadata — there is an in-memory fallback in `documents_db` for quick testing.

---

## 📦 Project Structure (high-level)
- `backend/` — FastAPI server: app code, services, DB models, tests
- `verdant-ai-chat/` — Frontend: Vite + React app
- `README.md` — This file
- `SETUP_CHECKLIST.md` / `FRONTEND_GUIDE.md` — More detailed guides

---

## 🤝 Contributing
- Open issues for bugs or feature requests
- Fork, branch, and open a PR for review
- Keep commits small and focused

---

## 📄 License
MIT (add LICENSE file if required)

---

If you'd like, I can expand any section (e.g., add deployment steps or a sequence diagram for the RAG flow). 🚀
