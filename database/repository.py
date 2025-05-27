from typing import List, Optional
from datetime import datetime

from .models import DBCFile, User, UserRole
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
        """
        Get a user by username
        
        Args:
            username (str): Username to search for
            
        Returns:
            Optional[User]: User object if found, None otherwise
        """
        with db_session.get_session() as session:
            return session.query(User).filter(User.username == username).first()

    @staticmethod
    def create_user(username: str, password_hash: str, role: str = UserRole.GENERIC_USER.value) -> Optional[User]:
        """
        Create a new user
        
        Args:
            username (str): Username for the new user
            password_hash (str): Hashed password
            role (str): User role (default: generic_user)
            
        Returns:
            Optional[User]: Created user object if successful, None otherwise
        """
        with db_session.get_session() as session:
            if session.query(User).filter(User.username == username).first():
                return None  # Username already exists
            user = User(username=username, password_hash=password_hash, role=role)
            session.add(user)
            session.commit()
            session.refresh(user)
            # Create a new instance with the same data to avoid detached instance issues
            return User(
                id=user.id,
                username=user.username,
                password_hash=user.password_hash,
                role=user.role,
                created_at=user.created_at
            )

    @staticmethod
    def get_user_password_hash(username: str) -> Optional[str]:
        """
        Get the password hash for a user
        
        Args:
            username (str): Username to get password hash for
            
        Returns:
            Optional[str]: Password hash if user exists, None otherwise
        """
        with db_session.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            return user.password_hash if user else None

    @staticmethod
    def get_user_role(username: str) -> Optional[str]:
        """
        Get the role of a user
        
        Args:
            username (str): Username to get role for
            
        Returns:
            Optional[str]: User role if found, None otherwise
        """
        with db_session.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            return user.role if user else None

    @staticmethod
    def update_user_role(username: str, new_role: str) -> bool:
        """
        Update the role of a user
        
        Args:
            username (str): Username to update
            new_role (str): New role to set
            
        Returns:
            bool: True if update successful, False otherwise
        """
        with db_session.get_session() as session:
            user = session.query(User).filter(User.username == username).first()
            if user:
                user.role = new_role
                session.commit()
                return True
            return False 