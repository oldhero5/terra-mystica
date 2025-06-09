"""
Authentication endpoints
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_active_user, get_current_user, security
from app.models.user import User, RefreshToken
from app.schemas.auth import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    ApiKeyCreate,
    ApiKeyResponse
)
from app.utils.auth import AuthUtils

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user"""
    
    # Validate password confirmation
    if not user_create.passwords_match():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check username if provided
    if user_create.username:
        existing_username = db.query(User).filter(User.username == user_create.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # Create new user
    hashed_password = AuthUtils.hash_password(user_create.password)
    
    db_user = User(
        email=user_create.email,
        username=user_create.username,
        full_name=user_create.full_name,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,  # Email verification required
        email_verification_token=AuthUtils.generate_verification_token(),
        email_verification_expires=datetime.now(timezone.utc) + timedelta(hours=24)
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/login", response_model=TokenResponse)
def login_user(
    user_login: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Authenticate user and return tokens"""
    
    # Find user by email
    user = db.query(User).filter(User.email == user_login.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not AuthUtils.verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is inactive"
        )
    
    # Create tokens
    access_token = AuthUtils.create_access_token(subject=user.id)
    refresh_token = AuthUtils.create_refresh_token()
    refresh_token_hash = AuthUtils.hash_refresh_token(refresh_token)
    
    # Store refresh token in database
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=refresh_token_hash,
        device_info=request.headers.get("User-Agent", ""),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    db.add(db_refresh_token)
    
    # Update last login
    user.last_login = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(
    refresh_request: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
) -> Any:
    """Refresh access token using refresh token"""
    
    refresh_token_hash = AuthUtils.hash_refresh_token(refresh_request.refresh_token)
    
    # Find refresh token in database
    db_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == refresh_token_hash,
        RefreshToken.is_revoked == False,
        RefreshToken.expires_at > datetime.now(timezone.utc)
    ).first()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    user = db.query(User).filter(User.id == db_token.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    # Create new tokens
    access_token = AuthUtils.create_access_token(subject=user.id)
    new_refresh_token = AuthUtils.create_refresh_token()
    new_refresh_token_hash = AuthUtils.hash_refresh_token(new_refresh_token)
    
    # Revoke old refresh token
    db_token.is_revoked = True
    db_token.revoked_at = datetime.now(timezone.utc)
    
    # Create new refresh token
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_token_hash,
        device_info=request.headers.get("User-Agent", ""),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("User-Agent"),
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    
    db.add(new_db_token)
    db.commit()
    db.refresh(user)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=UserResponse.model_validate(user)
    )


@router.post("/logout")
def logout_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Any:
    """Logout user and revoke refresh tokens"""
    
    # Revoke all refresh tokens for this user
    db.query(RefreshToken).filter(
        RefreshToken.user_id == current_user.id,
        RefreshToken.is_revoked == False
    ).update({
        "is_revoked": True,
        "revoked_at": datetime.now(timezone.utc)
    })
    
    db.commit()
    
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """Get current user information"""
    return current_user


@router.post("/api-key", response_model=ApiKeyResponse)
def create_api_key(
    api_key_create: ApiKeyCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Create API key for current user"""
    
    # Generate API key
    api_key = AuthUtils.generate_api_key()
    
    # Update user with API key
    current_user.api_key = api_key
    current_user.api_key_name = api_key_create.name
    current_user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(current_user)
    
    return ApiKeyResponse(
        api_key=api_key,
        name=api_key_create.name,
        created_at=current_user.updated_at
    )


@router.delete("/api-key")
def revoke_api_key(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> Any:
    """Revoke current user's API key"""
    
    current_user.api_key = None
    current_user.api_key_name = None
    current_user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {"message": "API key revoked successfully"}