from typing import Optional
import cantools

class EditHandler:
    def __init__(self, database):
        self.database = database

    def edit_signal_name_in_db(self, message_name: str, old_signal_name: str, new_signal_name: str) -> bool:
        """
        Update the signal name in the cantools DBC database object.
        Returns True if successful, False otherwise.
        """
        if not self.database:
            return False
        for msg in getattr(self.database, 'messages', []):
            if msg.name == message_name:
                for signal in getattr(msg, 'signals', []):
                    if signal.name == old_signal_name:
                        signal.name = new_signal_name
                        return True
        return False

    def save_to_file(self, file_path: str) -> bool:
        """
        Save the current in-memory DBC database to the specified file.
        Returns True if successful, False otherwise.
        """
        if not self.database:
            return False
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.database.as_dbc_string())
            return True
        except Exception as e:
            print(f"Error saving DBC file: {e}")
            return False 