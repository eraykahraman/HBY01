from typing import Optional, Tuple
from database.repository import DBCRepository
from database.models import DBCFile
from PyQt5.QtCore import QObject, pyqtSignal
from sqlalchemy.exc import SQLAlchemyError

class DBLoadController(QObject):
    """Controller for handling DBC file database operations"""
    
    # Signals
    dbc_loaded = pyqtSignal(DBCFile)  # Emitted when a DBC file is successfully loaded to DB
    dbc_load_failed = pyqtSignal(str)  # Emitted when loading fails, with error message
    
    def __init__(self):
        super().__init__()
        self.repository = DBCRepository()
    
    def load_dbc_to_database(self, file_name: str, file_path: str, content: str) -> Tuple[bool, Optional[DBCFile], Optional[str]]:
        """
        Load a DBC file into the database
        
        Args:
            file_name (str): Name of the DBC file
            file_path (str): Path to the DBC file
            content (str): Content of the DBC file
            
        Returns:
            Tuple[bool, Optional[DBCFile], Optional[str]]: 
                - Success status
                - DBCFile object if successful, None otherwise
                - Error message if failed, None otherwise
        """
        try:
            # Check if file already exists in database
            existing_file = self.repository.get_dbc_file_by_path(file_path)
            if existing_file:
                error_msg = f"File '{file_name}' already exists in database"
                self.dbc_load_failed.emit(error_msg)
                return False, None, error_msg
            
            # Save to database
            dbc_file = self.repository.save_dbc_file(
                file_name=file_name,
                file_path=file_path,
                content=content
            )
            
            if dbc_file:
                # Create a copy of the file name before emitting signal
                file_name = dbc_file.file_name
                self.dbc_loaded.emit(dbc_file)
                return True, dbc_file, None
            else:
                error_msg = "Failed to save DBC file to database"
                self.dbc_load_failed.emit(error_msg)
                return False, None, error_msg
                
        except SQLAlchemyError as e:
            error_msg = f"Database error: {str(e)}"
            self.dbc_load_failed.emit(error_msg)
            return False, None, error_msg
        except Exception as e:
            error_msg = f"Error loading DBC file to database: {str(e)}"
            self.dbc_load_failed.emit(error_msg)
            return False, None, error_msg
    
    def get_dbc_file(self, file_id: int) -> Optional[DBCFile]:
        """
        Get a DBC file from the database by ID
        
        Args:
            file_id (int): ID of the DBC file
            
        Returns:
            Optional[DBCFile]: DBCFile object if found, None otherwise
        """
        try:
            return self.repository.get_dbc_file(file_id)
        except SQLAlchemyError as e:
            self.dbc_load_failed.emit(f"Database error while retrieving file: {str(e)}")
            return None
    
    def get_dbc_file_by_path(self, file_path: str) -> Optional[DBCFile]:
        """
        Get a DBC file from the database by path
        
        Args:
            file_path (str): Path of the DBC file
            
        Returns:
            Optional[DBCFile]: DBCFile object if found, None otherwise
        """
        try:
            return self.repository.get_dbc_file_by_path(file_path)
        except SQLAlchemyError as e:
            self.dbc_load_failed.emit(f"Database error while retrieving file: {str(e)}")
            return None
    
    def get_all_dbc_files(self) -> list[DBCFile]:
        """
        Get all DBC files from the database
        
        Returns:
            list[DBCFile]: List of all DBC files
        """
        try:
            return self.repository.get_all_dbc_files()
        except SQLAlchemyError as e:
            self.dbc_load_failed.emit(f"Database error while retrieving files: {str(e)}")
            return []
    
    def update_dbc_file(self, file_id: int, content: str, version: Optional[str] = None) -> Optional[DBCFile]:
        """
        Update a DBC file in the database
        
        Args:
            file_id (int): ID of the DBC file to update
            content (str): New content for the DBC file
            version (Optional[str]): New version string
            
        Returns:
            Optional[DBCFile]: Updated DBCFile object if successful, None otherwise
        """
        try:
            updated_file = self.repository.update_dbc_file(file_id, content, version)
            if updated_file:
                self.dbc_loaded.emit(updated_file)
            return updated_file
        except SQLAlchemyError as e:
            self.dbc_load_failed.emit(f"Database error while updating file: {str(e)}")
            return None
    
    def delete_dbc_file(self, file_id: int) -> bool:
        """
        Delete a DBC file from the database
        
        Args:
            file_id (int): ID of the DBC file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        try:
            return self.repository.delete_dbc_file(file_id)
        except SQLAlchemyError as e:
            self.dbc_load_failed.emit(f"Database error while deleting file: {str(e)}")
            return False 