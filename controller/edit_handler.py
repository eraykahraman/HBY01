from typing import Optional, Dict, Any, List
import cantools
from cantools.database import Database
from copy import deepcopy
from cantools.database.can.attribute import Attribute
from cantools.database.can.signal import Signal

# Monkey patch the Signal class to handle None values properly during serialization
original_signal_init = Signal.__init__

def patched_signal_init(self, *args, **kwargs):
    # Call the original __init__
    original_signal_init(self, *args, **kwargs)
    
    # Ensure minimum and maximum are always floats, never None
    if self.minimum is None:
        if self.is_signed:
            self.minimum = -(2 ** (self.length - 1))
        else:
            self.minimum = 0.0
            
    if self.maximum is None:
        if self.is_signed:
            self.maximum = (2 ** (self.length - 1)) - 1
        else:
            self.maximum = (2 ** self.length) - 1

# Apply the monkey patch
Signal.__init__ = patched_signal_init

# Also patch Signal's __repr__ and __str__ methods to handle None values
original_signal_repr = Signal.__repr__

def patched_signal_repr(self):
    try:
        return original_signal_repr(self)
    except Exception as e:
        # Create a safe representation if the original fails
        return f"Signal(name='{self.name}', start={self.start}, length={self.length})"

Signal.__repr__ = patched_signal_repr

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

    def edit_signal_byte_order(self, message_name: str, signal_name: str, new_byte_order: str) -> tuple[bool, str]:
        """
        Edit the byte order of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        if new_byte_order not in ['little_endian', 'big_endian']:
            return False, "Byte order must be either 'little_endian' or 'big_endian'."
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        signal.byte_order = new_byte_order
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_is_signed(self, message_name: str, signal_name: str, is_signed: bool) -> tuple[bool, str]:
        """
        Edit whether a signal is signed in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        signal.is_signed = is_signed
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_scale(self, message_name: str, signal_name: str, new_scale: float) -> tuple[bool, str]:
        """
        Edit the scale factor of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        signal.scale = float(new_scale)
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_offset(self, message_name: str, signal_name: str, new_offset: float) -> tuple[bool, str]:
        """
        Edit the offset of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        signal.offset = float(new_offset)
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_minimum(self, message_name: str, signal_name: str, new_minimum: Optional[float]) -> tuple[bool, str]:
        """
        Edit the minimum value of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        # Check if minimum is less than maximum (if maximum exists)
                        if signal.maximum is not None and new_minimum is not None and new_minimum > signal.maximum:
                            return False, f"Minimum value ({new_minimum}) cannot be greater than maximum value ({signal.maximum})"
                        signal.minimum = new_minimum
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_maximum(self, message_name: str, signal_name: str, new_maximum: Optional[float]) -> tuple[bool, str]:
        """
        Edit the maximum value of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        # Check if maximum is greater than minimum (if minimum exists)
                        if signal.minimum is not None and new_maximum is not None and new_maximum < signal.minimum:
                            return False, f"Maximum value ({new_maximum}) cannot be less than minimum value ({signal.minimum})"
                        signal.maximum = new_maximum
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_unit(self, message_name: str, signal_name: str, new_unit: str) -> tuple[bool, str]:
        """
        Edit the unit of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        signal.unit = new_unit.strip()
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_comment(self, message_name: str, signal_name: str, new_comment: str) -> tuple[bool, str]:
        """
        Edit the comment of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        signal.comment = new_comment
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_receivers(self, message_name: str, signal_name: str, new_receivers: list) -> tuple[bool, str]:
        """
        Edit the receivers of a signal in a given message.
        Args:
            message_name: Name of the message containing the signal
            signal_name: Name of the signal to edit
            new_receivers: List of node names that receive this signal
            
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Validate that all receivers exist as nodes
        existing_nodes = {node.name: node for node in self.database.nodes}
        invalid_receivers = [r for r in new_receivers if r not in existing_nodes]
        if invalid_receivers:
            return False, f"Invalid receiver nodes: {', '.join(invalid_receivers)}"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        try:
                            # Only update the _receivers attribute
                            signal._receivers = [str(name) for name in new_receivers]
                            return True, ""
                        except Exception as e:
                            # If we can't set _receivers, try setting receivers directly
                            try:
                                signal.receivers = [str(name) for name in new_receivers]
                                return True, ""
                            except Exception as e2:
                                return False, f"Error updating receivers: {str(e2)}"
                        
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_is_multiplexer(self, message_name: str, signal_name: str, is_multiplexer: bool) -> tuple[bool, str]:
        """
        Edit whether a signal is a multiplexer in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        # Update multiplexer properties
                        signal.is_multiplexer = is_multiplexer
                        if is_multiplexer:
                            # If this is a multiplexer signal, clear multiplexer_ids and multiplexer_signal
                            signal.multiplexer_ids = None
                            signal.multiplexer_signal = None
                            # Set the multiplexer attribute for cantools export
                            signal.multiplexer = 'Multiplexer'
                            # Update all signals in the message that use this as their multiplexer
                            for other_signal in msg.signals:
                                if hasattr(other_signal, 'multiplexer_ids') and other_signal.multiplexer_ids:
                                    other_signal.multiplexer_signal = signal.name
                        else:
                            # If this is no longer a multiplexer, remove references from other signals
                            signal.multiplexer = None
                            for other_signal in msg.signals:
                                if other_signal.multiplexer_signal == signal.name:
                                    other_signal.multiplexer_signal = None
                                    other_signal.multiplexer_ids = None
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_multiplexer_id(self, message_name: str, signal_name: str, multiplexer_id: Optional[int]) -> tuple[bool, str]:
        """
        Edit the multiplexer ID of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        # Update multiplexer properties
                        signal.multiplexer_ids = [multiplexer_id] if multiplexer_id is not None else None
                        if multiplexer_id is not None:
                            # If setting a multiplexer ID, find the multiplexer signal in the message
                            signal.is_multiplexer = False
                            multiplexer_signal = next((s for s in msg.signals if s.is_multiplexer), None)
                            if multiplexer_signal:
                                signal.multiplexer_signal = multiplexer_signal.name
                                # Set the multiplexer attribute for cantools export
                                signal.multiplexer = str(multiplexer_id)
                            else:
                                return False, "No multiplexer signal found in the message"
                        else:
                            # If clearing multiplexer ID, clear multiplexer signal reference
                            signal.multiplexer_signal = None
                            signal.multiplexer = None
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def edit_signal_choices(self, message_name: str, signal_name: str, choices: Dict[int, str]) -> tuple[bool, str]:
        """
        Edit the value table (choices) of a signal in a given message.
        Args:
            message_name: Name of the message containing the signal
            signal_name: Name of the signal to edit
            choices: Dictionary mapping raw values to their descriptions
            
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message and signal
        for msg in self.database.messages:
            if msg.name == message_name:
                for signal in msg.signals:
                    if signal.name == signal_name:
                        try:
                            # Update the choices dictionary
                            signal._choices = {int(k): str(v) for k, v in choices.items()}
                            return True, ""
                        except Exception as e:
                            return False, f"Error updating choices: {str(e)}"
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

    def delete_signal(self, message_name: str, signal_name: str) -> tuple[bool, str]:
        """
        Delete a signal from a message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Find the signal to delete
        signal_to_delete = None
        for signal in message.signals:
            if signal.name == signal_name:
                signal_to_delete = signal
                break
                
        if not signal_to_delete:
            return False, f"Signal '{signal_name}' not found in message '{message_name}'."
            
        # Remove the signal from the message
        message.signals.remove(signal_to_delete)
        return True, ""

    def add_signal(self, message_name: str, signal_data: dict) -> tuple[bool, str]:
        """
        Add a new signal to a message.
        
        Args:
            message_name (str): Name of the message to add the signal to
            signal_data (dict): Dictionary containing the signal data
                Required keys:
                - name (str): Signal name
                - start (int): Start bit
                - length (int): Signal length in bits
                - byte_order (str): 'little_endian' or 'big_endian'
                - is_signed (bool): Whether the signal is signed
                
                Optional keys:
                - scale (float): Scale factor
                - offset (float): Signal offset
                - minimum (float): Minimum value
                - maximum (float): Maximum value
                - unit (str): Signal unit
                - receivers (list): List of receiver node names
                - comment (str): Signal comment
                - is_multiplexer (bool): Whether the signal is a multiplexer
                - multiplexer_id (int): Multiplexer identifier
                - is_float (bool): Whether the signal is a float value
                - choices (dict): Value to name mapping dictionary
        
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Validate required fields
        required_fields = ['name', 'start', 'length', 'byte_order', 'is_signed']
        for field in required_fields:
            if field not in signal_data:
                return False, f"Missing required field: {field}"
                
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Check if the signal name already exists in any message
        for msg in self.database.messages:
            for signal in msg.signals:
                if signal.name == signal_data['name']:
                    return False, f"Signal name '{signal_data['name']}' already exists in message '{msg.name}'."
        
        # Check if the signal would overlap with existing signals
        new_signal_end_bit = signal_data['start'] + signal_data['length'] - 1
        for signal in message.signals:
            signal_start_bit = signal.start
            signal_end_bit = signal.start + signal.length - 1
            
            # Check for overlap
            if (signal_data['start'] <= signal_end_bit and new_signal_end_bit >= signal_start_bit):
                return False, f"Signal would overlap with existing signal '{signal.name}'"
                
        # Check if signal exceeds message length
        if new_signal_end_bit >= message.length * 8:
            return False, f"Signal would exceed message length of {message.length * 8} bits."
            
        # Create new signal
        try:
            # Extract required parameters
            name = signal_data['name']
            start = int(signal_data['start'])  # Ensure integer
            length = int(signal_data['length'])  # Ensure integer
            byte_order = signal_data['byte_order']
            is_signed = bool(signal_data['is_signed'])  # Ensure boolean
            
            # Initialize with safe default values
            scale = 1.0
            offset = 0.0
            
            # For compatibility with the cantools parser, use explicit values instead of None
            # Default minimum/maximum based on the length and signedness of the signal
            if is_signed:
                default_min = -(2 ** (length - 1))
                default_max = (2 ** (length - 1)) - 1
            else:
                default_min = 0.0
                default_max = (2 ** length) - 1
                
            minimum = default_min
            maximum = default_max
            
            # Safely convert scale
            try:
                if 'scale' in signal_data and signal_data['scale'] is not None and signal_data['scale'] != '':
                    scale = float(signal_data['scale'])
            except (ValueError, TypeError) as e:
                return False, f"Invalid scale value: {signal_data.get('scale')}. It must be a valid number."
                
            # Safely convert offset
            try:
                if 'offset' in signal_data and signal_data['offset'] is not None and signal_data['offset'] != '':
                    offset = float(signal_data['offset'])
            except (ValueError, TypeError) as e:
                return False, f"Invalid offset value: {signal_data.get('offset')}. It must be a valid number."
            
            # Safely handle minimum (using explicit default if None)
            try:
                if 'minimum' in signal_data and signal_data['minimum'] is not None:
                    if signal_data['minimum'] == 0 or signal_data['minimum'] == '0':
                        minimum = 0.0
                    elif signal_data['minimum'] != '':
                        minimum = float(signal_data['minimum'])
            except (ValueError, TypeError) as e:
                # Use the default, don't use None
                pass
                
            # Safely handle maximum (using explicit default if None)
            try:
                if 'maximum' in signal_data and signal_data['maximum'] is not None:
                    if signal_data['maximum'] == 0 or signal_data['maximum'] == '0':
                        maximum = 0.0
                    elif signal_data['maximum'] != '':
                        maximum = float(signal_data['maximum'])
            except (ValueError, TypeError) as e:
                # Use the default, don't use None
                pass
                
            # Extract other optional parameters
            unit = str(signal_data.get('unit', ''))
            comment = str(signal_data.get('comment', ''))
            is_multiplexer = bool(signal_data.get('is_multiplexer', False))
            
            # Handle multiplexer_id (ensure it's an integer if present)
            multiplexer_id = None
            if 'multiplexer_id' in signal_data and signal_data['multiplexer_id'] is not None:
                if signal_data['multiplexer_id'] != -1:  # -1 means not multiplexed
                    try:
                        multiplexer_id = int(signal_data['multiplexer_id'])
                    except (ValueError, TypeError):
                        # Don't fail, just don't set it
                        pass
            
            is_float = bool(signal_data.get('is_float', False))
            choices = signal_data.get('choices', {})
            receivers = signal_data.get('receivers', [])
            
            # Create new signal - Fix the constructor parameters
            new_signal = Signal(
                name=name,
                start=start,
                length=length,
                byte_order=byte_order,
                is_signed=is_signed,
                scale=scale,
                offset=offset,
                minimum=minimum,
                maximum=maximum,
                unit=unit,
                comment=comment,
                receivers=receivers,
                is_multiplexer=is_multiplexer,
                is_float=is_float
            )
            
            # Set multiplexer_id separately if needed
            if multiplexer_id is not None:
                if hasattr(new_signal, 'multiplexer_ids'):
                    new_signal.multiplexer_ids = [multiplexer_id]
                    # Set multiplexer signal reference if this is a multiplexed signal
                    if not is_multiplexer:
                        # Find multiplexer signal in the message
                        multiplexer_signal = next((s for s in message.signals if s.is_multiplexer), None)
                        if multiplexer_signal:
                            new_signal.multiplexer_signal = multiplexer_signal.name
                            # Set multiplexer attribute for export
                            new_signal.multiplexer = str(multiplexer_id)
            
            # Add choices if any
            if choices:
                new_signal.choices = choices
                
            # Add signal to message
            message.signals.append(new_signal)
            return True, ""
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error creating signal: {str(e)}"

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

    def edit_message_name(self, old_message_name: str, new_message_name: str) -> tuple[bool, str]:
        """
        Edit the name of a message.
        Returns (success, error_message)
        """
        if not new_message_name or not new_message_name.strip():
            return False, "Message name cannot be empty."
            
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message in both current and original database
        message = None
        for msg in self.database.messages:
            if msg.name == old_message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{old_message_name}' not found."
            
        # Check for uniqueness
        if any(m.name == new_message_name for m in self.database.messages):
            return False, f"A message with the name '{new_message_name}' already exists."
            
        # Update the message name in the database
        message.name = new_message_name
        return True, ""

    def delete_message(self, message_name: str) -> tuple[bool, str]:
        """
        Delete a message from the database.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Remove the message from the database
        self.database.messages.remove(message)
        return True, ""

    def edit_message_frame_id(self, message_name: str, new_frame_id: int) -> tuple[bool, str]:
        """
        Edit the frame ID of a message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Validate frame ID
        if new_frame_id < 0:
            return False, "Frame ID cannot be negative."
            
        # Check if frame ID is within valid range based on extended frame flag
        if message.is_extended_frame:
            if new_frame_id > 0x1FFFFFFF:  # 29-bit max
                return False, "Extended frame ID cannot exceed 0x1FFFFFFF (29 bits)"
        else:
            if new_frame_id > 0x7FF:  # 11-bit max
                return False, "Standard frame ID cannot exceed 0x7FF (11 bits)"
                
        # Check for duplicate frame IDs
        for msg in self.database.messages:
            if msg != message and msg.frame_id == new_frame_id:
                return False, f"A message with frame ID 0x{new_frame_id:X} already exists."
                
        # Update the frame ID
        message.frame_id = new_frame_id
        return True, ""

    def edit_message_is_extended_frame(self, message_name: str, is_extended: bool) -> tuple[bool, str]:
        """
        Edit whether a message uses extended frame format.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # If switching to standard frame, validate current frame ID
        if not is_extended and message.frame_id > 0x7FF:
            return False, "Cannot switch to standard frame: frame ID exceeds 11 bits (0x7FF)"
            
        # Update the extended frame flag
        message.is_extended_frame = is_extended
        return True, ""

    def edit_message_senders(self, message_name: str, new_senders: list) -> tuple[bool, str]:
        """
        Edit the senders of a message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Validate that all senders exist as nodes
        existing_nodes = {node.name: node for node in self.database.nodes}
        invalid_senders = [s for s in new_senders if s not in existing_nodes]
        if invalid_senders:
            return False, f"Invalid sender nodes: {', '.join(invalid_senders)}"
            
        try:
            # Set the senders attribute directly (preferred for cantools)
            message.senders = [str(name) for name in new_senders]
            return True, ""
        except Exception:
            # Fallback: try to set the internal _senders attribute
            try:
                message._senders = [str(name) for name in new_senders]
                return True, ""
            except Exception as e:
                return False, f"Error updating senders: {str(e)}"

    def edit_message_send_type(self, message_name: str, new_send_type: str) -> tuple[bool, str]:
        """
        Edit the send type of a message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        try:
            # Make sure message.dbc exists
            if not hasattr(message, 'dbc') or message.dbc is None:
                try:
                    object.__setattr__(message, '_send_type', new_send_type)
                    return True, ""
                except Exception as e:
                    return False, "Cannot set send type - dbc attribute not available"
            
            # Make sure message.dbc.attributes is initialized
            if not hasattr(message.dbc, 'attributes') or message.dbc.attributes is None:
                message.dbc.attributes = {}
                
            # Check if the database has attribute definitions
            if hasattr(self.database, 'dbc') and hasattr(self.database.dbc, 'attribute_definitions'):
                # Get the attribute definition
                if 'GenMsgSendType' in self.database.dbc.attribute_definitions:
                    definition = self.database.dbc.attribute_definitions['GenMsgSendType']
                    
                    # Check if definition has _choices attribute
                    if hasattr(definition, '_choices') and definition._choices:
                        choices = definition._choices
                        
                        # Handle list of choices
                        if isinstance(choices, list):
                            # Try to find the new_send_type in the choices list
                            if new_send_type in choices:
                                # Find the index for this choice
                                choice_index = choices.index(new_send_type)
                                
                                # Try to create the attribute
                                try:
                                    attr_sig = str(Attribute.__init__.__code__.co_varnames)
                                    
                                    # Try different ways to create the attribute
                                    if 'value' in attr_sig and 'definition' in attr_sig:
                                        message.dbc.attributes['GenMsgSendType'] = Attribute(
                                            value=choice_index,
                                            definition=definition
                                        )
                                    elif len(attr_sig.split(',')) >= 3:  # At least self, arg1, arg2
                                        message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_index)
                                except Exception:
                                    pass
                            else:
                                # Try case-insensitive matching
                                matched = False
                                for i, value in enumerate(choices):
                                    if isinstance(value, str) and value.lower() == new_send_type.lower():
                                        choice_index = i
                                        try:
                                            message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_index)
                                            matched = True
                                            break
                                        except Exception:
                                            pass
                        
                        # Handle dictionary of choices
                        elif isinstance(choices, dict):
                            # Try to find the new_send_type in the choices values
                            if new_send_type in choices.values():
                                # Find the key for this choice value
                                for key, value in choices.items():
                                    if value == new_send_type:
                                        choice_key = key
                                        break
                                
                                # Try to create the attribute
                                try:
                                    message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_key)
                                except Exception:
                                    pass
                    
                    # Check if the definition has choices property
                    elif hasattr(definition, 'choices') and definition.choices:
                        choices = definition.choices
                        
                        # Handle based on type
                        if isinstance(choices, list):
                            if new_send_type in choices:
                                choice_index = choices.index(new_send_type)
                                try:
                                    message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_index)
                                except Exception as e:
                                    pass
                        elif isinstance(choices, dict):
                            if new_send_type in choices.values():
                                for key, value in choices.items():
                                    if value == new_send_type:
                                        try:
                                            message.dbc.attributes['GenMsgSendType'] = Attribute(definition, key)
                                            break
                                        except Exception as e:
                                            pass
                    
                    # Update _send_type for UI updates
                    try:
                        object.__setattr__(message, '_send_type', new_send_type)
                    except Exception:
                        pass
                    
                    return True, ""
                else:
                    # Still try to update _send_type for UI display
                    try:
                        object.__setattr__(message, '_send_type', new_send_type)
                        return True, ""
                    except Exception:
                        return False, "Cannot set send type - attribute not found"
            else:
                # Still try to update _send_type for UI display
                try:
                    object.__setattr__(message, '_send_type', new_send_type)
                    return True, ""
                except Exception:
                    return False, "Cannot set send type - definitions not available"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error updating send_type: {str(e)}"

    def edit_message_frame_format(self, message_name: str, new_frame_format: str) -> tuple[bool, str]:
        """
        Edit the frame format of a message.
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        try:
            # Make sure message.dbc exists
            if not hasattr(message, 'dbc') or message.dbc is None:
                try:
                    object.__setattr__(message, '_frame_format', new_frame_format)
                    return True, ""
                except Exception as e:
                    return False, "Cannot set frame format - dbc attribute not available"
            
            # Make sure message.dbc.attributes is initialized
            if not hasattr(message.dbc, 'attributes') or message.dbc.attributes is None:
                message.dbc.attributes = {}
                
            # Check if the database has attribute definitions
            if hasattr(self.database, 'dbc') and hasattr(self.database.dbc, 'attribute_definitions'):
                # Get the attribute definition
                if 'VFrameFormat' in self.database.dbc.attribute_definitions:
                    definition = self.database.dbc.attribute_definitions['VFrameFormat']
                    
                    # Check if definition has _choices attribute
                    if hasattr(definition, '_choices') and definition._choices:
                        choices = definition._choices
                        
                        # Handle list of choices
                        if isinstance(choices, list):
                            # Try to find the new_frame_format in the choices list
                            if new_frame_format in choices:
                                # Find the index for this choice
                                choice_index = choices.index(new_frame_format)
                                
                                # Try to create the attribute
                                try:
                                    attr_sig = str(Attribute.__init__.__code__.co_varnames)
                                    
                                    # Try different ways to create the attribute
                                    if 'value' in attr_sig and 'definition' in attr_sig:
                                        message.dbc.attributes['VFrameFormat'] = Attribute(
                                            value=choice_index,
                                            definition=definition
                                        )
                                    elif len(attr_sig.split(',')) >= 3:  # At least self, arg1, arg2
                                        message.dbc.attributes['VFrameFormat'] = Attribute(definition, choice_index)
                                except Exception as e:
                                    pass
                            else:
                                # Try case-insensitive matching
                                matched = False
                                for i, value in enumerate(choices):
                                    if isinstance(value, str) and value.lower() == new_frame_format.lower():
                                        choice_index = i
                                        try:
                                            message.dbc.attributes['VFrameFormat'] = Attribute(definition, choice_index)
                                            matched = True
                                            break
                                        except Exception as e:
                                            pass
                        
                        # Handle dictionary of choices
                        elif isinstance(choices, dict):
                            # Try to find the new_frame_format in the choices values
                            if new_frame_format in choices.values():
                                # Find the key for this choice value
                                for key, value in choices.items():
                                    if value == new_frame_format:
                                        choice_key = key
                                        break
                                
                                # Try to create the attribute
                                try:
                                    message.dbc.attributes['VFrameFormat'] = Attribute(definition, choice_key)
                                except Exception as e:
                                    pass
                    
                    # Check if the definition has choices property
                    elif hasattr(definition, 'choices') and definition.choices:
                        choices = definition.choices
                        
                        # Handle based on type
                        if isinstance(choices, list):
                            if new_frame_format in choices:
                                choice_index = choices.index(new_frame_format)
                                try:
                                    message.dbc.attributes['VFrameFormat'] = Attribute(definition, choice_index)
                                except Exception as e:
                                    pass
                        elif isinstance(choices, dict):
                            if new_frame_format in choices.values():
                                for key, value in choices.items():
                                    if value == new_frame_format:
                                        try:
                                            message.dbc.attributes['VFrameFormat'] = Attribute(definition, key)
                                            break
                                        except Exception as e:
                                            pass
                    
                    # Update _frame_format for UI updates
                    try:
                        object.__setattr__(message, '_frame_format', new_frame_format)
                    except Exception:
                        pass
                    
                    return True, ""
                else:
                    # Still try to update _frame_format for UI display
                    try:
                        object.__setattr__(message, '_frame_format', new_frame_format)
                        return True, ""
                    except Exception:
                        return False, "Cannot set frame format - attribute not found"
            else:
                # Still try to update _frame_format for UI display
                try:
                    object.__setattr__(message, '_frame_format', new_frame_format)
                    return True, ""
                except Exception:
                    return False, "Cannot set frame format - definitions not available"
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error updating frame_format: {str(e)}"

    def edit_message_cycle_time(self, message_name: str, new_cycle_time: int) -> tuple[bool, str]:
        """
        Edit the cycle time of a message (in milliseconds).
        Returns (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Validate cycle time
        if new_cycle_time is not None and new_cycle_time < 0:
            return False, "Cycle time cannot be negative"
            
        try:
            # Use object.__setattr__ for direct attribute setting
            try:
                object.__setattr__(message, 'cycle_time', new_cycle_time)
            except Exception:
                # If that fails, try setting a _cycle_time attribute
                object.__setattr__(message, '_cycle_time', new_cycle_time)
            
            # Make sure message.dbc exists and add the attribute there as well
            if hasattr(message, 'dbc') and message.dbc is not None:
                # Make sure message.dbc.attributes is initialized
                if not hasattr(message.dbc, 'attributes') or message.dbc.attributes is None:
                    message.dbc.attributes = {}
                    
                # Try to set attribute via Attribute class if definitions exist
                if hasattr(self.database, 'dbc') and hasattr(self.database.dbc, 'attribute_definitions'):
                    if 'GenMsgCycleTime' in self.database.dbc.attribute_definitions:
                        definition = self.database.dbc.attribute_definitions['GenMsgCycleTime']
                        try:
                            attr_sig = str(Attribute.__init__.__code__.co_varnames)
                            
                            # Try different ways to create the attribute
                            if 'value' in attr_sig and 'definition' in attr_sig:
                                message.dbc.attributes['GenMsgCycleTime'] = Attribute(
                                    value=new_cycle_time,
                                    definition=definition
                                )
                            elif len(attr_sig.split(',')) >= 3:  # At least self, arg1, arg2
                                message.dbc.attributes['GenMsgCycleTime'] = Attribute(definition, new_cycle_time)
                        except Exception:
                            # If we can't add to attributes, at least the direct property is set
                            pass
                    
            return True, ""
                
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False, f"Error updating cycle_time: {str(e)}"

    def edit_message_receivers(self, message_name: str, new_receivers: list) -> tuple[bool, str]:
        """
        Edit the receivers of all signals in a message.
        
        Since messages themselves don't directly have receivers but their signals do,
        this method updates all signals in the message to have the same receivers.
        
        Args:
            message_name (str): Name of the message to update
            new_receivers (list): List of receiver node names to set for all signals
            
        Returns:
            tuple[bool, str]: (Success status, Error message if any)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        message = None
        for msg in self.database.messages:
            if msg.name == message_name:
                message = msg
                break
                
        if not message:
            return False, f"Message '{message_name}' not found."
            
        # Validate that all receivers exist as nodes
        existing_nodes = {node.name: node for node in self.database.nodes}
        invalid_receivers = [r for r in new_receivers if r not in existing_nodes]
        if invalid_receivers:
            return False, f"Invalid receiver nodes: {', '.join(invalid_receivers)}"
            
        # Process all signals in the message
        success = True
        errors = []
        
        if not message.signals:
            return False, "Message has no signals to update receivers for."
            
        for signal in message.signals:
            try:
                # Use the same approach as in edit_signal_receivers
                try:
                    # Only update the _receivers attribute if present
                    signal._receivers = [str(name) for name in new_receivers]
                except Exception as e1:
                    # If we can't set _receivers, try setting receivers directly
                    try:
                        signal.receivers = [str(name) for name in new_receivers]
                    except Exception as e2:
                        success = False
                        errors.append(f"Error updating receivers for signal '{signal.name}': {str(e2)}")
            except Exception as e:
                success = False
                errors.append(f"Error updating receivers for signal '{signal.name}': {str(e)}")
        
        if success:
            return True, ""
        else:
            return False, "Errors occurred while updating receivers: " + "; ".join(errors)
            
    def edit_node_name(self, old_node_name: str, new_node_name: str) -> tuple[bool, str]:
        """
        Edit the name of a node in the database.
        
        Args:
            old_node_name (str): Current node name
            new_node_name (str): New node name
            
        Returns:
            tuple[bool, str]: (Success status, Error message if any)
        """
        if not self.database:
            return False, "Database not initialized"
            
        if not new_node_name or not new_node_name.strip():
            return False, "Node name cannot be empty."
            
        # Check if new name already exists
        if any(node.name == new_node_name for node in self.database.nodes):
            return False, f"A node with the name '{new_node_name}' already exists."
            
        # Find the node to edit
        node_to_edit = None
        for node in self.database.nodes:
            if node.name == old_node_name:
                node_to_edit = node
                break
                
        if not node_to_edit:
            return False, f"Node '{old_node_name}' not found."
            
        # Update the node name
        node_to_edit.name = new_node_name
        
        # Update references in message senders
        for message in self.database.messages:
            # Update senders list
            if hasattr(message, 'senders') and message.senders:
                if old_node_name in message.senders:
                    try:
                        # Replace the old node name with the new one
                        new_senders = [new_node_name if sender == old_node_name else sender 
                                     for sender in message.senders]
                        # Try to set the senders attribute directly
                        message.senders = new_senders
                    except (AttributeError, TypeError) as e:
                        # If that fails, try to set the _senders internal attribute
                        try:
                            message._senders = new_senders
                        except (AttributeError, TypeError):
                            # If both attempts fail, log but continue
                            pass
            
            # Update receivers in all signals of this message
            for signal in message.signals:
                if hasattr(signal, 'receivers') and signal.receivers:
                    if old_node_name in signal.receivers:
                        # Create the updated receivers list
                        new_receivers = [new_node_name if receiver == old_node_name else receiver 
                                        for receiver in signal.receivers]
                        
                        try:
                            # First try to update the _receivers attribute if it exists
                            if hasattr(signal, '_receivers'):
                                signal._receivers = new_receivers
                            else:
                                # Try to update the receivers attribute directly
                                signal.receivers = new_receivers
                        except (AttributeError, TypeError):
                            # If direct assignment fails, try a fallback approach
                            try:
                                # Use object.__setattr__ as a last resort
                                object.__setattr__(signal, '_receivers', new_receivers)
                            except Exception:
                                # If all approaches fail, log but continue
                                pass
                                
        return True, "" 