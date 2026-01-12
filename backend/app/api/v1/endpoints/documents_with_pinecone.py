# Document endpoints with Pinecone vector storage
from fastapi import APIRouter, UploadFile, File, Query, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid
import logging
from datetime import datetime

from app.services.document_processor import DocumentProcessor
from app.services.embedding import embedding_service
from app.services.vector_store import pinecone_service
from app.core.supabase import SupabaseService

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory document store (backup)
documents_db = {}

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

async def process_and_index_document(
    doc_id: str, 
    content: bytes, 
    filename: str, 
    user_id: int
):
    """Background task to process document and store in Pinecone"""
    try:
        logger.info(f"=== Starting document processing: {filename} ===")
        
        # Process document into chunks
        processor = DocumentProcessor()
        text = processor.extract_text(content, filename)
        
        if not text:
            logger.error(f"No text extracted from {filename}")
            _update_doc_status(user_id, doc_id, "failed", 0)
            return
            
        logger.info(f"Extracted {len(text)} chars from {filename}")
        
        chunks = processor.chunk_text(text, source=filename)
        
        if not chunks:
            logger.error(f"No chunks created from {filename}")
            _update_doc_status(user_id, doc_id, "failed", 0)
            return
            
        logger.info(f"Created {len(chunks)} chunks from {filename}")
        
        # Generate embeddings for each chunk
        vectors = []
        metadata_list = []
        
        for i, chunk in enumerate(chunks):
            embedding = embedding_service.encode_single(chunk)
            if embedding:
                vec_id = f"{doc_id}_chunk_{i}"
                vectors.append((vec_id, embedding))
                metadata_list.append({
                    "text": chunk,
                    "source": filename,
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "user_id": str(user_id)
                })
                logger.debug(f"Embedded chunk {i}: {len(embedding)} dims")
            else:
                logger.warning(f"Failed to embed chunk {i}")
        
        logger.info(f"Generated {len(vectors)} embeddings for {filename}")
        
        if not vectors:
            logger.error(f"No embeddings generated for {filename}")
            _update_doc_status(user_id, doc_id, "failed", 0)
            return
        
        # Store in Pinecone
        namespace = f"user_{user_id}"
        logger.info(f"Upserting {len(vectors)} vectors to namespace '{namespace}'")
        
        success = pinecone_service.upsert_vectors(
            vectors=vectors,
            namespace=namespace,
            metadata=metadata_list
        )
        
        # Update document status
        status = "indexed" if success else "failed"
        _update_doc_status(user_id, doc_id, status, len(chunks))
        
        if success:
            logger.info(f"✓ Document {filename} indexed successfully with {len(chunks)} chunks")
        else:
            logger.error(f"✗ Failed to index document {filename}")
        
    except Exception as e:
        logger.error(f"Error processing document {filename}: {str(e)}")
        _update_doc_status(user_id, doc_id, "failed", 0)


def _update_doc_status(user_id: int, doc_id: str, status: str, chunk_count: int):
    """Update document status in memory and Supabase"""
    # Update in-memory
    if user_id in documents_db:
        for doc in documents_db[user_id]:
            if doc["id"] == doc_id:
                doc["status"] = status
                doc["chunk_count"] = chunk_count
                break
    
    # Update in Supabase
    try:
        client = SupabaseService.get_client()
        client.table("documents").update({
            "status": status,
            "chunk_count": chunk_count
        }).eq("id", doc_id).execute()
    except Exception as e:
        logger.warning(f"Failed to update Supabase: {e}")


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...), 
    user_id: int = Query(1)
):
    """Upload document and index to Pinecone vector DB"""
    if not file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Initialize user docs if not exists
    if user_id not in documents_db:
        documents_db[user_id] = []
    
    # Create document entry
    doc_id = str(uuid.uuid4())
    content = await file.read()
    created_at = datetime.utcnow().isoformat()
    
    doc = {
        "id": doc_id,
        "filename": file.filename,
        "file_size": len(content),
        "status": "processing",
        "chunk_count": 0,
        "created_at": created_at,
        "file_type": file.content_type
    }
    
    documents_db[user_id].append(doc)
    
    # Store in Supabase
    try:
        client = SupabaseService.get_client()
        client.table("documents").insert([{
            "id": doc_id,
            "user_id": user_id,
            "filename": file.filename,
            "file_size": len(content),
            "status": "processing",
            "chunk_count": 0
        }]).execute()
    except Exception as e:
        logger.warning(f"Failed to store in Supabase: {e}")
    
    # Process document in background
    background_tasks.add_task(
        process_and_index_document,
        doc_id,
        content,
        file.filename,
        user_id
    )
    
    logger.info(f"Document upload started: {file.filename} (id: {doc_id})")
    
    return DocumentResponse(**doc)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(user_id: int = Query(1), skip: int = 0, limit: int = 50):
    """List user's documents"""
    # Try Supabase first
    try:
        client = SupabaseService.get_client()
        response = client.table("documents").select("*").eq("user_id", user_id).execute()
        if response.data:
            docs = [DocumentResponse(
                id=d["id"],
                filename=d["filename"],
                file_size=d["file_size"],
                status=d["status"],
                chunk_count=d.get("chunk_count", 0),
                created_at=d.get("created_at", "")
            ) for d in response.data[skip:skip+limit]]
            return DocumentListResponse(documents=docs, total=len(response.data))
    except Exception as e:
        logger.warning(f"Supabase fetch failed: {e}")
    
    # Fallback to in-memory
    if user_id not in documents_db:
        return DocumentListResponse(documents=[], total=0)
    
    docs = documents_db[user_id][skip:skip+limit]
    return DocumentListResponse(
        documents=[DocumentResponse(**doc) for doc in docs],
        total=len(documents_db[user_id])
    )


@router.get("/health/pinecone-status")
async def check_pinecone_status():
    """Check if Pinecone is properly initialized"""
    return {
        "pinecone_initialized": pinecone_service.initialized,
        "pinecone_api_key_set": bool(pinecone_service.api_key),
        "pinecone_index_name": pinecone_service.index_name,
        "pinecone_dimension": pinecone_service.dimension,
        "embedding_model_loaded": embedding_service.model is not None,
        "status": "✓ Ready" if pinecone_service.initialized else "✗ NOT Ready",
        "stats": pinecone_service.get_stats() if pinecone_service.initialized else {}
    }


@router.get("/{doc_id}")
async def get_document_detail(doc_id: str, user_id: int = Query(1)):
    """Get document detail"""
    try:
        client = SupabaseService.get_client()
        response = client.table("documents").select("*").eq("id", doc_id).execute()
        if response.data:
            return response.data[0]
    except Exception as e:
        logger.warning(f"Supabase fetch failed: {e}")
    
    # Fallback to in-memory
    if user_id in documents_db:
        for doc in documents_db[user_id]:
            if doc["id"] == doc_id:
                return DocumentResponse(**doc)
    
    raise HTTPException(status_code=404, detail="Document not found")


@router.delete("/{doc_id}")
async def delete_document(doc_id: str, user_id: int = Query(1)):
    """Delete document and its vectors from Pinecone"""
    # Delete from Pinecone
    try:
        namespace = f"user_{user_id}"
        pinecone_service.delete_by_prefix(doc_id, namespace)
    except Exception as e:
        logger.warning(f"Failed to delete from Pinecone: {e}")
    
    # Delete from Supabase
    try:
        client = SupabaseService.get_client()
        client.table("documents").delete().eq("id", doc_id).execute()
    except Exception as e:
        logger.warning(f"Supabase delete failed: {e}")
    
    # Delete from memory
    if user_id in documents_db:
        documents_db[user_id] = [doc for doc in documents_db[user_id] if doc["id"] != doc_id]
    
    return {"message": "Document deleted"}
