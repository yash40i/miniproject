"""
Pydantic schemas for API request/response validation
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional


class UserRegister(BaseModel):
    """User registration request"""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        """Validate password minimum length"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class UserLogin(BaseModel):
    """User login request"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    """User response (without password)"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class AnalysisRequest(BaseModel):
    """Analysis request"""
    job_description: str


class AnalysisStatus(BaseModel):
    """Analysis status response"""
    analysis_id: str
    status: str
    error: Optional[str] = None


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ForgotPasswordResponse(BaseModel):
    """Forgot password response"""
    message: str
    email: str


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password minimum length"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class ResetPasswordResponse(BaseModel):
    """Reset password response"""
    message: str
    email: str


class VerifyResetTokenRequest(BaseModel):
    """Verify reset token request"""
    token: str


class VerifyResetTokenResponse(BaseModel):
    """Verify reset token response"""
    valid: bool
    email: Optional[str] = None
    message: str


class GoogleAuthRequest(BaseModel):
    """Google OAuth token request"""
    token: str
    email: Optional[str] = None
    name: Optional[str] = None


class GoogleAuthResponse(BaseModel):
    """Google OAuth response"""
    access_token: str
    token_type: str
    user: UserResponse


class UserUpdateRequest(BaseModel):
    """Update user profile request"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    
    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    current_password: str
    new_password: str
    confirm_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        """Validate password minimum length"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class ChangePasswordResponse(BaseModel):
    """Change password response"""
    message: str
    success: bool


class UserProfileResponse(BaseModel):
    """User profile response with additional info"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True
