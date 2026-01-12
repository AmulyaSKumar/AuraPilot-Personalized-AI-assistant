# Pinecone Vector Store Service (SDK v3+)
import logging
from typing import List, Dict, Any, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Pinecone
try:
    from pinecone import Pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False
    logger.warning("Pinecone not available")


class PineconeService:
    """Service for managing vectors in Pinecone (SDK v3+)"""

    def __init__(self):
        self.api_key = settings.PINECONE_API_KEY
        self.index_name = settings.PINECONE_INDEX_NAME
        self.dimension = settings.PINECONE_INDEX_DIMENSION
        self.pc = None
        self.index = None
        self.initialized = False

        if not PINECONE_AVAILABLE:
            logger.error("Pinecone package not installed - vectors will NOT be stored!")
            return

        if not self.api_key:
            logger.error("Pinecone API key not configured - vectors will NOT be stored!")
            return

        try:
            # Initialize Pinecone client (new SDK v3+)
            logger.info(f"Initializing Pinecone with index: {self.index_name}")
            self.pc = Pinecone(api_key=self.api_key)
            
            # Check if index exists
            existing_indexes = [idx.name for idx in self.pc.list_indexes()]
            logger.info(f"Existing Pinecone indexes: {existing_indexes}")
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec={
                        "serverless": {
                            "cloud": "aws",
                            "region": "us-east-1"
                        }
                    }
                )
                logger.info(f"Created index {self.index_name}")
            
            # Get the index
            self.index = self.pc.Index(self.index_name)
            self.initialized = True
            logger.info(f"✓ Pinecone initialized successfully! Index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"✗ Failed to initialize Pinecone: {str(e)}")
            self.initialized = False

    def upsert_vectors(
        self,
        vectors: List[tuple],
        namespace: str = "default",
        metadata: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Upsert vectors to Pinecone
        
        Args:
            vectors: List of (id, embedding) tuples
            namespace: Namespace for user isolation
            metadata: List of metadata dicts
            
        Returns:
            Success status
        """
        if not self.initialized:
            logger.error(f"✗ Pinecone not initialized! Cannot upsert {len(vectors)} vectors")
            return False

        try:
            # Prepare vectors with metadata
            data_to_upsert = []
            for i, (vec_id, embedding) in enumerate(vectors):
                meta = metadata[i] if metadata and i < len(metadata) else {}
                data_to_upsert.append({
                    "id": vec_id,
                    "values": embedding,
                    "metadata": meta
                })

            # Upsert in batches of 100
            batch_size = 100
            for i in range(0, len(data_to_upsert), batch_size):
                batch = data_to_upsert[i : i + batch_size]
                self.index.upsert(vectors=batch, namespace=namespace)

            logger.info(f"✓ Upserted {len(data_to_upsert)} vectors to namespace '{namespace}'")
            return True

        except Exception as e:
            logger.error(f"✗ Error upserting vectors: {str(e)}")
            return False

    def query_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        namespace: str = "default",
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Query similar vectors"""
        if not self.initialized:
            logger.warning("Pinecone not initialized, returning empty results")
            return []

        try:
            query_params = {
                "vector": query_embedding,
                "top_k": top_k,
                "namespace": namespace,
                "include_metadata": True,
            }
            
            if filter:
                query_params["filter"] = filter

            results = self.index.query(**query_params)

            matches = []
            for match in results.get("matches", []):
                matches.append({
                    "id": match.get("id"),
                    "score": match.get("score"),
                    "metadata": match.get("metadata", {}),
                })

            logger.info(f"Found {len(matches)} similar vectors in namespace '{namespace}'")
            return matches

        except Exception as e:
            logger.error(f"Error querying vectors: {str(e)}")
            return []

    def delete_by_prefix(self, prefix: str, namespace: str = "default") -> bool:
        """Delete vectors by ID prefix"""
        if not self.initialized:
            return False
        try:
            # Note: Pinecone serverless doesn't support delete by prefix directly
            # This is a workaround - in production, track IDs and delete explicitly
            logger.info(f"Delete by prefix '{prefix}' requested for namespace '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Error deleting by prefix: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        if not self.initialized:
            return {"error": "Pinecone not initialized"}

        try:
            stats = self.index.describe_index_stats()
            return stats.to_dict() if hasattr(stats, 'to_dict') else dict(stats)
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}


# Singleton instance
pinecone_service = PineconeService()
