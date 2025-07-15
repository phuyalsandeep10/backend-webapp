from sqlmodel import Field, SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select

load_dotenv()

# Database URL - supports both sync and async
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/chatboq_db"
)
ASYNC_DATABASE_URL = os.getenv(
    "ASYNC_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/chatboq_db",
)


print(f"Database URL: {DATABASE_URL}")
print(f"Async Database URL: {ASYNC_DATABASE_URL}")

# Create sync engine for Alembic migrations
sync_engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async engine for application
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections every 5 minutes
)

# Create async session factory
async_session = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def init_db():
    """Initialize database tables."""
    # Import all models to ensure they are registered with SQLAlchemy
    import src.models

    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


def init_db_sync():
    """Initialize database tables synchronously (for Alembic)."""
    # Import all models to ensure they are registered with SQLAlchemy
    import src.models

    SQLModel.metadata.create_all(sync_engine)


async def get_session():
    """Get a new async SQLModel session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


# Dependency for FastAPI
SessionDep = Annotated[AsyncSession, Depends(get_session)]
