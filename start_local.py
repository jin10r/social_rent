#!/usr/bin/env python3
"""
Local development startup script
This script helps to start the application locally without Docker
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi', 'uvicorn', 'asyncpg', 'sqlalchemy', 
        'pydantic', 'python-dotenv', 'httpx'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ All dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    return True

def check_postgres_connection():
    """Check if PostgreSQL is accessible"""
    try:
        import asyncpg
        import asyncio
        
        async def test_connection():
            try:
                conn = await asyncpg.connect(
                    user='postgres',
                    password='postgres123',
                    database='social_rent',
                    host='localhost',
                    port=5432
                )
                await conn.close()
                return True
            except Exception as e:
                print(f"❌ PostgreSQL connection failed: {e}")
                return False
        
        return asyncio.run(test_connection())
    except ImportError:
        print("❌ asyncpg not available for connection test")
        return False

def setup_environment():
    """Setup environment variables"""
    env_vars = {
        'DATABASE_URL': 'postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent',
        'BOT_TOKEN': '8482163056:AAFO_l3IuliKB6I81JyQ-3_VrZuQ-8S5P-k',
        'WEBAPP_URL': 'http://localhost:3000'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ Set {key}")

def start_backend():
    """Start the backend server"""
    print("\n🚀 Starting backend server...")
    backend_dir = Path("backend")
    
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Change to backend directory and start the server
        os.chdir(backend_dir)
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'main:app', 
            '--host', '0.0.0.0', 
            '--port', '8001', 
            '--reload'
        ], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start backend: {e}")
        return False
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
        return True

def main():
    """Main function"""
    print("🔧 Social Rent Application - Local Development Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Check PostgreSQL connection
    print("\n🔍 Checking PostgreSQL connection...")
    if not check_postgres_connection():
        print("\n⚠️  PostgreSQL connection failed!")
        print("Please ensure PostgreSQL is running and accessible")
        print("You can start PostgreSQL with:")
        print("  sudo systemctl start postgresql")
        print("  sudo -u postgres createdb social_rent")
        print("  sudo -u postgres psql -d social_rent -f init.sql")
        response = input("\nContinue anyway? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    # Start backend
    start_backend()

if __name__ == "__main__":
    main()