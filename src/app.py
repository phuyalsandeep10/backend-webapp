from fastapi import FastAPI

from starlette.middleware.sessions import SessionMiddleware

from src.common.dependencies import get_user_by_token
from src.config.broadcast import broadcast
from src.config.settings import settings
from src.middleware import AuthMiddleware, CORSMiddleware

# Replace with your friend's IP or use "*" for all origins (less secure)

app = FastAPI(
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)


# CORS middleware
app.add_middleware(CORSMiddleware)
# Auth middleware
app.add_middleware(
    AuthMiddleware,
    get_user_by_token,
    extemp_paths=[
        "/auth/login",
        "/auth/register",
        "/auth/validate-email",
        "/auth/refresh-token",
        "/auth/verify-email",
        "/auth/oauth/google",
        "/auth/forgot-password-request",
        "/auth/forgot-password-verify",
        "/docs",
        "/openapi.json",
        # "/auth/me",
        "/tickets/confirm",
        "/organizations/countries",
        "/chat/",
    ],
)

# Session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
