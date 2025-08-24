from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlmodel import create_engine

from src.config.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@localhost:5432/{settings.DB_NAME}"
SYNC_DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@localhost:5432/{settings.DB_NAME}"

engine = create_async_engine(url=DATABASE_URL)

async_session = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

SYNC_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/chatboq_db"
# Create sync engine for Alembic migrations
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

Base = declarative_base()
