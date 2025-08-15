from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.common.dependencies import get_user_by_token
from src.config.broadcast import broadcast
from src.config.settings import settings
from src.middleware import AuthMiddleware

# Replace with your friend's IP or use "*" for all origins (less secure)

app = FastAPI(
    on_startup=[broadcast.connect],
    on_shutdown=[broadcast.disconnect],
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=settings.PROJECT_DESCRIPTION,
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
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
        "/auth/forgot-password-request",
        "/auth/forgot-password-verify",
        "/docs",
        "/openapi.json",
        "/auth/me",
        "/tickets/confirm",
    ],
)

# Session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
