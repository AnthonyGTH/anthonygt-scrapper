from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, index=True)
    url = Column(Text, nullable=False)
    site = Column(String(50), nullable=False, index=True)
    category = Column(String(100))
    reference_price = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    prices = relationship("Price", back_populates="product")
    deals = relationship("Deal", back_populates="product")

class Price(Base):
    __tablename__ = "prices"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    price = Column(Float, nullable=False)
    currency = Column(String(3), default="MXN")
    availability = Column(String(50))
    scraped_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    product = relationship("Product", back_populates="prices")

class Deal(Base):
    __tablename__ = "deals"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    original_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False)
    ai_reasoning = Column(Text)
    telegram_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    product = relationship("Product", back_populates="deals")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
