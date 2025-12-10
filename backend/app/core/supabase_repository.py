# Supabase Repositories
import logging
from typing import Optional, List, Dict, Any

from app.core.supabase import SupabaseService
from app.core.security import get_password_hash
from app.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class SupabaseUserRepository:
    """User operations using Supabase"""

    TABLE = "users"

    @staticmethod
    async def create_user(user_in: UserCreate) -> Optional[Dict[str, Any]]:
        """Create a new user"""
        try:
            client = SupabaseService.get_client()
            user_data = {
                "email": user_in.email,
                "username": user_in.username,
                "hashed_password": get_password_hash(user_in.password),
                "full_name": user_in.full_name or "",
                "is_active": True,
            }
            response = (
                client.table(SupabaseUserRepository.TABLE)
                .insert([user_data])
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseUserRepository.TABLE)
                .select("*")
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by ID: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseUserRepository.TABLE)
                .select("*")
                .eq("email", email)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseUserRepository.TABLE)
                .select("*")
                .eq("username", username)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by username: {str(e)}")
            return None

    @staticmethod
    async def update_user(user_id: int, user_update: UserUpdate) -> Optional[Dict[str, Any]]:
        """Update user profile"""
        try:
            client = SupabaseService.get_client()
            update_data = user_update.dict(exclude_unset=True)
            response = (
                client.table(SupabaseUserRepository.TABLE)
                .update(update_data)
                .eq("id", user_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return None

    @staticmethod
    async def user_exists(email: str = None, username: str = None) -> bool:
        """Check if user exists"""
        try:
            client = SupabaseService.get_client()
            if email:
                response = (
                    client.table(SupabaseUserRepository.TABLE)
                    .select("id")
                    .eq("email", email)
                    .execute()
                )
                if response.data:
                    return True

            if username:
                response = (
                    client.table(SupabaseUserRepository.TABLE)
                    .select("id")
                    .eq("username", username)
                    .execute()
                )
                if response.data:
                    return True

            return False
        except Exception as e:
            logger.error(f"Error checking user existence: {str(e)}")
            return False

    @staticmethod
    async def delete_user(user_id: int) -> bool:
        """Delete user"""
        try:
            client = SupabaseService.get_client()
            client.table(SupabaseUserRepository.TABLE).delete().eq("id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return False


class SupabaseChatRepository:
    """Chat message operations using Supabase"""

    TABLE = "chat_messages"

    @staticmethod
    async def create_message(message_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create chat message"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseChatRepository.TABLE)
                .insert([message_data])
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating message: {str(e)}")
            return None

    @staticmethod
    async def get_user_messages(
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's messages"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseChatRepository.TABLE)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []

    @staticmethod
    async def delete_user_messages(user_id: int) -> bool:
        """Delete all messages for user"""
        try:
            client = SupabaseService.get_client()
            client.table(SupabaseChatRepository.TABLE).delete().eq("user_id", user_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting messages: {str(e)}")
            return False


class SupabaseDocumentRepository:
    """Document operations using Supabase"""

    TABLE = "documents"

    @staticmethod
    async def create_document(document_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create document record"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseDocumentRepository.TABLE)
                .insert([document_data])
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating document: {str(e)}")
            return None

    @staticmethod
    async def get_user_documents(
        user_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get user's documents"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseDocumentRepository.TABLE)
                .select("*")
                .eq("user_id", user_id)
                .order("created_at", desc=True)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting documents: {str(e)}")
            return []

    @staticmethod
    async def get_document_by_id(document_id: int) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseDocumentRepository.TABLE)
                .select("*")
                .eq("id", document_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error getting document: {str(e)}")
            return None

    @staticmethod
    async def update_document(document_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update document"""
        try:
            client = SupabaseService.get_client()
            response = (
                client.table(SupabaseDocumentRepository.TABLE)
                .update(update_data)
                .eq("id", document_id)
                .execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating document: {str(e)}")
            return None

    @staticmethod
    async def delete_document(document_id: int) -> bool:
        """Delete document"""
        try:
            client = SupabaseService.get_client()
            client.table(SupabaseDocumentRepository.TABLE).delete().eq("id", document_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}")
            return False
