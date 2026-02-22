"""
Authentication API Router

FastAPI router implementing JWT-based authentication endpoints.
Provides signup, login, and user profile retrieval.

Usage:
    from fastapi import FastAPI
    from src.api_auth import router as auth_router
    
    app = FastAPI()
    app.include_router(auth_router)
"""

import logging
import os
from datetime import datetime, timedelta
from typing import Optional, List

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.db import SessionLocal, get_db, User, hash_password, verify_password


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT configuration
SECRET_KEY = os.getenv("API_SECRET", "project149_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Security scheme for Bearer token
security = HTTPBearer()


# Pydantic schemas

class SignupIn(BaseModel):
    """
    Signup request schema.
    
    Attributes:
        email: User's email address
        password: Plain text password (will be hashed)
        name: User's display name
        preferred_categories: List of preferred product categories (1-3 required)
    """
    email: EmailStr
    password: str
    name: str
    preferred_categories: List[str]  # Required: 1-3 categories


class LoginIn(BaseModel):
    """
    Login request schema.
    
    Attributes:
        email: User's email address
        password: Plain text password
    """
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    """
    Token response schema.
    
    Attributes:
        access_token: JWT access token
        token_type: Token type (always "bearer")
    """
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    """
    User response schema.
    
    Attributes:
        id: User ID
        email: User's email address
        name: User's display name
    """
    id: int
    email: EmailStr
    name: str
    
    class Config:
        from_attributes = True


class ForgotPasswordIn(BaseModel):
    """
    Forgot password request schema.
    
    Attributes:
        email: User's email address
    """
    email: EmailStr


class ResetPasswordIn(BaseModel):
    """
    Reset password request schema.
    
    Attributes:
        email: User's email address
        new_password: New password
        reset_code: Reset verification code
    """
    email: EmailStr
    new_password: str
    reset_code: str


class ResetCodeOut(BaseModel):
    """
    Reset code response schema.
    
    Attributes:
        message: Success message
        reset_code: Temporary reset code (for demo purposes)
    """
    message: str
    reset_code: str


# Create router
router = APIRouter(prefix="/auth", tags=["auth"])


# Helper functions

def create_access_token(user_id: int) -> str:
    """
    Create JWT access token for user.
    
    Args:
        user_id: User ID to encode in token
        
    Returns:
        JWT access token string
    """
    expiry = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {
        "sub": str(user_id),
        "exp": expiry
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def decode_access_token(token: str) -> Optional[int]:
    """
    Decode JWT access token and extract user ID.
    
    Args:
        token: JWT access token string
        
    Returns:
        User ID if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
        return user_id
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid token")
        return None
    except (ValueError, TypeError):
        logger.warning("Invalid token payload")
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    token = credentials.credentials
    
    # Decode token
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user


# API endpoints

@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(signup_data: SignupIn, db: Session = Depends(get_db)):
    """
    Register a new user account with category preferences.
    
    Creates a new user with hashed password and preferred categories.
    Email must be unique. Categories are mandatory (1-3 required).
    
    Args:
        signup_data: Signup request data (email, password, name, preferred_categories)
        db: Database session
        
    Returns:
        Created user information (without password)
        
    Raises:
        HTTPException 400: If email already exists or invalid categories
    """
    # Validate categories
    if not signup_data.preferred_categories:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least 1 category must be selected"
        )
    
    if len(signup_data.preferred_categories) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 categories can be selected"
        )
    
    # Valid categories
    valid_categories = {
        "Garment Upper body",
        "Garment Lower body",
        "Garment Full body",
        "Accessories",
        "Underwear",
        "Shoes",
        "Swimwear",
        "Socks & Tights",
        "Nightwear"
    }
    
    # Validate each category
    for cat in signup_data.preferred_categories:
        if cat not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category: {cat}"
            )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == signup_data.email).first()
    if existing_user:
        logger.warning(f"Signup attempt with existing email: {signup_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password and categories
    hashed_pwd = hash_password(signup_data.password)
    new_user = User(
        email=signup_data.email,
        password_hash=hashed_pwd,
        name=signup_data.name,
        preferred_categories=",".join(signup_data.preferred_categories)  # Store as comma-separated
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id}) with categories: {new_user.preferred_categories}")
    
    return new_user


@router.post("/login", response_model=TokenOut)
def login(login_data: LoginIn, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT access token.
    
    Validates email and password, then generates a JWT token for authentication.
    
    Args:
        login_data: Login request data (email, password)
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user:
        logger.warning(f"Login attempt with non-existent email: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(login_data.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token = create_access_token(user.id)
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    
    return TokenOut(access_token=access_token)


@router.get("/me", response_model=UserOut)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user's information.
    
    Protected endpoint that requires valid JWT token in Authorization header.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Current user information
    """
    logger.info(f"User profile accessed: {current_user.email} (ID: {current_user.id})")
    return current_user


@router.post("/forgot-password", response_model=ResetCodeOut)
def forgot_password(forgot_data: ForgotPasswordIn, db: Session = Depends(get_db)):
    """
    Request password reset for user account.
    
    In a production environment, this would send an email with a reset link.
    For demo purposes, it returns a reset code directly.
    
    Args:
        forgot_data: Forgot password request data (email)
        db: Database session
        
    Returns:
        Reset code for password reset (demo purposes)
        
    Raises:
        HTTPException 404: If email not found
    """
    # Find user by email
    user = db.query(User).filter(User.email == forgot_data.email).first()
    if not user:
        logger.warning(f"Password reset attempt with non-existent email: {forgot_data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email address not found"
        )
    
    # Generate a simple reset code (in production, this would be more secure)
    import hashlib
    import time
    reset_string = f"{user.email}{user.id}{time.time()}"
    reset_code = hashlib.md5(reset_string.encode()).hexdigest()[:8].upper()
    
    # In production, you would:
    # 1. Store the reset code in database with expiration
    # 2. Send email with reset link
    # 3. Return only success message
    
    logger.info(f"Password reset requested for: {user.email} (ID: {user.id})")
    
    return ResetCodeOut(
        message="Password reset code generated. In production, this would be sent via email.",
        reset_code=reset_code
    )


@router.post("/reset-password")
def reset_password(reset_data: ResetPasswordIn, db: Session = Depends(get_db)):
    """
    Reset user password with verification code.
    
    In production, this would verify the reset token from email.
    For demo purposes, it accepts any 8-character code.
    
    Args:
        reset_data: Reset password request data (email, new_password, reset_code)
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If email not found
        HTTPException 400: If reset code is invalid
    """
    # Find user by email
    user = db.query(User).filter(User.email == reset_data.email).first()
    if not user:
        logger.warning(f"Password reset attempt with non-existent email: {reset_data.email}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email address not found"
        )
    
    # Validate reset code (simplified for demo)
    if len(reset_data.reset_code) != 8 or not reset_data.reset_code.isalnum():
        logger.warning(f"Invalid reset code format for user: {reset_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid reset code format"
        )
    
    # In production, you would:
    # 1. Verify the reset code against database
    # 2. Check if code has expired
    # 3. Invalidate the code after use
    
    # Update user password
    new_password_hash = hash_password(reset_data.new_password)
    user.password_hash = new_password_hash
    
    db.commit()
    
    logger.info(f"Password reset completed for: {user.email} (ID: {user.id})")
    
    return {"message": "Password reset successfully. You can now login with your new password."}
