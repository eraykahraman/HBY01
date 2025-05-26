from typing import List, Optional
from datetime import datetime

from .models import DBCFile, User
from .session import db_session

class DBCRepository:
    """Repository for DBC file operations"""
    
    @staticmethod
    def save_dbc_file(file_name: str, file_path: str, content: str, version: Optional[str] = None) -> DBCFile:
        """Save a DBC file to the database"""
        with db_session.get_session() as session:
            dbc_file = DBCFile(
                file_name=file_name,
                file_path=file_path,
                content=content,
                version=version
            )
            session.add(dbc_file)
            session.commit()
            session.refresh(dbc_file)
            return dbc_file
    
    @staticmethod
    def get_dbc_file(file_id: int) -> Optional[DBCFile]:
        """Get a DBC file by ID"""
        with db_session.get_session() as session:
            return session.query(DBCFile).filter(DBCFile.id == file_id).first()
    
    @staticmethod
    def get_dbc_file_by_path(file_path: str) -> Optional[DBCFile]:
        """Get a DBC file by path"""
        with db_session.get_session() as session:
            return session.query(DBCFile).filter(DBCFile.file_path == file_path).first()
    
    @staticmethod
    def get_all_dbc_files() -> List[DBCFile]:
        """Get all DBC files"""
        with db_session.get_session() as session:
            return session.query(DBCFile).all()
    
    @staticmethod
    def update_dbc_file(file_id: int, content: str, version: Optional[str] = None) -> Optional[DBCFile]:
        """Update a DBC file"""
        with db_session.get_session() as session:
            dbc_file = session.query(DBCFile).filter(DBCFile.id == file_id).first()
            if dbc_file:
                dbc_file.content = content
                dbc_file.version = version
                dbc_file.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(dbc_file)
            return dbc_file
    
    @staticmethod
    def delete_dbc_file(file_id: int) -> bool:
        """Delete a DBC file"""
        with db_session.get_session() as session:
            dbc_file = session.query(DBCFile).filter(DBCFile.id == file_id).first()
            if dbc_file:
                session.delete(dbc_file)
                session.commit()
                return True
            return False

class UserRepository:
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        with db_session.get_session() as session:
            return session.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(username: str, password_hash: str) -> Optional[User]:
        with db_session.get_session() as session:
            if session.query(User).filter(User.username == username).first():
                return None  # Username already exists
            user = User(username=username, password_hash=password_hash)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    @staticmethod
    def get_user_password_hash(username: str) -> Optional[str]:
        with db_session.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            return user.password_hash if user else None 