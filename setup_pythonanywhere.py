#!/usr/bin/env python
"""
Setup script for PythonAnywhere environment
This script will:
1. Create necessary directories
2. Initialize the database
3. Verify configuration
"""

import os
import sys
from pathlib import Path

def setup_directories():
    """Create necessary directories for the application"""
    print("Setting up directories...")
    
    # List of directories to create
    directories = [
        "instance",
        "logs",
        "app/static/uploads/avatars",
        "app/static/uploads/covers"
    ]
    
    # Create each directory
    for directory in directories:
        path = Path(directory)
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
                print(f"✓ Created directory: {directory}")
            except Exception as e:
                print(f"✗ Failed to create directory {directory}: {str(e)}")
                return False
    
    return True

def initialize_database():
    """Initialize the database using Flask-Migrate or SQLAlchemy"""
    print("\nInitializing database...")
    
    try:
        # First try using Flask-Migrate (preferred method)
        from flask.cli import ScriptInfo
        from flask_migrate import upgrade as migrate_upgrade
        from app import create_app
        
        app = create_app()
        # Set up Flask context
        with app.app_context():
            migrate_upgrade()
            print("✓ Database initialized using Flask-Migrate")
            
    except Exception as e:
        print(f"! Flask-Migrate failed: {str(e)}")
        print("Trying direct SQLAlchemy initialization...")
        
        try:
            # Fallback to direct SQLAlchemy initialization
            from app import db, create_app
            app = create_app()
            with app.app_context():
                db.create_all()
                print("✓ Database initialized using SQLAlchemy")
        except Exception as e:
            print(f"✗ Failed to initialize database: {str(e)}")
            return False
    
    return True

def verify_config():
    """Verify application configuration"""
    print("\nVerifying configuration...")
    
    try:
        from app import create_app
        app = create_app()
        
        with app.app_context():
            # Check database URL
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', 'Not configured')
            print(f"Database URL: {db_url}")
            
            # Check secret key (without exposing it)
            if app.config.get('SECRET_KEY'):
                print("✓ Secret key is configured")
            else:
                print("✗ Secret key is not configured")
            
            # Check if database file exists for SQLite
            if db_url.startswith('sqlite:///'):
                db_path = db_url.replace('sqlite:///', '')
                if os.path.isfile(db_path):
                    print(f"✓ Database file exists at {db_path}")
                else:
                    print(f"✗ Database file does not exist at {db_path}")
            
            print("Configuration verification complete")
    except Exception as e:
        print(f"✗ Configuration verification failed: {str(e)}")
        return False
    
    return True

def main():
    """Main script execution"""
    print("PythonAnywhere Setup Script")
    print("==========================")
    
    # Change to the application root directory
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        print(f"Working directory: {os.getcwd()}")
    except Exception as e:
        print(f"Failed to set working directory: {str(e)}")
        return 1
    
    # Run setup steps
    if not setup_directories():
        print("Directory setup failed")
        return 1
    
    if not initialize_database():
        print("Database initialization failed")
        return 1
    
    if not verify_config():
        print("Configuration verification failed")
        return 1
    
    print("\n✓ Setup completed successfully!")
    print("You can now reload your web application in the PythonAnywhere dashboard.")
    return 0

if __name__ == "__main__":
    sys.exit(main())