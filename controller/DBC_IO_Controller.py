from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, pyqtSignal
from model.dbc_model import DBCModel
from .dbc_io_handler import DBC_IO_Handler

class DBC_IO_Controller(QObject):
    # Signals for notifying the view of changes
    handler_created = pyqtSignal(DBC_IO_Handler)  # Emitted when a new handler is created
    handler_removed = pyqtSignal(str)  # Emitted when a handler is removed
    handlers_changed = pyqtSignal(list)  # Emitted when the handlers list changes
    dbc_exported = pyqtSignal(str)  # Emitted when a DBC file is exported
    
    def __init__(self):
        super().__init__()
        self.model = DBCModel()
        self.handlers = {}  # Dictionary to store DBC_IO_Handler instances
        
    def import_dbc(self, parent_window=None):
        """
        Opens a file dialog to select and load a DBC file
        Returns the handler if successful, None otherwise
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
                return handler, file_name, None
            else:
                return None, None, error
        
        return None, None, None
    
    def export_dbc(self, file_path, parent_window=None):
        """
        Opens a file dialog to select a location to export the DBC file
        
        Args:
            file_path (str): Path of the source DBC file to export
            parent_window: Parent window for the file dialog
            
        Returns:
            tuple[bool, str, str]: (Success status, Target file path, Error message if any)
        """
        if file_path not in self.handlers:
            return False, None, "File not loaded in the application"
            
        target_file, _ = QFileDialog.getSaveFileName(
            parent_window,
            "Export DBC File",
            "",
            "DBC Files (*.dbc);;All Files (*.*)"
        )
        
        if not target_file:
            return False, None, "Export cancelled"
            
        # Ensure the file has .dbc extension if none is provided
        if not target_file.lower().endswith('.dbc'):
            target_file += '.dbc'
            
        # Use the model to perform the export
        success, error = self.model.export_dbc(file_path, target_file)
        
        if success:
            # Emit signal about successful export
            self.dbc_exported.emit(target_file)
            return True, target_file, None
        else:
            return False, None, error
    
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