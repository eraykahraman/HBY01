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
                return self.model.get_dbc(file_name), file_name, None
            else:
                return None, None, "Failed to load DBC file"
        
        return None, None, None
    
    def remove_dbc(self, file_path):
        """
        Removes a DBC file from the model
        Returns True if successful, False otherwise
        """
        return self.model.remove_dbc(file_path)
    
    def get_dbc(self, file_path):
        """
        Returns the DBC database for the given file path
        """
        return self.model.get_dbc(file_path)
    
    def get_all_dbc_files(self):
        """
        Returns a list of all loaded DBC file paths
        """
        return self.model.get_all_dbc_files() 