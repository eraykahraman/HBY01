import cantools

class DBCModel:
    def __init__(self):
        self.dbc_files = {}  # Dictionary to store multiple DBC files
        
    def load_dbc(self, file_path):
        """
        Loads a DBC file from the given path
        Returns (True, None) if successful, (False, error_message) otherwise
        """
        try:
            db = cantools.database.load_file(file_path)
            self.dbc_files[file_path] = db
            return True, None
        except Exception as e:
            return False, str(e)
            
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