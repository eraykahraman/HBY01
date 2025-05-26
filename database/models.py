from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

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