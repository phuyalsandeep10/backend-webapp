from pydantic import BaseModel, EmailStr


class LoginDto(BaseModel):
    email: EmailStr
    password: str


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
