from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QObject, pyqtSignal
from model.dbc_model import DBCModel

class DBC_IO_Controller(QObject):
    # Signals for DBC operations
    dbc_loaded = pyqtSignal(str, object)  # Emits (file_path, db) when DBC is loaded
    dbc_error = pyqtSignal(str)           # Emits error message when loading fails
    dbc_removed = pyqtSignal(str)         # Emits file_path when DBC is removed
    
    def __init__(self):
        super().__init__()
        self.model = DBCModel()
        
    def import_dbc(self, parent_window=None):
        """
        Opens a file dialog to select and load a DBC file
        Emits appropriate signals based on the result
        """
        file_name, _ = QFileDialog.getOpenFileName(
            parent_window,
            "Select DBC File",
            "",
            "DBC Files (*.dbc);;All Files (*.*)"
        )
        
        if file_name:
            if self.model.load_dbc(file_name):
                db = self.model.get_dbc(file_name)
                self.dbc_loaded.emit(file_name, db)
                return True
            else:
                self.dbc_error.emit("Failed to load DBC file")
                return False
        
        return False
    
    def remove_dbc(self, file_path):
        """
        Removes a DBC file from the model
        Emits dbc_removed signal if successful
        """
        if self.model.remove_dbc(file_path):
            self.dbc_removed.emit(file_path)
            return True
        return False
    
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