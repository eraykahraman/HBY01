from typing import Optional, Dict, Any, List
import cantools
from cantools.database import Database
from copy import deepcopy

class EditHandler:
    def __init__(self, database: Database):
        self.database = database
        self.original_database = deepcopy(database)

    def edit_signal_name(self, message_name: str, old_signal_name: str, new_signal_name: str) -> tuple[bool, str]:
        """
        Edit the name of a signal in a given message.
        Returns (success, error_message)
        """
        if not new_signal_name or not new_signal_name.strip():
            return False, "Signal name cannot be empty."
            
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message in both current and original database
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Check for uniqueness
        if any(s.name == new_signal_name for s in message.signals):
            return False, f"A signal with the name '{new_signal_name}' already exists in this message."
            
        # Find and update the signal
        for signal in message.signals:
            if signal.name == old_signal_name:
                # Update the signal name in the database
                signal.name = new_signal_name
                return True, ""
                
        return False, f"Signal '{old_signal_name}' not found in message '{message_name}'."

    def edit_signal_length(self, message_name: str, signal_name: str, new_length: int) -> tuple[bool, str]:
        """
        Edit the length of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        if new_length <= 0:
            return False, "Signal length must be greater than 0."
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Find and update the signal
        for signal in message.signals:
            if signal.name == signal_name:
                # Check if new length would exceed message length
                if signal.start + new_length > message.length * 8:
                    return False, f"Signal length would exceed message length. Maximum allowed: {message.length * 8 - signal.start} bits"
                # Update the signal length
                signal.length = new_length
                return True, ""
                
        return False, f"Signal '{signal_name}' not found in message '{message_name}'."

    def edit_signal_start_bit(self, message_name: str, signal_name: str, new_start_bit: int) -> tuple[bool, str]:
        """
        Edit the start bit of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        if new_start_bit < 0:
            return False, "Start bit cannot be negative."
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Find and update the signal
        for signal in message.signals:
            if signal.name == signal_name:
                # Check if new start bit + length would exceed message length
                if new_start_bit + signal.length > message.length * 8:
                    return False, f"Signal would exceed message length. Maximum allowed start bit: {message.length * 8 - signal.length}"
                # Update the signal start bit
                signal.start = new_start_bit
                return True, ""
                
        return False, f"Signal '{signal_name}' not found in message '{message_name}'."

    def get_diff(self) -> Dict[str, Any]:
        """
        Get the differences between the original and edited database
        
        Returns:
            Dict[str, Any]: Dictionary containing the differences
        """
        diffs = {}
        for msg_idx, msg in enumerate(self.database.messages):
            orig_msg = self.original_database.messages[msg_idx]
            if msg.name != orig_msg.name:
                diffs[f"message_{msg_idx}"] = {
                    "type": "message_name",
                    "old": orig_msg.name,
                    "new": msg.name
                }
            for sig_idx, sig in enumerate(msg.signals):
                orig_sig = orig_msg.signals[sig_idx]
                if sig.name != orig_sig.name:
                    diffs[f"signal_{msg_idx}_{sig_idx}"] = {
                        "type": "signal_name",
                        "message": msg.name,
                        "old": orig_sig.name,
                        "new": sig.name
                    }
        return diffs

    def save_to_file(self, file_path: str) -> bool:
        """
        Save the current in-memory DBC database to the specified file.
        Returns True if successful, False otherwise.
        """
        if not self.database:
            return False
        try:
            # Get the database as DBC string
            dbc_string = self.database.as_dbc_string()
            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(dbc_string)
            return True
        except Exception as e:
            print(f"Error saving DBC file: {e}")
            return False 