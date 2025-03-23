from PyQt5.QtWidgets import QFileDialog
from model.dbc_model import DBCModel

class DBC_IO_Controller:
    def __init__(self):
        self.model = DBCModel()
        
    def import_dbc(self, parent_window=None):
        """
        Opens a file dialog to select and load a DBC file
        Returns the loaded database if successful, None otherwise
        """
        file_name, _ = QFileDialog.getOpenFileName(
            parent_window,
            "Select DBC File",
            "",
            "DBC Files (*.dbc);;All Files (*.*)"
        )
        
        if file_name:
            if self.model.load_dbc(file_name):
                return self.model.get_current_dbc(), file_name, None
            else:
                return None, None, "Failed to load DBC file"
        
        return None, None, None
    
    def remove_dbc(self, file_path):
        """
        Removes a DBC file from the model
        Returns True if successful, False otherwise
        """
        if self.model.get_current_file_path() == file_path:
            self.model.clear_current_dbc()
            return True
        return False
    
    def get_current_dbc(self):
        """
        Returns the currently loaded DBC database
        """
        return self.model.get_current_dbc()
    
    def clear_current_dbc(self):
        """
        Clears the currently loaded DBC database
        """
        self.model.clear_current_dbc() 