# Embedding Service
import logging
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using mock embeddings")


class EmbeddingService:
    """Service for generating text embeddings"""

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL
        self.dimension = settings.EMBEDDING_DIMENSION
        self.model = None

        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"✓ Embedding model loaded successfully: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.model = None
        else:
            logger.warning("Using mock embeddings - install sentence-transformers for real embeddings")

    def encode_single(self, text: str) -> Optional[List[float]]:
        """Generate embedding for a single text"""
        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            if self.model is not None:
                embedding = self.model.encode(text, convert_to_numpy=True)
                result = embedding.tolist()
                logger.debug(f"Generated embedding of dimension {len(result)}")
                return result
            else:
                # Mock embedding for testing (returns zero vector)
                logger.warning("Using mock embedding (model not available)")
                return [0.0] * self.dimension
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None

    def encode_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """Generate embeddings for multiple texts"""
        if not texts:
            return []

        try:
            if self.model is not None:
                embeddings = self.model.encode(texts, convert_to_numpy=True)
                return [emb.tolist() for emb in embeddings]
            else:
                # Mock embeddings
                logger.warning("Using mock embeddings (model not available)")
                return [[0.0] * self.dimension for _ in texts]
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            return [None] * len(texts)


# Singleton instance
embedding_service = EmbeddingService()
