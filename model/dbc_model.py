import cantools
from PyQt5.QtCore import QObject, pyqtSignal

class DBCModel(QObject):
    # Signals for notifying the view of changes
    dbc_loaded = pyqtSignal(str)  # Emitted when a DBC file is successfully loaded
    dbc_error = pyqtSignal(str)   # Emitted when there's an error loading a DBC file
    
    def __init__(self):
        super().__init__()
        self.current_dbc = None
        self.current_file_path = None
        
    def load_dbc(self, file_path):
        """
        Loads a DBC file from the given path
        Returns True if successful, False otherwise
        """
        try:
            self.current_dbc = cantools.database.load_file(file_path)
            self.current_file_path = file_path
            self.dbc_loaded.emit(file_path)
            return True
        except Exception as e:
            self.dbc_error.emit(str(e))
            return False
            
    def get_current_dbc(self):
        """
        Returns the currently loaded DBC database
        """
        return self.current_dbc
        
    def get_current_file_path(self):
        """
        Returns the path of the currently loaded DBC file
        """
        return self.current_file_path
        
    def clear_current_dbc(self):
        """
        Clears the currently loaded DBC database
        """
        self.current_dbc = None
        self.current_file_path = None 