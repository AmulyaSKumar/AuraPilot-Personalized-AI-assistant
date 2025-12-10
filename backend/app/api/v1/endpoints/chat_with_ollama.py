# Chat endpoints with Ollama LLM
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from typing import List
import httpx
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory chat storage
chats_db = {}

class ChatQueryRequest(BaseModel):
    query: str
    user_id: int = 1
    temperature: float = 0.7

class ChatResponse(BaseModel):
    response: str
    sources: List[dict] = []

async def call_ollama(prompt: str, temperature: float = 0.7) -> str:
    """Call Ollama API to get LLM response"""
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{settings.OLLAMA_API_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature
                    }
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("response", "No response from model")
            else:
                logger.error(f"Ollama error: {response.status_code} - {response.text}")
                return f"Error from Ollama: {response.status_code}"
    except httpx.ConnectError:
        logger.error("Cannot connect to Ollama. Is it running?")
        return "Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)"
    except Exception as e:
        logger.error(f"Ollama error: {str(e)}")
        return f"Error: {str(e)}"

@router.post("/query", response_model=ChatResponse)
async def query_chat(request: ChatQueryRequest):
    """Send a chat query - uses Ollama LLM"""
    user_id = request.user_id
    
    # Initialize user chat if not exists
    if user_id not in chats_db:
        chats_db[user_id] = []
    
    # Build prompt with context
    system_prompt = """You are AuraPilot, a helpful AI assistant. 
You help users with their questions in a friendly and informative way.
Be concise but thorough in your responses."""
    
    # Include recent chat history for context
    history = ""
    recent_messages = chats_db[user_id][-6:]  # Last 3 exchanges
    for msg in recent_messages:
        if msg["role"] == "user":
            history += f"User: {msg['content']}\n"
        else:
            history += f"Assistant: {msg['content']}\n"
    
    full_prompt = f"""{system_prompt}

{history}User: {request.query}
Assistant:"""
    
    # Get response from Ollama
    response_text = await call_ollama(full_prompt, request.temperature)
    
    # Store messages
    chats_db[user_id].append({
        "role": "user",
        "content": request.query
    })
    chats_db[user_id].append({
        "role": "assistant",
        "content": response_text,
        "sources": []
    })
    
    return ChatResponse(response=response_text, sources=[])

@router.get("/messages")
async def get_messages(user_id: int = Query(1)):
    """Get chat history"""
    if user_id not in chats_db:
        return []
    return chats_db[user_id]

@router.delete("/history")
async def clear_history(user_id: int = Query(1)):
    """Clear chat history"""
    if user_id in chats_db:
        chats_db[user_id] = []
    return {"message": "Chat history cleared"}

@router.get("/messages/{message_id}")
async def get_message_detail(message_id: int):
    """Get message detail"""
    return {"message_id": message_id, "detail": "Message detail"}
