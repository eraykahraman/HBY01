import cantools
from PyQt5.QtCore import QObject, pyqtSignal

class DBCModel(QObject):
    # Signals for notifying the view of changes
    dbc_loaded = pyqtSignal(str)  # Emitted when a DBC file is successfully loaded
    dbc_error = pyqtSignal(str)   # Emitted when there's an error loading a DBC file
    
    def __init__(self):
        super().__init__()
        self.dbc_files = {}  # Dictionary to store multiple DBC files
        
    def load_dbc(self, file_path):
        """
        Loads a DBC file from the given path
        Returns True if successful, False otherwise
        """
        try:
            db = cantools.database.load_file(file_path)
            self.dbc_files[file_path] = db
            self.dbc_loaded.emit(file_path)
            return True
        except Exception as e:
            self.dbc_error.emit(str(e))
            return False
            
    def get_dbc(self, file_path):
        """
        Returns the DBC database for the given file path
        """
        return self.dbc_files.get(file_path)
        
    def remove_dbc(self, file_path):
        """
        Removes a DBC file from the model
        Returns True if successful, False otherwise
        """
        if file_path in self.dbc_files:
            del self.dbc_files[file_path]
            return True
        return False
        
    def get_all_dbc_files(self):
        """
        Returns a list of all loaded DBC file paths
        """
        return list(self.dbc_files.keys()) 