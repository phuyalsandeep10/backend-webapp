from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlmodel import create_engine


from src.config.settings import settings

DATABASE_URL = f"postgresql+asyncpg://postgres:postgres@localhost:5432/chatboq_db"

print(f"db user {DATABASE_URL}")
engine = create_async_engine(url=DATABASE_URL)

async_session = async_sessionmaker(
    engine=engine, class_=AsyncSession, expire_on_commit=False
)

# Create sync engine for Alembic migrations
sync_engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=300,
)

Base = declarative_base()
