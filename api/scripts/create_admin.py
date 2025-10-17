#!/usr/bin/env python3
"""
Script privado para crear el usuario administrador único.
Solo debe ejecutarse una vez por el propietario.
"""

import os
import sys
import getpass
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Base

# Load environment variables
load_dotenv()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin_user():
    """Crear usuario administrador único"""
    print("🔐 === CREACIÓN DE USUARIO ADMINISTRADOR ===")
    print("⚠️  ADVERTENCIA: Este script solo debe ejecutarse UNA VEZ")
    print("⚠️  Las credenciales serán las únicas para acceder al sistema")
    print()
    
    # Database configuration
    DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT', 5432)}/{os.getenv('POSTGRES_DB')}"
    
    try:
        # Create database engine
        engine = create_engine(DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        db = SessionLocal()
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.is_admin == True).first()
        if existing_admin:
            print("❌ Ya existe un usuario administrador en el sistema")
            print(f"   Usuario: {existing_admin.username}")
            print(f"   Email: {existing_admin.email}")
            print("   No se puede crear otro administrador")
            return False
        
        # Get admin credentials
        print("📝 Ingresa las credenciales del administrador:")
        print()
        
        username = input("👤 Usuario: ").strip()
        if not username:
            print("❌ El usuario no puede estar vacío")
            return False
        
        email = input("📧 Email: ").strip()
        if not email or "@" not in email:
            print("❌ Email inválido")
            return False
        
        print()
        print("🔒 Contraseña (mínimo 12 caracteres, debe ser muy segura):")
        password = getpass.getpass("   Contraseña: ")
        if len(password) < 12:
            print("❌ La contraseña debe tener al menos 12 caracteres")
            return False
        
        password_confirm = getpass.getpass("   Confirmar contraseña: ")
        if password != password_confirm:
            print("❌ Las contraseñas no coinciden")
            return False
        
        # Hash password
        hashed_password = pwd_context.hash(password)
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_admin=True,
            created_at=datetime.utcnow()
        )
        
        db.add(admin_user)
        db.commit()
        
        print()
        print("✅ Usuario administrador creado exitosamente!")
        print(f"   Usuario: {username}")
        print(f"   Email: {email}")
        print(f"   Creado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("🔐 IMPORTANTE:")
        print("   - Guarda estas credenciales en un lugar seguro")
        print("   - No las compartas con nadie")
        print("   - Son las únicas credenciales para acceder al sistema")
        print("   - Si las pierdes, tendrás que resetear la base de datos")
        print()
        print("🚀 El sistema está listo para usar")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando usuario administrador: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    success = create_admin_user()
    if not success:
        sys.exit(1)