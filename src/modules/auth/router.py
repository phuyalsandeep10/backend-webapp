from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from jose import jwt
from datetime import datetime, timedelta
from src.common.dependencies import (
    get_current_user,
    update_user_cache,
    get_bearer_token,
)

from fastapi import Depends
from src.common.dependencies import create_access_token
from src.enums import ProviderEnum
import pyotp
from .schema import (
    LoginSchema,
    RegisterSchema,
    VerifyEmailTokenSchema,
    ForgotPasswordVerifySchema,
    VerifyEmailSchema,
    ResetPasswordSchema,
    RefreshTokenSchema,
    VerifyTwoFAOtpSchema,
    UserSchema,
    ValidateEmailSchema
)
from src.utils.response import CustomResponse as cr

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


from .models import EmailVerification, RefreshToken, User
from .social_auth import oauth
from jose.exceptions import JWTError
from fastapi.encoders import jsonable_encoder


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
async def user_login(request: LoginSchema):

    user = await User.find_one(where={"email": request.email})

    # Check if user exists
    if not user:
        raise HTTPException(status_code=401, detail="Email not found")

    if not user.password:
        raise HTTPException(status_code=401, detail="Invalid Password")

    if not compare_password(user.password, request.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    data = await create_token(user)
    # return data

    # remove password
    del user.password
    user_schema = UserSchema.model_validate(user, from_attributes=True)
    return cr.success(
        data=jsonable_encoder({"user": user_schema, "is_2fa_verified": False, **data})
    )


@router.post("/logout")
async def logout(user=Depends(get_current_user)):

    token_data = await RefreshToken.find_one(where={"user_id": user.id, "active": True})

    if not token_data:
        raise HTTPException(status_code=404, detail="No active refresh token found")
    # Mark the token as inactive
    await RefreshToken.update(token_data.id, active=False)

    return cr.success(data={"message": "Logged out successfully"})


@router.post("/refresh-token")
async def refresh_token(body: RefreshTokenSchema):
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

        return cr.success(data={"access_token": access_token})
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/validate-email")
async def validateEmail(body: ValidateEmailSchema):
    user = await User.find_one({"email": body.email})
    if user:
        return cr.error(data={"success": False},message='Email already registered')
       
    return cr.success(data={"success": True})


@router.post("/register")
async def register(request: RegisterSchema):

    user = await User.find_one({"email": request.email})

    # Check if user already exists

    if user:
        return cr.error(data={"success": False},message='Email already registered') 

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

    return cr.success(data={"message": "User registered successfully"})


@router.get("/me")
async def get_auth_user(user=Depends(get_current_user)):
    try:
        userDb = await User.get(user.id)

        if not userDb:
            raise HTTPException(status_code=404, detail="Not found")
        # Remove password from the response
        user_schema = UserSchema.model_validate(userDb, from_attributes=True)
        return cr.success(
            data=jsonable_encoder(
                {
                    "user": user_schema,
                    "is_2fa_verified": user.is_2fa_verified,
                }
            )
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/verify-email")
async def verify_email_token(body: VerifyEmailTokenSchema):

    user = await User.find_one({"email": body.email})

    if not user:
        return cr.error(data={"success": False},message='User not found')

    verification = await EmailVerification.find_one(
        {"token": body.token, "is_used": False, "user_id": user.id}
    )

    if not verification:
        return cr.error(data={"success": False},message='Invalid or expired verification token')
      

    expires_at = verification.expires_at
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    if expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Verification token has expired")
    # Mark the token as used
    await EmailVerification.update(verification.id, is_used=True)
    # Here you would typically update the user's email verification status
    user = await User.update(user.id, email_verified_at=datetime.utcnow())
    tokens = await create_token(user)

    return cr.success(data={"message": "Email verified successfully", **tokens})


@router.post("/reset-password")
async def reset_password(body: ResetPasswordSchema, user=Depends(get_current_user)):

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
    return cr.success(data={"message": "Password reset successfully"})


@router.post("/forgot-password-request")
async def forgot_password_request(body: VerifyEmailSchema):
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

    return cr.success(data={"message": "Password reset link sent to your email"})


@router.post("/forgot-password-verify")
async def forgot_password_verify(body: ForgotPasswordVerifySchema):

    user = await User.find_one({"email": body.email})

    if not user:
        raise HTTPException(status_code=404, detail="Email not found")

    verification = await EmailVerification.find_one(
        {"token": body.token, "is_used": False, "user_id": user.id}
    )

    if not verification:
        return cr.error(data={"success": False},message='Invalid or expired verification token')
      

    expires_at = verification.expires_at
    if isinstance(expires_at, str):
        expires_at = datetime.fromisoformat(expires_at)

    # Check if the token has expired
    if expires_at < datetime.utcnow():
        return cr.error(data={"success": False},message='Verification token has expired')

    # Mark the token as used
    await EmailVerification.update(verification.id, is_used=True)
    # Update the user's password

    await User.update(user.id, password=hash_password(body.new_password))
    return cr.success(data={"message": "Password reset successfully"})


@router.get("/invitations")
async def get_invitations(user=Depends(get_current_user)):
    
    data = await OrganizationInvitation.filter(where={"email": user.email})
    return cr.success(data=data)


@router.get("/oauth/{provider}")
async def oauth_login(request: Request, provider: str):
    if provider not in ["google", "apple"]:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    redirect_uri = request.url_for("oauth_callback", provider=provider)
    return await getattr(oauth, provider).authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(request: Request, provider: ProviderEnum):
    if provider not in ["google", "apple"]:
        raise HTTPException(status_code=400, detail="Unsupported provider")
    client = getattr(oauth, provider)

    token = await client.authorize_access_token(request)

    userinfo = (
        await client.parse_id_token(request, token)
        if provider == "apple"
        else token.get("userinfo")
    )
    # Fallback for Apple: userinfo may be in token['id_token'] (decode if needed)
    # Fallback for Google: userinfo may be in token['userinfo'] or fetch from userinfo_endpoint

    # Extract user info (adjust as needed)
    email = userinfo.get("email")
    name = userinfo.get("name") or userinfo.get("email")
    image = userinfo.get("picture", "")

    # Your user creation/login logic here
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


@router.post("/2fa-otp/generate")
async def generate_2fa_otp(user=Depends(get_current_user)):
    otp_secrete = pyotp.random_base32()
    print(f"user {user.email}")

    otp_auth_url = pyotp.totp.TOTP(otp_secrete).provisioning_uri(
        name=user.email, issuer_name=settings.PROJECT_NAME
    )

    await User.update(
        user.id,
        two_fa_secret=otp_secrete,
        two_fa_auth_url=otp_auth_url,
        two_fa_enabled=True,
    )

    return cr.success(data={"secret": otp_secrete, "auth_url": otp_auth_url})


@router.post("/2fa-verify")
async def verify_two_fa(
    body: VerifyTwoFAOtpSchema,
    user=Depends(get_current_user),
    token: str = Depends(get_bearer_token),
):
    userDb = await User.get(user.id)
    if not userDb:
        return cr.error(message="User not found")

    two_fa_secrete = userDb.two_fa_secret
    totp = pyotp.TOTP(two_fa_secrete)

    message = "Token is invalid or user doesn't exist"

    if not totp.verify(body.token):
        return cr.error(message=message)
    await User.update(user.id, is_2fa_verified=True)
    update_user_cache(token, user)

    return cr.success(data={"message": "2FA verified successfully"})


@router.post("/2fa-disabled")
async def disable_two_fa(user=Depends(get_current_user)):

    await User.update(user.id, two_fa_enabled=False)

    return cr.success(data={"message": "2FA disabled successfully"})
