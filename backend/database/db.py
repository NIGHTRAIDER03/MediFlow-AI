"""Async database engine, session factory, and initialization."""

import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
from database.models import Base

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://mediflow:mediflow123@127.0.0.1:5433/mediflow"
)

# Handle different PostgreSQL URL formats:
# - Supabase uses: postgresql://...
# - Render uses: postgres://...
# - We need: postgresql+asyncpg://...
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Supabase fix: change pooler port 6543 to direct connection port 5432
# asyncpg doesn't support transaction-mode pooling (pgbouncer on port 6543)
if ":6543/" in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace(":6543/", ":5432/")

# Detect if we're connecting to a cloud database (Supabase, Render, etc.)
is_cloud_db = "supabase" in DATABASE_URL or "render" in DATABASE_URL or "neon" in DATABASE_URL

# Configure SSL for cloud databases
connect_args = {}
if is_cloud_db:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Create all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    """Dependency that yields an async session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
