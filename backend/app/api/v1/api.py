# API router
from fastapi import APIRouter

from app.api.v1.endpoints import auth_with_supabase as auth, chat_with_ollama as chat, documents_with_pinecone as documents

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])