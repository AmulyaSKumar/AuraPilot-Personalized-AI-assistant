# Simple Document endpoints (no complex auth)
from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid

router = APIRouter()

# In-memory document store
documents_db = {}  # user_id -> [documents]

class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_size: int
    status: str
    chunk_count: int
    created_at: str

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int

@router.post("/upload")
async def upload_document(file: UploadFile = File(...), user_id: int = Query(1)):
    """Upload document - simple version"""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Initialize user docs if not exists
    if user_id not in documents_db:
        documents_db[user_id] = []
    
    # Create document entry
    doc_id = str(uuid.uuid4())
    content = await file.read()
    
    doc = {
        "id": doc_id,
        "filename": file.filename,
        "file_size": len(content),
        "status": "indexed",  # Simplified - no processing
        "chunk_count": 5,  # Mock chunk count
        "created_at": "2025-12-10T00:00:00Z",
        "file_type": file.content_type
    }
    
    documents_db[user_id].append(doc)
    
    return DocumentResponse(**doc)

@router.get("/", response_model=DocumentListResponse)
async def list_documents(user_id: int = Query(1), skip: int = 0, limit: int = 50):
    """List documents - simple version"""
    if user_id not in documents_db:
        return DocumentListResponse(documents=[], total=0)
    
    docs = documents_db[user_id][skip:skip+limit]
    
    return DocumentListResponse(
        documents=[DocumentResponse(**doc) for doc in docs],
        total=len(documents_db[user_id])
    )

@router.get("/{doc_id}")
async def get_document_detail(doc_id: str, user_id: int = Query(1)):
    """Get document detail - simple version"""
    if user_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    for doc in documents_db[user_id]:
        if doc["id"] == doc_id:
            return DocumentResponse(**doc)
    
    raise HTTPException(status_code=404, detail="Document not found")

@router.delete("/{doc_id}")
async def delete_document(doc_id: str, user_id: int = Query(1)):
    """Delete document - simple version"""
    if user_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    documents_db[user_id] = [doc for doc in documents_db[user_id] if doc["id"] != doc_id]
    
    return {"message": "Document deleted"}

@router.post("/{doc_id}/reindex")
async def reindex_document(doc_id: str, user_id: int = Query(1)):
    """Reindex document - simple version"""
    return {"message": "Document reindexing queued"}
