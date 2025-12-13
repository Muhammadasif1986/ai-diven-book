"""
Database connection and session management for the RAG chatbot system.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from src.core.config import settings

# Create async engine for Neon Postgres
async_engine = create_async_engine(
    settings.NEON_DATABASE_URL,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=20,  # Connection pool size
    max_overflow=30,  # Additional connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=300,  # Recycle connections after 5 minutes
)

# Create sync engine (for cases where async is not suitable)
sync_engine = create_engine(
    settings.NEON_DATABASE_URL.replace('+asyncpg', ''),
    echo=settings.DEBUG,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)

# Create async session maker
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create sync session maker
SyncSessionLocal = sessionmaker(
    sync_engine,
    expire_on_commit=False
)

Base = declarative_base()


@asynccontextmanager
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager for database sessions."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_sync_session():
    """Sync context manager for database sessions."""
    session = SyncSessionLocal()
    try:
        yield session
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_db():
    """Initialize database tables."""
    async with async_engine.begin() as conn:
        # Create all tables defined in models
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all database tables (use with caution!)."""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)