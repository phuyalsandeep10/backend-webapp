from typing import Union

from fastapi import FastAPI
from src.config.settings import settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from src.modules.auth.router import router as auth_router
from src.modules.organizations.router import router as organization_router
from src.modules.admin.router import router as admin_router
from src.modules.team.router import router as team_router
from src.modules.chat.routers.customer import router as customer_router
from src.config.broadcast import broadcast


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
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
