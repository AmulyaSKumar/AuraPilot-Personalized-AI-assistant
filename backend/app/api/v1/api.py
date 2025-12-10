# API router
from fastapi import APIRouter

from app.api.v1.endpoints import auth_simple as auth, chat_simple as chat, documents_simple as documents

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])