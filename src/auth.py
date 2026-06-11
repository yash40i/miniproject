"""
Authentication utilities for JWT tokens and password hashing
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import secrets
import hashlib

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
PASSWORD_RESET_EXPIRE_MINUTES = 60  # 1 hour

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify and decode a JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")
        if user_id is None:
            return None
        return {"user_id": user_id}
    except JWTError:
        return None


def generate_password_reset_token(email: str) -> str:
    """Generate a secure password reset token"""
    data = f"{email}{secrets.token_urlsafe(32)}{datetime.utcnow().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()


def create_password_reset_link(token: str, frontend_url: str = "http://localhost:3000") -> str:
    """Create a password reset link"""
    return f"{frontend_url}/reset-password?token={token}"


def verify_password_reset_token(token: str, token_from_db: str, expires_at: datetime) -> bool:
    """Verify if password reset token is valid"""
    # Check if token matches
    if token != token_from_db:
        return False
    
    # Check if token has expired
    if expires_at < datetime.utcnow():
        return False
    
    return True
