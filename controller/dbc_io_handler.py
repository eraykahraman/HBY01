from typing import Optional, Dict, Any, List
from cantools.database import Database
import os
from model.dbc_model import DBCModel
from PyQt5.QtCore import QObject, pyqtSignal

class DBC_IO_Handler(QObject):
    # Signal emitted when nodes list changes
    nodes_changed = pyqtSignal(list)
    
    def __init__(self, file_path: str, model: DBCModel):
        """
        Initialize a DBC IO Handler for a specific DBC file
        
        Args:
            file_path (str): Path to the DBC file
            model (DBCModel): Reference to the main DBC model
        """
        super().__init__()
        self.file_path = file_path
        self.model = model
        self.database: Optional[Database] = None
        self.is_loaded: bool = False
        self.nodes: List[Dict[str, Any]] = []  # Store the list of nodes
        # Connect to model signals to capture error messages
        self.model.dbc_error.connect(self._on_model_error)
        self.last_error: Optional[str] = None
        
    def _on_model_error(self, error_msg: str):
        """Store the last error message from the model"""
        self.last_error = error_msg
        
    def load_dbc(self) -> tuple[bool, Optional[str]]:
        """
        Load the DBC file into memory using the DBCModel
        
        Returns:
            tuple[bool, Optional[str]]: (Success status, Error message if any)
        """
        try:
            if not os.path.exists(self.file_path):
                return False, f"File not found: {self.file_path}"
                
            self.last_error = None  # Reset last error before attempting load
            if self.model.load_dbc(self.file_path):
                self.database = self.model.get_dbc(self.file_path)
                self.is_loaded = True
                # Parse nodes after successful load
                self.nodes = self.parse_nodes()
                self.nodes_changed.emit(self.nodes)
                return True, None
            else:
                return False, self.last_error or "Failed to load DBC file"
            
        except Exception as e:
            return False, f"Error loading DBC file: {str(e)}"
            
    def get_database(self) -> Optional[Database]:
        """
        Returns the DBC database
        """
        return self.model.get_dbc(self.file_path)
        
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the DBC file
        
        Returns:
            Dict[str, Any]: Dictionary containing file information
        """
        db = self.get_database()
        return {
            "file_path": self.file_path,
            "file_name": os.path.basename(self.file_path),
            "is_loaded": self.is_loaded,
            "messages_count": len(db.messages) if db else 0,
            "nodes_count": len(db.nodes) if db else 0
        }
        
    def parse_nodes(self) -> List[Dict[str, Any]]:
        """
        Parse all nodes from the DBC database
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing node information
                Each dictionary contains:
                - name (str): The name of the node
                - comment (Optional[str]): The comment associated with the node
        """
        if not self.is_valid():
            return []
            
        nodes = []
        for node in self.database.nodes:
            node_info = {
                "name": node.name,
                "comment": node.comment
            }
            nodes.append(node_info)
            
        return nodes
        
    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Returns the current list of nodes
        
        Returns:
            List[Dict[str, Any]]: List of node information dictionaries
        """
        return self.nodes
        
    def unload(self) -> bool:
        """
        Unload the DBC file from memory using the model
        
        Returns:
            bool: True if successfully unloaded, False otherwise
        """
        if self.model.remove_dbc(self.file_path):
            self.database = None
            self.is_loaded = False
            self.nodes = []  # Clear nodes list
            self.nodes_changed.emit(self.nodes)  # Emit empty list
            return True
        return False
        
    def cleanup(self):
        """
        Clean up handler resources and disconnect signals
        """
        # Disconnect from model signals
        try:
            self.model.dbc_error.disconnect(self._on_model_error)
        except:
            pass  # Signal might already be disconnected
        
        # Clear references
        self.database = None
        self.model = None
        self.is_loaded = False
        self.last_error = None
        self.nodes = []
        
    def is_valid(self) -> bool:
        """
        Check if the handler is valid and has a loaded database
        
        Returns:
            bool: True if the handler is valid and has a loaded database
        """
        return self.is_loaded and self.get_database() is not None
        
    def get_file_path(self) -> str:
        """
        Returns the file path of this handler
        """
        return self.file_path 