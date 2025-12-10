# Authentication endpoints with Supabase storage
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from jose import jwt
from app.core.config import settings
from app.core.supabase import SupabaseService
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

# Models
class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    full_name: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

def create_token(user_id: int, username: str) -> str:
    """Create JWT token"""
    payload = {"sub": str(user_id), "username": username}
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(user_in: UserCreate):
    """Register new user - saves to Supabase"""
    try:
        client = SupabaseService.get_client()
        
        # Check if user already exists
        existing = client.table("users").select("id").eq("email", user_in.email).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        existing = client.table("users").select("id").eq("username", user_in.username).execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create user (storing password as plain text for simplicity)
        user_data = {
            "email": user_in.email,
            "username": user_in.username,
            "hashed_password": user_in.password,  # Simple - no hashing
            "full_name": user_in.full_name,
            "is_active": True
        }
        
        response = client.table("users").insert([user_data]).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create user")
        
        user = response.data[0]
        token = create_token(user["id"], user["username"])
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                username=user["username"],
                full_name=user["full_name"]
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login user - validates against Supabase"""
    try:
        client = SupabaseService.get_client()
        
        # Find user by username
        response = client.table("users").select("*").eq("username", request.username).execute()
        
        if not response.data:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = response.data[0]
        
        # Simple password check
        if user["hashed_password"] != request.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = create_token(user["id"], user["username"])
        
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user["id"],
                email=user["email"],
                username=user["username"],
                full_name=user["full_name"]
            )
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/me", response_model=UserResponse)
async def get_me(user_id: int = 1):
    """Get current user from Supabase"""
    try:
        client = SupabaseService.get_client()
        response = client.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user = response.data[0]
        return UserResponse(
            id=user["id"],
            email=user["email"],
            username=user["username"],
            full_name=user["full_name"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get me error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def logout():
    """Logout user"""
    return {"message": "Logged out successfully"}
