from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool
from contextlib import contextmanager
from typing import Generator

from .config import DatabaseConfig
from .models import Base

# Database connection settings
DATABASE_URL = "postgresql://dbc1:s7s5dbaE@localhost:5432/dbc"

# Create engine with NullPool to avoid connection issues
engine = create_engine(DATABASE_URL, poolclass=NullPool)

# Create session factory
session_factory = sessionmaker(bind=engine)

class DatabaseSession:
    """Database session manager"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = session_factory
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables from the database"""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[scoped_session, None, None]:
        """Get a database session"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

def recreate_tables():
    """Drop and recreate all tables"""
    db_session.drop_tables()
    db_session.create_tables()

# Create a global instance
db_session = DatabaseSession() 