from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from models import Base
import os
import asyncio
import logging
from typing import AsyncGenerator

# Configure logging
logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent")

logger.info(f"Using database URL: {DATABASE_URL}")

# Create async engine with improved configuration
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for debugging SQL queries
    future=True,
    pool_pre_ping=True,  # Enable connection health checks
    pool_recycle=300,    # Recycle connections every 5 minutes
    pool_size=10,        # Maximum number of connections in pool
    max_overflow=20,     # Maximum number of connections that can be created beyond pool_size
    connect_args={
        "server_settings": {
            "application_name": "social_rent_backend"
        }
    }
)

# Create async session maker
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def wait_for_database(max_retries: int = 30, retry_interval: float = 2.0):
    """Wait for database to be ready with improved error handling"""
    logger.info("Waiting for database to be ready...")
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                # Test basic connectivity
                result = await conn.execute("SELECT 1 as test")
                row = result.fetchone()
                if row and row[0] == 1:
                    logger.info(f"Database connection successful on attempt {attempt + 1}")
                    return
                else:
                    raise Exception("Database test query failed")
                    
        except Exception as e:
            logger.warning(f"Database connection attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_interval} seconds...")
                await asyncio.sleep(retry_interval)
            else:
                error_msg = f"Failed to connect to database after {max_retries} attempts"
                logger.error(error_msg)
                raise Exception(error_msg) from e

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session with error handling"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_database():
    """Initialize database tables with improved error handling"""
    try:
        # Wait for database to be ready
        await wait_for_database()
        
        # Test if tables already exist
        async with engine.begin() as conn:
            # Check if users table exists
            result = await conn.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """)
            tables_exist = result.scalar()
            
            if tables_exist:
                logger.info("Database tables already exist")
            else:
                logger.info("Creating database tables...")
                # Create all tables
                await conn.run_sync(Base.metadata.create_all)
                logger.info("Database tables created successfully")
                
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

async def close_database():
    """Close database connections"""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise