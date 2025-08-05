#!/usr/bin/env python3
import asyncio
import asyncpg
import sys
import os

async def wait_for_database():
    """Wait for database to be ready"""
    max_retries = 30
    delay = 2.0
    
    for attempt in range(max_retries):
        try:
            # Get database connection parameters from environment
            db_host = os.getenv("DB_HOST", "db")
            db_port = int(os.getenv("DB_PORT", "5432"))
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "postgres123")
            db_name = os.getenv("DB_NAME", "social_rent")
            
            print(f"Attempting to connect to database at {db_host}:{db_port} (attempt {attempt + 1}/{max_retries})")
            
            # Try to connect to the database
            conn = await asyncpg.connect(
                user=db_user,
                password=db_password,
                database=db_name,
                host=db_host,
                port=db_port
            )
            await conn.close()
            print(f"Database is ready after {attempt + 1} attempts")
            return True
        except Exception as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print(f"Waiting {delay} seconds before next attempt...")
                await asyncio.sleep(delay)
            else:
                print(f"Failed to connect to database after {max_retries} attempts")
                return False

if __name__ == "__main__":
    success = asyncio.run(wait_for_database())
    if not success:
        sys.exit(1)