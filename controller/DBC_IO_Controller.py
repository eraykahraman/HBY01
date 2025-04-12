from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, pyqtSignal
from model.dbc_model import DBCModel
from .dbc_io_handler import DBC_IO_Handler
from utils.db_service import DBCDatabaseService
import logging
import os

class DBC_IO_Controller(QObject):
    # Signals for notifying the view of changes
    handler_created = pyqtSignal(DBC_IO_Handler)  # Emitted when a new handler is created
    handler_removed = pyqtSignal(str)  # Emitted when a handler is removed
    handlers_changed = pyqtSignal(list)  # Emitted when the handlers list changes
    db_error = pyqtSignal(str)  # Emitted when there's a database error
    
    def __init__(self):
        super().__init__()
        self.model = DBCModel()
        self.handlers = {}  # Dictionary to store DBC_IO_Handler instances
        self.logger = logging.getLogger(__name__)
        
        # Initialize database service
        self.db_service = DBCDatabaseService()
        self.init_database()
        
    def init_database(self):
        """Initialize database connection if enabled in config"""
        try:
            if self.db_service.init_database():
                self.logger.info("Database initialized successfully")
            else:
                self.logger.info("Database not enabled or initialization failed")
        except Exception as e:
            self.logger.error(f"Database initialization error: {str(e)}")
            self.db_error.emit(f"Database initialization error: {str(e)}")
        
    def import_dbc(self, parent_window=None, store_in_db=True):
        """
        Opens a file dialog to select and load a DBC file
        
        Args:
            parent_window: Parent window for the file dialog
            store_in_db (bool): Whether to store the file in the database
            
        Returns:
            tuple: (handler, file_name, error)
        """
        file_name, _ = QFileDialog.getOpenFileName(
            parent_window,
            "Select DBC File",
            "",
            "DBC Files (*.dbc);;All Files (*.*)"
        )
        
        if file_name:
            # Create a new handler for this DBC file
            handler = DBC_IO_Handler(file_name, self.model)
            success, error = handler.load_dbc()
            if success:
                self.handlers[file_name] = handler
                self.handler_created.emit(handler)
                self.handlers_changed.emit(list(self.handlers.values()))
                
                # Store in database if database is enabled and store_in_db is True
                if store_in_db:
                    try:
                        if self.db_service.is_database_enabled():
                            # Store file info
                            dbc_id = self.db_service.store_dbc_file(file_name)
                            if dbc_id:
                                # Get summary information
                                file_info = handler.get_file_info()
                                
                                # Update metadata
                                self.db_service.update_dbc_file_metadata(
                                    dbc_id, 
                                    file_info['nodes_count'],
                                    file_info['messages_count'],
                                    file_info['signals_count'],
                                    {
                                        'version': file_info.get('version'),
                                        'bit_timing': file_info.get('bit_timing'),
                                        'nodes_timing': file_info.get('nodes_timing'),
                                        'environment_variables': file_info.get('environment_variables'),
                                    }
                                )
                                
                                self.logger.info(f"DBC file stored in database: {file_name}")
                    except Exception as e:
                        self.logger.error(f"Error storing DBC file in database: {str(e)}")
                        # Don't block user if database storage fails
                        self.db_error.emit(f"Warning: Database storage failed: {str(e)}")
                
                return handler, file_name, None
            else:
                return None, None, error
        
        return None, None, None
    
    def remove_dbc(self, file_path):
        """
        Removes a DBC file from the model and cleans up the handler
        Returns True if successful, False otherwise
        """
        if file_path in self.handlers:
            handler = self.handlers[file_path]
            # First unload the DBC file
            if handler.unload():
                # Clean up handler resources
                handler.cleanup()
                # Remove handler from our dictionary
                del self.handlers[file_path]
                # Notify views
                self.handler_removed.emit(file_path)
                self.handlers_changed.emit(list(self.handlers.values()))
                return True
        return False
    
    def get_handler(self, file_path):
        """
        Returns the handler for a specific DBC file
        """
        return self.handlers.get(file_path)
    
    def get_all_handlers(self):
        """
        Returns a list of all handlers
        """
        return list(self.handlers.values())
        
    def get_recent_dbc_files(self, limit=10):
        """
        Get a list of recently accessed DBC files from the database.
        
        Args:
            limit (int): Maximum number of files to return
            
        Returns:
            list: List of dbc file info dictionaries
        """
        try:
            if not self.db_service.is_database_enabled():
                return []
                
            files = self.db_service.get_dbc_files()
            # Sort by last_accessed time, most recent first
            files.sort(key=lambda x: x.get('last_accessed', 0) or 0, reverse=True)
            return files[:limit]
        except Exception as e:
            self.logger.error(f"Error getting recent DBC files: {str(e)}")
            return []
            
    def search_dbc_files(self, search_term):
        """
        Search for DBC files in the database
        
        Args:
            search_term (str): Search term to match against filenames, nodes, etc.
            
        Returns:
            list: List of matching dbc file info dictionaries
        """
        try:
            if not self.db_service.is_database_enabled():
                return []
                
            return self.db_service.search_dbc_files(search_term)
        except Exception as e:
            self.logger.error(f"Error searching DBC files: {str(e)}")
            return []
            
    def load_dbc_files_from_database(self):
        """
        Load all DBC files from the database and create handlers for them.
        
        Returns:
            int: Number of files loaded
        """
        try:
            if not self.db_service.is_database_enabled():
                self.logger.info("Database not enabled, skipping database file loading")
                return 0
                
            # Get all DBC files from database
            dbc_files = self.db_service.get_all_dbc_files()
            
            # Track how many files were loaded
            loaded_count = 0
            
            # Load each file
            for file_info in dbc_files:
                file_path = file_info.get('filepath')
                
                # Skip if already loaded
                if file_path in self.handlers:
                    continue
                    
                # Skip if file doesn't exist on disk
                if not os.path.exists(file_path):
                    self.logger.warning(f"DBC file in database not found on disk: {file_path}")
                    continue
                
                # Create a new handler for this DBC file
                handler = DBC_IO_Handler(file_path, self.model)
                success, error = handler.load_dbc()
                
                if success:
                    self.handlers[file_path] = handler
                    self.handler_created.emit(handler)
                    loaded_count += 1
                else:
                    self.logger.error(f"Failed to load DBC file from database: {file_path}, Error: {error}")
            
            # Update all handlers
            self.handlers_changed.emit(list(self.handlers.values()))
            
            return loaded_count
            
        except Exception as e:
            self.logger.error(f"Error loading DBC files from database: {str(e)}")
            self.db_error.emit(f"Error loading DBC files from database: {str(e)}")
            return 0 