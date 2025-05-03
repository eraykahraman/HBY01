from typing import Optional, Dict, Any, List
import cantools
from cantools.database import Database
from copy import deepcopy
from cantools.database.can.attribute import Attribute

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
        Args:
            message_name: Name of the message containing the signal
            signal_name: Name of the signal to delete
            
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.database:
            return False, "Database not initialized"
            
        # Find the message
        for msg in self.database.messages:
            if msg.name == message_name:
                # Find and remove the signal
                for i, signal in enumerate(msg.signals):
                    if signal.name == signal_name:
                        # Remove the signal
                        del msg.signals[i]
                        return True, ""
                return False, f"Signal '{signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found."

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
            
        # Debug: Print initial state
        print(f"[DEBUG] Editing send_type for message '{message_name}'")
        print(f"[DEBUG] Current send_type: {getattr(message, 'send_type', None)}")
        print(f"[DEBUG] Has message.dbc: {hasattr(message, 'dbc')}")
        
        try:
            print(f"[DEBUG] Attempting to update to new send_type: {new_send_type}")
            
            # Make sure message.dbc exists
            if not hasattr(message, 'dbc') or message.dbc is None:
                print("[DEBUG] message.dbc doesn't exist, can't create it without DbcSpecifics class")
                print("[DEBUG] Trying to set _send_type attribute directly")
                try:
                    object.__setattr__(message, '_send_type', new_send_type)
                    print("[DEBUG] Direct _send_type setting succeeded")
                    return True, ""
                except Exception as e:
                    print(f"[DEBUG] Direct _send_type setting failed: {str(e)}")
                    return False, "Cannot set send type - dbc attribute not available"
            
            # Make sure message.dbc.attributes is initialized
            if not hasattr(message.dbc, 'attributes') or message.dbc.attributes is None:
                print("[DEBUG] Creating new attributes dictionary")
                message.dbc.attributes = {}
                
            # Check if the database has attribute definitions
            if hasattr(self.database, 'dbc') and hasattr(self.database.dbc, 'attribute_definitions'):
                # Get the attribute definition
                if 'GenMsgSendType' in self.database.dbc.attribute_definitions:
                    definition = self.database.dbc.attribute_definitions['GenMsgSendType']
                    print(f"[DEBUG] Found GenMsgSendType definition: {definition}")
                    print(f"[DEBUG] Definition type: {type(definition)}")
                    print(f"[DEBUG] Definition dir: {dir(definition)}")
                    
                    # Check if definition has _choices attribute
                    if hasattr(definition, '_choices') and definition._choices:
                        print(f"[DEBUG] Definition has _choices: {definition._choices}")
                        choices = definition._choices
                        
                        # Handle list of choices
                        if isinstance(choices, list):
                            print("[DEBUG] Choices is a list")
                            
                            # Try to find the new_send_type in the choices list
                            if new_send_type in choices:
                                # Find the index for this choice
                                choice_index = choices.index(new_send_type)
                                print(f"[DEBUG] Found '{new_send_type}' at index {choice_index}")
                                
                                # Try to create the attribute
                                try:
                                    print(f"[DEBUG] Setting GenMsgSendType attribute with index {choice_index}")
                                    attr_sig = str(Attribute.__init__.__code__.co_varnames)
                                    print(f"[DEBUG] Attribute constructor signature: {attr_sig}")
                                    
                                    # Try different ways to create the attribute
                                    if 'value' in attr_sig and 'definition' in attr_sig:
                                        print("[DEBUG] Using value and definition parameters")
                                        message.dbc.attributes['GenMsgSendType'] = Attribute(
                                            value=choice_index,
                                            definition=definition
                                        )
                                    elif len(attr_sig.split(',')) >= 3:  # At least self, arg1, arg2
                                        print("[DEBUG] Using positional parameters: definition, choice_index")
                                        message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_index)
                                    else:
                                        print("[DEBUG] Couldn't determine constructor parameters")
                                except Exception as e:
                                    print(f"[DEBUG] Error creating attribute: {str(e)}")
                            else:
                                # Try case-insensitive matching
                                matched = False
                                for i, value in enumerate(choices):
                                    if isinstance(value, str) and value.lower() == new_send_type.lower():
                                        choice_index = i
                                        print(f"[DEBUG] Found case-insensitive match '{value}' at index {choice_index}")
                                        try:
                                            message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_index)
                                            matched = True
                                            break
                                        except Exception as e:
                                            print(f"[DEBUG] Error setting attribute: {str(e)}")
                                
                                if not matched:
                                    print(f"[DEBUG] Value '{new_send_type}' not found in choices list")
                        
                        # Handle dictionary of choices
                        elif isinstance(choices, dict):
                            print("[DEBUG] Choices is a dictionary")
                            # Try to find the new_send_type in the choices values
                            if new_send_type in choices.values():
                                # Find the key for this choice value
                                for key, value in choices.items():
                                    if value == new_send_type:
                                        choice_key = key
                                        print(f"[DEBUG] Found '{new_send_type}' with key {choice_key}")
                                        break
                                
                                # Try to create the attribute
                                try:
                                    print(f"[DEBUG] Setting GenMsgSendType attribute with choice_key {choice_key}")
                                    message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_key)
                                except Exception as e:
                                    print(f"[DEBUG] Error creating attribute: {str(e)}")
                            else:
                                print(f"[DEBUG] Value '{new_send_type}' not found in choices dict")
                    
                    # Check if the definition has choices property
                    elif hasattr(definition, 'choices') and definition.choices:
                        print(f"[DEBUG] Definition has choices property: {definition.choices}")
                        choices = definition.choices
                        
                        # Handle based on type
                        if isinstance(choices, list):
                            if new_send_type in choices:
                                choice_index = choices.index(new_send_type)
                                try:
                                    message.dbc.attributes['GenMsgSendType'] = Attribute(definition, choice_index)
                                except Exception as e:
                                    print(f"[DEBUG] Error setting attribute: {str(e)}")
                        elif isinstance(choices, dict):
                            if new_send_type in choices.values():
                                for key, value in choices.items():
                                    if value == new_send_type:
                                        try:
                                            message.dbc.attributes['GenMsgSendType'] = Attribute(definition, key)
                                            break
                                        except Exception as e:
                                            print(f"[DEBUG] Error setting attribute: {str(e)}")
                    
                    # Fall back to direct approach if no choices found
                    else:
                        print("[DEBUG] Definition doesn't have usable choices")
                    
                    # Update _send_type for UI updates
                    try:
                        print("[DEBUG] Setting _send_type attribute directly")
                        object.__setattr__(message, '_send_type', new_send_type)
                        print("[DEBUG] Direct _send_type setting succeeded")
                    except Exception as e:
                        print(f"[DEBUG] Direct _send_type setting failed: {str(e)}")
                    
                    # Print final state
                    print(f"[DEBUG] After update - send_type: {getattr(message, 'send_type', None)}")
                    print(f"[DEBUG] message.dbc.attributes contains GenMsgSendType: {'GenMsgSendType' in message.dbc.attributes}")
                    if 'GenMsgSendType' in message.dbc.attributes:
                        print(f"[DEBUG] GenMsgSendType attribute: {message.dbc.attributes['GenMsgSendType']}")
                    
                    return True, ""
                else:
                    print("[DEBUG] No GenMsgSendType definition found in the database")
                    
                    # Still try to update _send_type for UI display
                    try:
                        object.__setattr__(message, '_send_type', new_send_type)
                        print("[DEBUG] Direct _send_type setting succeeded")
                        return True, ""
                    except Exception as e:
                        print(f"[DEBUG] Direct _send_type setting failed: {str(e)}")
                        return False, "Cannot set send type - attribute not found"
            else:
                print("[DEBUG] Database does not have attribute definitions")
                
                # Still try to update _send_type for UI display
                try:
                    object.__setattr__(message, '_send_type', new_send_type)
                    print("[DEBUG] Direct _send_type setting succeeded")
                    return True, ""
                except Exception as e:
                    print(f"[DEBUG] Direct _send_type setting failed: {str(e)}")
                    return False, "Cannot set send type - definitions not available"
                
        except Exception as e:
            print(f"[DEBUG] Exception while updating send_type: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Error updating send_type: {str(e)}" 