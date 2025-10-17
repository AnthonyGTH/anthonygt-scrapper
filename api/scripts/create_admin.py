#!/usr/bin/env python3
"""
Script to create admin user for the price monitoring system.
Run this script once to create the initial admin user.
"""

import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from datetime import datetime

# Add the parent directory to the path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Base

def create_admin_user():
    """Create admin user with hashed password"""
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Database configuration
    DATABASE_URL = f"mysql+mysqlconnector://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', 3306)}/{os.getenv('POSTGRES_DB')}"
    
    # Create database engine
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("Admin user already exists!")
            return
        
        # Get admin credentials from environment or prompt
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@example.com")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        
        # Hash password
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed_password = pwd_context.hash(admin_password)
        
        # Create admin user
        admin_user = User(
            username=admin_username,
            email=admin_email,
            hashed_password=hashed_password,
            is_admin=True,
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        
        print(f"Admin user created successfully!")
        print(f"Username: {admin_username}")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("\nIMPORTANT: Change the default password after first login!")
        
    except Exception as e:
        print(f"Error creating admin user: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin_user()
