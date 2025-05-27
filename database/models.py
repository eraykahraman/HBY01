from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import declarative_base
import enum

Base = declarative_base()

class UserRole(str, enum.Enum):
    NETCOM_ENGINEER = "netcom_engineer"
    DESIGN_ENGINEER = "design_engineer"
    GENERIC_USER = "generic_user"

class DBCFile(Base):
    """Model for storing DBC file information"""
    __tablename__ = 'dbc_files'
    
    id = Column(Integer, primary_key=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    content = Column(Text, nullable=False)
    version = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default=UserRole.GENERIC_USER.value)
    created_at = Column(DateTime, default=datetime.utcnow) 