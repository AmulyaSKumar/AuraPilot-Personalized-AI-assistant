# Supabase Client Service
import logging
from typing import Optional, Dict, Any, List

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Service for Supabase database operations"""

    _instance: Optional[Any] = None

    @classmethod
    def get_client(cls) -> Any:
        """Get or create Supabase client"""
        if cls._instance is None:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.error("Supabase credentials not configured")
                raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

            try:
                from supabase import create_client
                cls._instance = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized")
            except ImportError as e:
                logger.error(f"Failed to import Supabase client: {str(e)}")
                raise

        return cls._instance

    @staticmethod
    async def insert(table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into table"""
        try:
            client = SupabaseService.get_client()
            response = client.table(table).insert(data).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error inserting into {table}: {str(e)}")
            raise

    @staticmethod
    async def get(table: str, id: int) -> Optional[Dict[str, Any]]:
        """Get single record by ID"""
        try:
            client = SupabaseService.get_client()
            response = client.table(table).select("*").eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting from {table}: {str(e)}")
            return None

    @staticmethod
    async def query(table: str, **filters) -> List[Dict[str, Any]]:
        """Query table with filters"""
        try:
            client = SupabaseService.get_client()
            query = client.table(table).select("*")

            for key, value in filters.items():
                query = query.eq(key, value)

            response = query.execute()
            return response.data or []
        except Exception as e:
            logger.error(f"Error querying {table}: {str(e)}")
            return []

    @staticmethod
    async def update(table: str, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update record by ID"""
        try:
            client = SupabaseService.get_client()
            response = client.table(table).update(data).eq("id", id).execute()
            return response.data[0] if response.data else {}
        except Exception as e:
            logger.error(f"Error updating {table}: {str(e)}")
            raise

    @staticmethod
    async def delete(table: str, id: int) -> bool:
        """Delete record by ID"""
        try:
            client = SupabaseService.get_client()
            client.table(table).delete().eq("id", id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting from {table}: {str(e)}")
            return False

    @staticmethod
    async def get_by_field(table: str, field: str, value: Any) -> Optional[Dict[str, Any]]:
        """Get single record by field"""
        try:
            client = SupabaseService.get_client()
            response = client.table(table).select("*").eq(field, value).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error querying {table} by {field}: {str(e)}")
            return None


# Initialize
supabase_service = SupabaseService()
