"""
Database session and connection management for async SQLAlchemy 2.0.
"""
import os
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from services.api.app.db.base import Base

# Default to Postgres async URL or fallback to SQLite async for lightweight execution
DEFAULT_DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/creativeforge"
)

_async_engine: Optional[AsyncEngine] = None
_async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_async_engine(database_url: Optional[str] = None) -> AsyncEngine:
    global _async_engine
    if _async_engine is None or database_url is not None:
        url = database_url or DEFAULT_DB_URL
        # SQLite async connection argument adjustment if applicable
        connect_args = {}
        if url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        
        _async_engine = create_async_engine(
            url,
            echo=os.getenv("SQL_ECHO", "False").lower() in ("true", "1"),
            future=True,
            connect_args=connect_args,
        )
    return _async_engine


def get_async_sessionmaker(engine: Optional[AsyncEngine] = None) -> async_sessionmaker[AsyncSession]:
    global _async_session_factory
    eng = engine or get_async_engine()
    if _async_session_factory is None or engine is not None:
        _async_session_factory = async_sessionmaker(
            bind=eng,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _async_session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency injection helper for FastAPI routes."""
    session_maker = get_async_sessionmaker()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db(engine: Optional[AsyncEngine] = None) -> None:
    """Create all tables asynchronously (useful for test suites and initial bootstrap)."""
    eng = engine or get_async_engine()
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
