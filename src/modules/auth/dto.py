from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class LoginDto(BaseModel):
    email: EmailStr
    password: str


class ValidateEmail(BaseModel):
    email: EmailStr


class RegisterDto(LoginDto):
    name: str


class VerifyEmailTokenDto(BaseModel):
    token: str
    email: EmailStr


class VerifyEmailDto(BaseModel):
    email: EmailStr


class ForgotPasswordVerifyDto(VerifyEmailTokenDto):
    new_password: str


class RefreshTokenDto(BaseModel):
    token: str  # this is the refresh token to be validated


class ResetPasswordDto(BaseModel):
    new_password: str
    old_password: str


class VerifyTwoFAOtpDto(BaseModel):
    token: str


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    name: Optional[str] = None
    image: Optional[str] = None
    mobile: Optional[str] = None
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
