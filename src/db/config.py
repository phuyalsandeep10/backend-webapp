from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config.settings import settings

DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@localhost:5432/{settings.DB_NAME}"

engine = create_async_engine(url=DATABASE_URL)


async_session = sessionmaker(engine, class_=AsyncSession)

Base = declarative_base()
