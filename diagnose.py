#!/usr/bin/env python3
"""
Diagnostic script for database connection issues
"""

import os
import sys
import asyncio
import subprocess
import socket
from pathlib import Path

def check_python_packages():
    """Check if required Python packages are installed"""
    print("🔍 Checking Python packages...")
    
    required_packages = [
        'fastapi', 'uvicorn', 'asyncpg', 'sqlalchemy', 
        'pydantic', 'python-dotenv'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n📦 Missing packages: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    
    print("✅ All required packages are installed")
    return True

def check_environment_variables():
    """Check environment variables"""
    print("\n🔍 Checking environment variables...")
    
    required_vars = ['DATABASE_URL', 'BOT_TOKEN', 'WEBAPP_URL']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value[:50]}{'...' if len(value) > 50 else ''}")
        else:
            print(f"  ❌ {var} (not set)")
            missing.append(var)
    
    if missing:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing)}")
        return False
    
    print("✅ All environment variables are set")
    return True

def check_network_connectivity():
    """Check network connectivity to database"""
    print("\n🔍 Checking network connectivity...")
    
    # Check if port 5432 is open
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('localhost', 5432))
        sock.close()
        
        if result == 0:
            print("  ✅ Port 5432 is open on localhost")
            return True
        else:
            print("  ❌ Port 5432 is not accessible on localhost")
            return False
    except Exception as e:
        print(f"  ❌ Network check failed: {e}")
        return False

async def test_database_connection():
    """Test actual database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        import asyncpg
        
        # Try to connect to database
        conn = await asyncpg.connect(
            user='postgres',
            password='postgres123',
            database='social_rent',
            host='localhost',
            port=5432
        )
        
        # Test a simple query
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        
        if result == 1:
            print("  ✅ Database connection successful")
            return True
        else:
            print("  ❌ Database query failed")
            return False
            
    except ImportError:
        print("  ❌ asyncpg not available")
        return False
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False

def check_docker_status():
    """Check if Docker is running and containers are up"""
    print("\n🔍 Checking Docker status...")
    
    try:
        # Check if Docker is running
        result = subprocess.run(['docker', 'info'], capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ Docker is running")
            
            # Check if containers are running
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                if 'postgis' in result.stdout or 'postgres' in result.stdout:
                    print("  ✅ PostgreSQL container is running")
                    return True
                else:
                    print("  ❌ PostgreSQL container not found")
                    return False
            else:
                print("  ❌ Cannot check Docker containers")
                return False
        else:
            print("  ❌ Docker is not running")
            return False
    except FileNotFoundError:
        print("  ❌ Docker not installed")
        return False
    except Exception as e:
        print(f"  ❌ Docker check failed: {e}")
        return False

def check_postgresql_service():
    """Check if PostgreSQL service is running"""
    print("\n🔍 Checking PostgreSQL service...")
    
    try:
        result = subprocess.run(['systemctl', 'is-active', 'postgresql'], 
                              capture_output=True, text=True)
        if result.returncode == 0 and 'active' in result.stdout:
            print("  ✅ PostgreSQL service is running")
            return True
        else:
            print("  ❌ PostgreSQL service is not running")
            return False
    except FileNotFoundError:
        print("  ❌ systemctl not available (not systemd)")
        return False
    except Exception as e:
        print(f"  ❌ PostgreSQL service check failed: {e}")
        return False

def generate_report():
    """Generate a comprehensive diagnostic report"""
    print("🔧 Database Connection Diagnostic Report")
    print("=" * 50)
    
    issues = []
    solutions = []
    
    # Check Python packages
    if not check_python_packages():
        issues.append("Missing Python packages")
        solutions.append("Run: pip install fastapi uvicorn asyncpg sqlalchemy pydantic python-dotenv")
    
    # Check environment variables
    if not check_environment_variables():
        issues.append("Missing environment variables")
        solutions.append("Set required environment variables or use .env file")
    
    # Check network connectivity
    if not check_network_connectivity():
        issues.append("Network connectivity issues")
        solutions.append("Check if PostgreSQL is running on port 5432")
    
    # Check Docker status
    docker_ok = check_docker_status()
    
    # Check PostgreSQL service
    postgres_ok = check_postgresql_service()
    
    if not docker_ok and not postgres_ok:
        issues.append("No database service detected")
        solutions.append("Start PostgreSQL service or Docker containers")
    
    # Test database connection
    try:
        connection_ok = asyncio.run(test_database_connection())
        if not connection_ok:
            issues.append("Database connection failed")
            solutions.append("Check database credentials and permissions")
    except Exception as e:
        issues.append(f"Database connection test failed: {e}")
        solutions.append("Check database configuration")
    
    # Generate summary
    print("\n📊 Summary")
    print("=" * 30)
    
    if not issues:
        print("✅ No issues detected! Your setup should work correctly.")
    else:
        print(f"❌ Found {len(issues)} issue(s):")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        
        print("\n🔧 Suggested Solutions:")
        for i, solution in enumerate(solutions, 1):
            print(f"  {i}. {solution}")
    
    print("\n📋 Quick Fixes:")
    print("1. Restart PostgreSQL: sudo systemctl restart postgresql")
    print("2. Restart Docker containers: docker compose down && docker compose up")
    print("3. Check logs: docker compose logs backend")
    print("4. Rebuild containers: docker compose up --build")

if __name__ == "__main__":
    generate_report()