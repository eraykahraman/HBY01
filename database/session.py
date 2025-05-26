from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator

from .config import DatabaseConfig
from .models import Base

class DatabaseSession:
    """Database session manager"""
    
    def __init__(self):
        self.engine = create_engine(DatabaseConfig.get_url())
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def create_tables(self):
        """Create all tables in the database"""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables from the database"""
        Base.metadata.drop_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
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

# Create a global instance
db_session = DatabaseSession() 