from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from jose import jwt
from datetime import datetime, timedelta
from src.common.dependencies import get_current_user
from fastapi import Depends
from src.common.dependencies import create_access_token
from .dto import (
    LoginDto,
    RegisterDto,
    VerifyEmailTokenDto,
    ForgotPasswordVerifyDto,
    VerifyEmailDto,
    ResetPasswordDto,
    RefreshTokenDto,
)
from .models import User, EmailVerification, RefreshToken


from src.common.utils import (
    generate_numeric_token,
    compare_password,
    hash_password,
    generate_refresh_token,
)
from src.models import OrganizationInvitation
from src.tasks import send_verification_email, send_forgot_password_email
from .social_auth import oauth
from src.config.settings import settings
from src.modules.organizations.models import OrganizationInvitation
from src.tasks import send_forgot_password_email, send_verification_email

from .dto import (
    ForgotPasswordVerifyDto,
    LoginDto,
    RefreshTokenDto,
    RegisterDto,
    ResetPasswordDto,
    VerifyEmailDto,
    VerifyEmailTokenDto,
)
from .models import EmailVerification, RefreshToken, User
from .social_auth import oauth

router = APIRouter()


async def create_token(user):
    token = create_access_token(data={"sub": user.email})
    refresh_token = generate_refresh_token()

    await RefreshToken.create(
        user_id=user.id,
        token=refresh_token,
        active=True,
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=30),
    )

    return {"access_token": token, "refresh_token": refresh_token}


@router.post("/login")
async def login(request: LoginDto):

    user = await User.find_one(where={"email": request.email})

    # Check if user exists
    if not user:
        raise HTTPException(status_code=401, detail="Email not found")

    if not compare_password(user.password, request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    return await create_token(user)


@router.post("/logout")
async def logout(user=Depends(get_current_user)):

    token_data = await RefreshToken.find_one(where={"user_id": user.id, "active": True})

    if not token_data:
        raise HTTPException(status_code=404, detail="No active refresh token found")
    # Mark the token as inactive
    await RefreshToken.update(token_data.id, active=False)

    return {"message": "Logged out successfully"}


@router.post("/refresh-token")
async def refresh_token(body: RefreshTokenDto):
    # Validate the refresh token
    token_data = await RefreshToken.find_one(
        where={"token": body.token, "active": True}
    )

    if not token_data:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    # Check if the refresh token has expired
    expires_at = token_data.expires_at
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    # If the token has expired, raise an error
    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Refresh token has expired")

    # Create a new access token
    try:
        user = await User.get(token_data.user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        access_token = create_access_token(data={"sub": user.email})
        return {"access_token": access_token}
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/register")
async def register(request: RegisterDto):

    user = await User.find_one({"email": request.email})

    # Check if user already exists

    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(request.password)
    user = await User.create(
        email=request.email, name=request.name, password=hashed_password
    )

    token = generate_numeric_token(6)
    # Here you would typically send a verification email

    await EmailVerification.create(
        user_id=user.id,
        token=token,
        is_used=False,
        expires_at=datetime.utcnow() + timedelta(days=1),
        type="email_verification",
    )

    send_verification_email.delay(email=request.email, token=token)

    return {"message": "User registered successfully"}


@router.get("/me")
async def get_auth_user(user=Depends(get_current_user)):
    try:
        user = await User.get(user.id)
        del user.password  # Remove password from the response
        return user
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/verify-email")
async def verify_email_token(body: VerifyEmailTokenDto):

    user = await User.find_one({"email": body.email})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    verification = await EmailVerification.find_one(
        {"token": body.token, "is_used": False, "user_id": user.id}
    )

    if not verification:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    expires_at = verification.expires_at
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")
    # Mark the token as used
    await EmailVerification.update(verification.id, is_used=True)
    # Here you would typically update the user's email verification status
    await User.update(user.id, email_verified_at=datetime.utcnow())

    return {"message": "Email verified successfully"}


@router.post("/reset-password")
async def reset_password(
    body: ResetPasswordDto, user: User = Depends(get_current_user)
):

    user = await User.find_one({"email": user.email})

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    # Generate a reset token (in a real application, you would send this to the user's email)
    password = user.password
    if not compare_password(password, body.old_password):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    # Update the user's password
    new_hashed_password = hash_password(body.new_password)

    await User.update(user.id, password=new_hashed_password)

    # Here you would typically send a reset link to the user's email
    return {"message": "Password reset successfully"}


@router.post("/forgot-password-request")
async def forgot_password_request(body: VerifyEmailDto):
    user = await User.find_one({"email": body.email})

    # Check if user exists
    if not user:
        raise HTTPException(status_code=404, detail="Email not found")
    # Generate a reset token (in a real application, you would send this to the user's email)
    token = generate_numeric_token(6)

    await EmailVerification.create(
        user_id=user.id,
        token=token,
        is_used=False,
        expires_at=(datetime.utcnow() + timedelta(hours=1)),
        type="forgot_password",
    )

    send_forgot_password_email.delay(email=body.email, token=token)

    return {"message": "Password reset link sent to your email"}


@router.post("/forgot-password-verify")
async def forgot_password_verify(body: ForgotPasswordVerifyDto):

    user = await User.find_one({"email": body.email})

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    verification = await EmailVerification.find_one(
        {"token": body.token, "is_used": False, "user_id": user.id}
    )

    if not verification:
        raise HTTPException(
            status_code=400, detail="Invalid or expired verification token"
        )

    expires_at = verification.expires_at
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    # Check if the token has expired
    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")

    # Mark the token as used
    await EmailVerification.update(verification.id, is_used=True)
    # Update the user's password

    await User.update(user.id, password=hash_password(body.new_password))
    return {"message": "Password reset successfully"}


@router.get("/invitations")
async def get_invitations(user=Depends(get_current_user)):
    return await OrganizationInvitation.filter(where={"email": user.email})


@router.get("/oauth/google")
async def login(request: Request):
    redirect_uri = request.url_for("auth")

    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/oauth/google/callback")
async def auth(request: Request):

    response = await oauth.google.authorize_access_token(request)

    userinfo = response.get("userinfo")

    name = userinfo.get("email")
    email = userinfo.get("email")
    image = userinfo.get("picture")

    user = await User.find_one(where={"email": email})

    if not user:
        user = await User.create(
            email=email,
            name=name,
            image=image,
            email_verified_at=datetime.utcnow(),
            password="",
        )

    tokens = await create_token(user)

    redirect_url = f"{settings.FRONTEND_URL}/login?access_token={tokens.get('access_token')}&refresh_token={tokens.get('refresh_token')}"

    return RedirectResponse(redirect_url)
