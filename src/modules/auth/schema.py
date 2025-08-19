from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum

class VerifyEmailEnum(str, Enum):
    ForgotPassword = "forgot_password"
    EmailVerification = "email_verification"
  


class ResendVerificationSchema(BaseModel):
    email: EmailStr
    type: VerifyEmailEnum


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class ValidateEmailSchema(BaseModel):
    email: EmailStr


class RegisterSchema(LoginSchema):
    name: str


class VerifyEmailTokenSchema(BaseModel):
    token: str
    email: EmailStr


class VerifyEmailSchema(BaseModel):
    email: EmailStr


class ForgotPasswordVerifySchema(VerifyEmailTokenSchema):
    new_password: str


class RefreshTokenSchema(BaseModel):
    token: str  # this is the refresh token to be validated


class ResetPasswordSchema(BaseModel):
    new_password: str
    old_password: str


class VerifyTwoFAOtpSchema(BaseModel):
    token: str


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    image: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    is_active: bool
    two_fa_enabled: bool
    two_fa_secret: Optional[str] = None
    two_fa_auth_url: Optional[str] = None
    email_verified_at: Optional[datetime] = None
    is_superuser: bool
    is_staff: bool
    attributes: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_2fa_verified: Optional[bool] = None

    class Config:
        orm_mode = True

class UserProfileUpdateSchema(BaseModel):
    """Schema for updating user profile - only allows safe fields"""
    name: Optional[str] = None
    image: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    language: Optional[str] = None
    
