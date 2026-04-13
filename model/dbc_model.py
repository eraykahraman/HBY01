import cantools
import shutil
from PyQt5.QtCore import QObject, pyqtSignal

class DBCModel(QObject):
    # Signals for notifying the view of changes
    dbc_loaded = pyqtSignal(str)  # Emitted when a DBC file is successfully loaded
    dbc_error = pyqtSignal(str)   # Emitted when there's an error loading a DBC file
    dbc_exported = pyqtSignal(str) # Emitted when a DBC file is successfully exported
    
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
        except cantools.database.errors.Error as e:
            # Handle specific cantools errors
            self.dbc_error.emit(f"DBC format error: {str(e)}")
            return False
        except FileNotFoundError:
            self.dbc_error.emit(f"File not found: {file_path}")
            return False
        except PermissionError:
            self.dbc_error.emit(f"Permission denied accessing file: {file_path}")
            return False
        except Exception as e:
            self.dbc_error.emit(f"Error loading DBC file: {str(e)}")
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
    
    def export_dbc(self, source_file_path, target_file_path):
        """
        Exports a DBC file to the specified path.
        This method saves the current database state to the target location.
        
        Args:
            source_file_path (str): Path to the source DBC file
            target_file_path (str): Path where the DBC file should be exported
            
        Returns:
            tuple[bool, str]: (Success status, Error message if any)
        """
        try:
            import unicodedata
            # Check if the source file exists in our database
            db = self.dbc_files.get(source_file_path)
            if not db:
                return False, "Source DBC file not loaded in the application"
            
            # Get the database string and normalize unicode to handle special characters like quotes
            dbc_string = db.as_dbc_string()
            normalized_string = unicodedata.normalize('NFKD', dbc_string)
            
            # Save the current database state to the target file with proper encoding error handling
            with open(target_file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(normalized_string)
            
            # Emit signal for successful export
            self.dbc_exported.emit(target_file_path)
            
            return True, None
        except FileNotFoundError:
            return False, f"Source file not found: {source_file_path}"
        except PermissionError:
            return False, f"Permission denied: Unable to write to {target_file_path}"
        except Exception as e:
            return False, f"Error exporting DBC file: {str(e)}"