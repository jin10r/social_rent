from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from models import Base
import os
from typing import AsyncGenerator
import asyncio
import asyncpg
from sqlalchemy.exc import OperationalError

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent")

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    future=True,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def wait_for_database(max_retries: int = 30, delay: float = 2.0):
    """Wait for database to be ready"""
    print(f"Starting database connection check with {max_retries} max retries...")
    
    for attempt in range(max_retries):
        try:
            # Try to connect to the database
            print(f"Attempt {attempt + 1}/{max_retries}: Connecting to database...")
            conn = await asyncpg.connect(
                user="postgres",
                password="postgres123",
                database="social_rent",
                host="db",
                port=5432
            )
            await conn.close()
            print(f"✅ Database is ready after {attempt + 1} attempts")
            return
        except Exception as e:
            print(f"❌ Database connection attempt {attempt + 1} failed: {type(e).__name__}: {e}")
            if attempt < max_retries - 1:
                print(f"⏳ Waiting {delay} seconds before next attempt...")
                await asyncio.sleep(delay)
            else:
                print(f"💥 Failed to connect to database after {max_retries} attempts")
                raise Exception(f"Failed to connect to database after {max_retries} attempts: {e}")

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_database():
    """Initialize database tables"""
    # Wait for database to be ready
    await wait_for_database()
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)