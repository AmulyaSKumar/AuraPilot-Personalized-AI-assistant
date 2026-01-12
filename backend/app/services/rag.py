# RAG (Retrieval-Augmented Generation) Pipeline
import logging
from typing import List, Dict, Any, Optional, Union

from app.core.config import settings
from app.services.embedding import embedding_service
from app.services.vector_store import pinecone_service
from app.services.llm import ollama_service

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    Retrieval-Augmented Generation pipeline that combines
    document retrieval with LLM generation
    """

    def __init__(self):
        self.top_k = settings.RAG_TOP_K
        self.max_context_length = settings.MAX_CONTEXT_LENGTH

    async def generate_response(
        self,
        query: str,
        user_id: Union[str, int],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Generate a response using RAG pipeline
        
        Args:
            query: User query
            user_id: User ID for namespace isolation
            system_prompt: Optional system prompt
            temperature: Generation temperature
            
        Returns:
            Response with answer and sources
        """
        try:
            # Step 1: Generate query embedding
            logger.info(f"Generating embedding for query: {query[:50]}...")
            query_embedding = embedding_service.encode_single(query)
            if not query_embedding:
                return {
                    "response": "Error: Could not process query",
                    "sources": [],
                    "error": "Embedding generation failed",
                }

            # Step 2: Search for relevant documents
            user_namespace = f"user_{user_id}"
            logger.info(f"Searching Pinecone namespace: {user_namespace}")
            search_results = pinecone_service.query_similar(
                query_embedding=query_embedding,
                top_k=self.top_k,
                namespace=user_namespace,
            )

            # Step 3: Build context from search results
            context_chunks = []
            sources = []
            total_length = 0

            for result in search_results:
                metadata = result.get("metadata", {})
                chunk_text = metadata.get("text", "")
                source = metadata.get("source", "Unknown")

                # Check if adding this chunk exceeds max context length
                if total_length + len(chunk_text.split()) > self.max_context_length:
                    break

                context_chunks.append(chunk_text)
                sources.append(f"{source} (relevance: {result.get('score', 0):.2f})")
                total_length += len(chunk_text.split())

            # Step 4: Build prompt with context
            if context_chunks:
                context = "\n\n".join(context_chunks)
                augmented_prompt = f"""Use the following context to answer the question. If the context doesn't contain relevant information, say so.

Context:
{context}

Question: {query}

Answer:"""
            else:
                augmented_prompt = f"""I don't have any documents to reference for this question. Please upload relevant documents first.

Question: {query}

Answer: I don't have access to any uploaded documents to answer your question. Please upload some documents first, and then I can help you find information from them."""
                logger.warning("No context found for query")

            # Step 5: Generate response using LLM
            logger.info("Generating response with Ollama")
            llm_response = await ollama_service.generate(
                prompt=augmented_prompt,
                system_prompt=system_prompt or "You are a helpful AI assistant that answers questions based on the provided context.",
                temperature=temperature,
            )

            return {
                "response": llm_response.get("response", "Error generating response"),
                "sources": sources,
                "context_used": len(context_chunks) > 0,
            }

        except Exception as e:
            logger.error(f"RAG pipeline error: {str(e)}")
            return {
                "response": f"Error: {str(e)}",
                "sources": [],
                "error": str(e),
            }


# Singleton instance
rag_pipeline = RAGPipeline()
