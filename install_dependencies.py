#!/usr/bin/env python3
"""
Dependency installation script for Social Rent application
"""

import subprocess
import sys
import os
from pathlib import Path

def install_python_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    
    # Read requirements from backend/requirements.txt
    requirements_file = Path("backend/requirements.txt")
    if not requirements_file.exists():
        print("❌ requirements.txt not found in backend directory")
        return False
    
    try:
        with open(requirements_file, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        print(f"Found {len(requirements)} dependencies to install")
        
        # Install each dependency
        for req in requirements:
            print(f"Installing {req}...")
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'install', req
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"  ✅ {req}")
            else:
                print(f"  ❌ {req}: {result.stderr}")
                return False
        
        print("✅ All Python dependencies installed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def setup_postgresql():
    """Setup PostgreSQL database"""
    print("\n🗄️  Setting up PostgreSQL...")
    
    # Check if PostgreSQL is installed
    try:
        result = subprocess.run(['which', 'psql'], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ PostgreSQL not found. Please install PostgreSQL first.")
            print("Ubuntu/Debian: sudo apt install postgresql postgresql-contrib postgis")
            print("macOS: brew install postgresql postgis")
            return False
    except Exception as e:
        print(f"❌ Error checking PostgreSQL: {e}")
        return False
    
    print("✅ PostgreSQL is installed")
    
    # Check if database exists
    try:
        result = subprocess.run([
            'psql', '-h', 'localhost', '-U', 'postgres', '-d', 'social_rent', 
            '-c', 'SELECT 1'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Database 'social_rent' exists")
        else:
            print("Creating database 'social_rent'...")
            # Create database
            result = subprocess.run([
                'createdb', '-h', 'localhost', '-U', 'postgres', 'social_rent'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Database created successfully")
            else:
                print(f"❌ Failed to create database: {result.stderr}")
                return False
    except Exception as e:
        print(f"❌ Error setting up database: {e}")
        return False
    
    # Apply schema
    init_sql = Path("init.sql")
    if init_sql.exists():
        print("Applying database schema...")
        try:
            result = subprocess.run([
                'psql', '-h', 'localhost', '-U', 'postgres', '-d', 'social_rent', 
                '-f', 'init.sql'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Database schema applied successfully")
            else:
                print(f"❌ Failed to apply schema: {result.stderr}")
                return False
        except Exception as e:
            print(f"❌ Error applying schema: {e}")
            return False
    else:
        print("⚠️  init.sql not found, skipping schema application")
    
    return True

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres123@localhost:5432/social_rent

# Bot Configuration
BOT_TOKEN=8482163056:AAFO_l3IuliKB6I81JyQ-3_VrZuQ-8S5P-k

# Web Application Configuration
WEBAPP_URL=http://localhost:3000

# Backend Configuration
BACKEND_URL=http://localhost:8001

# Development Settings
DEBUG=true
LOG_LEVEL=INFO
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    return True

def main():
    """Main installation function"""
    print("🔧 Social Rent Application - Dependency Installation")
    print("=" * 60)
    
    success = True
    
    # Install Python dependencies
    if not install_python_dependencies():
        success = False
    
    # Setup environment
    if not setup_environment():
        success = False
    
    # Setup PostgreSQL (optional, user can skip)
    print("\n🗄️  PostgreSQL Setup (Optional)")
    print("If you're using Docker, you can skip this step.")
    response = input("Setup PostgreSQL locally? (y/N): ")
    
    if response.lower() == 'y':
        if not setup_postgresql():
            success = False
    
    # Final summary
    print("\n📊 Installation Summary")
    print("=" * 30)
    
    if success:
        print("✅ Installation completed successfully!")
        print("\n🚀 Next steps:")
        print("1. Start PostgreSQL (if not using Docker): sudo systemctl start postgresql")
        print("2. Run diagnostic: python3 diagnose.py")
        print("3. Start backend: cd backend && python3 -m uvicorn main:app --reload")
        print("4. Or use Docker: docker compose up --build")
    else:
        print("❌ Installation completed with errors.")
        print("Please check the error messages above and try again.")
        print("\n💡 Tips:")
        print("- Make sure you have Python 3.8+ installed")
        print("- Install PostgreSQL if you want to run locally")
        print("- Use Docker for easier setup")

if __name__ == "__main__":
    main()