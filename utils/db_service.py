import os
import hashlib
from typing import Optional, List, Dict, Any, Tuple
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_

from utils.db_manager import DatabaseManager
from model.dbc_orm import DBCFile
from utils import db_manager, config
import json

class DBCDatabaseService:
    """
    Service class for DBC file database operations.
    Provides methods for storing and retrieving DBC file data.
    """
    
    def __init__(self, custom_db_manager: DatabaseManager = None):
        """
        Initialize the DBC database service.
        
        Args:
            custom_db_manager (DatabaseManager, optional): Database manager to use.
                If None, uses the global db_manager instance.
        """
        self.logger = logging.getLogger(__name__)
        # Fix the reference to db_manager by using the parameter name that doesn't clash
        self.db_manager = custom_db_manager if custom_db_manager else db_manager
    
    def init_database(self) -> bool:
        """
        Initialize the database from the configuration.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Get connection string from config
        conn_string = config.get_db_connection_string()
        if not conn_string:
            self.logger.info("Database is disabled in configuration")
            return False
        
        # Initialize database connection
        if not self.db_manager.initialize(conn_string):
            self.logger.error("Failed to initialize database connection")
            return False
        
        # Create tables if they don't exist
        if not self.db_manager.create_tables():
            self.logger.error("Failed to create database tables")
            return False
        
        return True
    
    def is_database_enabled(self) -> bool:
        """
        Check if database is enabled and initialized.
        
        Returns:
            bool: True if enabled and initialized, False otherwise
        """
        return config.get("database", "enabled") and self.db_manager.engine is not None
    
    def store_dbc_file(self, file_path: str, store_content: bool = False) -> Optional[int]:
        """
        Store DBC file information in the database.
        
        Args:
            file_path (str): Path to the DBC file
            store_content (bool, optional): Whether to store file content in the database
        
        Returns:
            Optional[int]: ID of the stored DBC file or None if failed
        """
        if not self.is_database_enabled():
            self.logger.warning("Database not enabled, skipping DBC file storage")
            return None
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                self.logger.error(f"File not found: {file_path}")
                return None
            
            # Get file information
            file_size = os.path.getsize(file_path)
            file_name = os.path.basename(file_path)
            
            # Calculate file hash
            file_hash = None
            with open(file_path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            # Read file content if requested
            content = None
            if store_content:
                with open(file_path, 'rb') as f:
                    content = f.read()
            
            # Start database session
            session = self.db_manager.get_session()
            
            try:
                # Check if file already exists (by hash)
                existing_file = session.query(DBCFile).filter_by(file_hash=file_hash).first()
                if existing_file:
                    # Update last accessed time
                    existing_file.last_accessed = datetime.utcnow()
                    session.commit()
                    self.logger.info(f"Found existing DBC file in database: {file_name}")
                    return existing_file.id
                
                # Create new DBC file record
                dbc_file = DBCFile(
                    filename=file_name,
                    filepath=file_path,
                    file_hash=file_hash,
                    file_size=file_size,
                    content=content,
                    last_accessed=datetime.utcnow()
                )
                
                session.add(dbc_file)
                session.commit()
                
                return dbc_file.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error storing DBC file: {str(e)}")
                return None
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error storing DBC file: {str(e)}")
            return None
    
    def update_dbc_file_metadata(self, dbc_id: int, nodes_count: int, messages_count: int, signals_count: int, metadata: Dict = None) -> bool:
        """
        Update DBC file metadata (counts and general information).
        
        Args:
            dbc_id (int): ID of the DBC file
            nodes_count (int): Number of nodes
            messages_count (int): Number of messages
            signals_count (int): Number of signals
            metadata (Dict, optional): Additional metadata
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_database_enabled():
            self.logger.warning("Database not enabled, skipping metadata update")
            return False
        
        try:
            session = self.db_manager.get_session()
            
            try:
                # Get DBC file
                dbc_file = session.query(DBCFile).get(dbc_id)
                if not dbc_file:
                    self.logger.error(f"DBC file with ID {dbc_id} not found")
                    return False
                
                # Update counts
                dbc_file.nodes_count = nodes_count
                dbc_file.messages_count = messages_count
                dbc_file.signals_count = signals_count
                
                # Update metadata if provided
                if metadata:
                    dbc_file.file_metadata = metadata
                
                # Commit changes
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error updating DBC metadata: {str(e)}")
                return False
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error updating DBC metadata: {str(e)}")
            return False
    
    def get_dbc_files(self) -> List[Dict[str, Any]]:
        """
        Get a list of all DBC files in the database.
        
        Returns:
            List[Dict[str, Any]]: List of DBC file dictionaries
        """
        if not self.is_database_enabled():
            return []
        
        try:
            session = self.db_manager.get_session()
            
            try:
                dbc_files = session.query(DBCFile).all()
                
                result = []
                for dbc_file in dbc_files:
                    result.append({
                        "id": dbc_file.id,
                        "filename": dbc_file.filename,
                        "filepath": dbc_file.filepath,
                        "file_size": dbc_file.file_size,
                        "version": dbc_file.version,
                        "created_at": dbc_file.created_at,
                        "updated_at": dbc_file.updated_at,
                        "last_accessed": dbc_file.last_accessed,
                        "nodes_count": dbc_file.nodes_count,
                        "messages_count": dbc_file.messages_count,
                        "signals_count": dbc_file.signals_count
                    })
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error getting DBC files: {str(e)}")
            return []
    
    def get_dbc_file_by_hash(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get a DBC file by its hash.
        
        Args:
            file_hash (str): SHA-256 hash of the file
        
        Returns:
            Optional[Dict[str, Any]]: DBC file dictionary or None if not found
        """
        if not self.is_database_enabled():
            return None
        
        try:
            session = self.db_manager.get_session()
            
            try:
                dbc_file = session.query(DBCFile).filter_by(file_hash=file_hash).first()
                
                if not dbc_file:
                    return None
                
                result = {
                    "id": dbc_file.id,
                    "filename": dbc_file.filename,
                    "filepath": dbc_file.filepath,
                    "file_size": dbc_file.file_size,
                    "version": dbc_file.version,
                    "created_at": dbc_file.created_at,
                    "updated_at": dbc_file.updated_at,
                    "last_accessed": dbc_file.last_accessed,
                    "content": dbc_file.content,  # May be None if not stored
                    "nodes_count": dbc_file.nodes_count,
                    "messages_count": dbc_file.messages_count,
                    "signals_count": dbc_file.signals_count,
                    "file_metadata": dbc_file.file_metadata
                }
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error getting DBC file by hash: {str(e)}")
            return None
    
    def get_all_dbc_files(self) -> List[Dict[str, Any]]:
        """
        Get all DBC files from the database.
        
        Returns:
            List[Dict[str, Any]]: List of DBC file dictionaries
        """
        if not self.is_database_enabled():
            return []
        
        try:
            session = self.db_manager.get_session()
            
            try:
                dbc_files = session.query(DBCFile).all()
                
                result = []
                for dbc_file in dbc_files:
                    result.append({
                        "id": dbc_file.id,
                        "filename": dbc_file.filename,
                        "filepath": dbc_file.filepath,
                        "file_size": dbc_file.file_size,
                        "file_hash": dbc_file.file_hash,
                        "version": dbc_file.version,
                        "created_at": dbc_file.created_at,
                        "updated_at": dbc_file.updated_at,
                        "last_accessed": dbc_file.last_accessed,
                        "content": dbc_file.content,
                        "nodes_count": dbc_file.nodes_count,
                        "messages_count": dbc_file.messages_count,
                        "signals_count": dbc_file.signals_count,
                        "file_metadata": dbc_file.file_metadata
                    })
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error getting all DBC files: {str(e)}")
            return []
    
    def search_dbc_files(self, search_term: str) -> List[Dict[str, Any]]:
        """
        Search for DBC files by filename.
        
        Args:
            search_term (str): Search term
        
        Returns:
            List[Dict[str, Any]]: List of matching DBC files
        """
        if not self.is_database_enabled():
            return []
        
        try:
            session = self.db_manager.get_session()
            
            try:
                # Search in filenames and metadata
                dbc_files = session.query(DBCFile).filter(
                    DBCFile.filename.ilike(f"%{search_term}%")
                ).all()
                
                result = []
                for dbc_file in dbc_files:
                    result.append({
                        "id": dbc_file.id,
                        "filename": dbc_file.filename,
                        "filepath": dbc_file.filepath,
                        "file_size": dbc_file.file_size,
                        "version": dbc_file.version,
                        "created_at": dbc_file.created_at,
                        "updated_at": dbc_file.updated_at,
                        "last_accessed": dbc_file.last_accessed,
                        "nodes_count": dbc_file.nodes_count,
                        "messages_count": dbc_file.messages_count,
                        "signals_count": dbc_file.signals_count
                    })
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error searching DBC files: {str(e)}")
            return [] 