#!/usr/bin/env python3
import asyncio
import asyncpg
import os
import sys

async def test_database_connection():
    """Test database connection"""
    try:
        # Get database connection parameters
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = int(os.getenv("DB_PORT", "5432"))
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "postgres123")
        db_name = os.getenv("DB_NAME", "social_rent")
        
        print(f"Testing connection to database at {db_host}:{db_port}")
        print(f"User: {db_user}, Database: {db_name}")
        
        # Try to connect
        conn = await asyncpg.connect(
            user=db_user,
            password=db_password,
            database=db_name,
            host=db_host,
            port=db_port
        )
        
        # Test a simple query
        result = await conn.fetchval("SELECT version()")
        print(f"Database connection successful!")
        print(f"PostgreSQL version: {result}")
        
        await conn.close()
        return True
        
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_database_connection())
    if not success:
        sys.exit(1)
    else:
        print("Database connection test passed!")