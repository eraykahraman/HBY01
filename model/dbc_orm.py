from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, LargeBinary, JSON
from sqlalchemy.sql import func
from utils.db_manager import Base
import datetime

class DBCFile(Base):
    """Model for DBC files"""
    __tablename__ = 'dbc_files'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(512))
    file_hash = Column(String(64))  # SHA-256 hash of the file
    file_size = Column(Integer)  # Size in bytes
    content = Column(LargeBinary)  # Raw content of the file (optional)
    version = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    last_accessed = Column(DateTime)
    
    # Store summary information as JSON
    nodes_count = Column(Integer, default=0)
    messages_count = Column(Integer, default=0)
    signals_count = Column(Integer, default=0)
    file_metadata = Column(JSON)  # Store any additional metadata about the file
    
    def __repr__(self):
        return f"<DBCFile id={self.id}, filename={self.filename}>" 