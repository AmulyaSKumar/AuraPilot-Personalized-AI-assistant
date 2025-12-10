# Simple Authentication endpoints (no complex password hashing)
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from datetime import timedelta
from jose import jwt
from app.core.config import settings

router = APIRouter()

# Simple models
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

# Simple in-memory store for testing
users_db = {}
next_user_id = 1

def create_token(user_id: int, username: str) -> str:
    """Create simple JWT token"""
    payload = {"sub": str(user_id), "username": username}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return token

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(user_in: UserCreate):
    """Register new user - simple version"""
    global next_user_id
    
    # Check if user exists
    for user in users_db.values():
        if user["username"] == user_in.username or user["email"] == user_in.email:
            raise HTTPException(status_code=400, detail="User already exists")
    
    # Create user
    user_id = next_user_id
    next_user_id += 1
    
    users_db[user_id] = {
        "id": user_id,
        "email": user_in.email,
        "username": user_in.username,
        "password": user_in.password,  # Store plaintext (for testing only!)
        "full_name": user_in.full_name
    }
    
    user = users_db[user_id]
    token = create_token(user_id, user_in.username)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user)
    )

@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login - simple version"""
    # Find user by username
    user = None
    for u in users_db.values():
        if u["username"] == request.username:
            user = u
            break
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Simple password check
    if user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_token(user["id"], user["username"])
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse(**user)
    )

@router.get("/me", response_model=UserResponse)
async def get_me(token: str = None):
    """Get current user - simple version"""
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = int(payload.get("sub"))
        
        if user_id not in users_db:
            raise HTTPException(status_code=404, detail="User not found")
        
        return UserResponse(**users_db[user_id])
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/logout")
async def logout():
    """Logout - simple version"""
    return {"message": "Logged out successfully"}
