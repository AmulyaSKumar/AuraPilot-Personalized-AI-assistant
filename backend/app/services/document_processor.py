# Document Processing Service
import logging
from typing import List, Tuple
import re

logger = logging.getLogger(__name__)

# Try to import PyPDF2
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available")

from app.core.config import settings


class TextChunk:
    """Represents a chunk of text from a document"""

    def __init__(self, text: str, chunk_id: int, source: str):
        self.text = text
        self.chunk_id = chunk_id
        self.source = source

    def to_dict(self):
        return {
            "text": self.text,
            "chunk_id": self.chunk_id,
            "source": self.source,
        }


class DocumentProcessor:
    """Service for processing documents"""

    def __init__(self):
        self.chunk_size = settings.RAG_CHUNK_SIZE
        self.chunk_overlap = settings.RAG_CHUNK_OVERLAP

    def extract_text_from_pdf(self, file_path: str = None, file_content: bytes = None) -> str:
        """Extract text from PDF file"""
        if not PYPDF2_AVAILABLE:
            logger.error("PyPDF2 not available for PDF extraction")
            return ""
            
        try:
            text = ""
            if file_content:
                from io import BytesIO
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            else:
                with open(file_path, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return ""

    def extract_text_from_file(self, file_path: str = None, file_type: str = "txt", file_content: bytes = None) -> str:
        """Extract text from file"""
        try:
            if file_type.lower() == "pdf":
                return self.extract_text_from_pdf(file_path=file_path, file_content=file_content)
            elif file_type.lower() in ["txt", "md", "text"]:
                if file_content:
                    return file_content.decode("utf-8")
                else:
                    with open(file_path, "r", encoding="utf-8") as file:
                        return file.read()
            else:
                logger.warning(f"Unsupported file type: {file_type}")
                return ""
        except Exception as e:
            logger.error(f"Error extracting text: {str(e)}")
            return ""
    
    def extract_text(self, file_content: bytes, filename: str) -> str:
        """Extract text from file content (bytes)"""
        file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "txt"
        return self.extract_text_from_file(file_type=file_ext, file_content=file_content)

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        # Remove special characters but keep punctuation
        text = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]", "", text)
        return text.strip()

    def chunk_text(self, text: str, source: str = "document") -> List[str]:
        """
        Split text into overlapping chunks
        
        Args:
            text: Text to chunk
            source: Source document name
            
        Returns:
            List of text chunks (strings)
        """
        # Clean text
        text = self.clean_text(text)
        
        if not text:
            logger.warning("Empty text after cleaning")
            return []

        # Split by sentences for better context preservation
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_chunk = ""

        for sentence in sentences:
            # Add sentence to current chunk
            test_chunk = current_chunk + " " + sentence if current_chunk else sentence

            # Check if adding this sentence exceeds chunk size
            if len(test_chunk.split()) > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())

                # Start new chunk with overlap
                current_chunk = sentence
            else:
                current_chunk = test_chunk

        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        logger.info(f"Created {len(chunks)} chunks from document '{source}'")
        return chunks


# Singleton instance
document_processor = DocumentProcessor()
