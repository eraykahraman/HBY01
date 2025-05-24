from typing import TYPE_CHECKING, Optional, Dict, Any, List
from controller.edit_handler import EditHandler

if TYPE_CHECKING:
    from controller.dbc_io_handler import DBC_IO_Handler

class EditController:
    def __init__(self, handler: 'DBC_IO_Handler'):
        self.handler = handler
        self.edit_handler = None
        self._create_edit_handler()
        
    def _create_edit_handler(self):
        """Create EditHandler instance for the current database"""
        if self.handler.database:
            self.edit_handler = EditHandler(self.handler.database)
            
    def edit_signal_name(self, message_name: str, old_signal_name: str, new_signal_name: str) -> tuple[bool, str]:
        """
        Edit the name of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_name(message_name, old_signal_name, new_signal_name)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_length(self, message_name: str, signal_name: str, new_length: int) -> tuple[bool, str]:
        """
        Edit the length of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_length(message_name, signal_name, new_length)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_start_bit(self, message_name: str, signal_name: str, new_start_bit: int) -> tuple[bool, str]:
        """
        Edit the start bit of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_start_bit(message_name, signal_name, new_start_bit)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_byte_order(self, message_name: str, signal_name: str, new_byte_order: str) -> tuple[bool, str]:
        """
        Edit the byte order of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_byte_order(message_name, signal_name, new_byte_order)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_is_signed(self, message_name: str, signal_name: str, is_signed: bool) -> tuple[bool, str]:
        """
        Edit whether a signal is signed in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_is_signed(message_name, signal_name, is_signed)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_scale(self, message_name: str, signal_name: str, new_scale: float) -> tuple[bool, str]:
        """
        Edit the scale factor of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_scale(message_name, signal_name, new_scale)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_offset(self, message_name: str, signal_name: str, new_offset: float) -> tuple[bool, str]:
        """
        Edit the offset of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_offset(message_name, signal_name, new_offset)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_minimum(self, message_name: str, signal_name: str, new_minimum: Optional[float]) -> tuple[bool, str]:
        """
        Edit the minimum value of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_minimum(message_name, signal_name, new_minimum)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_maximum(self, message_name: str, signal_name: str, new_maximum: Optional[float]) -> tuple[bool, str]:
        """
        Edit the maximum value of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_maximum(message_name, signal_name, new_maximum)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_unit(self, message_name: str, signal_name: str, new_unit: str) -> tuple[bool, str]:
        """
        Edit the unit of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_unit(message_name, signal_name, new_unit)
        
        if success:
            self.handler.update_database()
            
        return success, error

    def edit_signal_comment(self, message_name: str, signal_name: str, new_comment: str) -> tuple[bool, str]:
        """
        Edit the comment of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_comment(message_name, signal_name, new_comment)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_receivers(self, message_name: str, signal_name: str, new_receivers: list) -> tuple[bool, str]:
        """
        Edit the receivers of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_receivers(message_name, signal_name, new_receivers)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_is_multiplexer(self, message_name: str, signal_name: str, is_multiplexer: bool) -> tuple[bool, str]:
        """
        Edit whether a signal is a multiplexer in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_is_multiplexer(message_name, signal_name, is_multiplexer)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_multiplexer_id(self, message_name: str, signal_name: str, multiplexer_id: Optional[int]) -> tuple[bool, str]:
        """
        Edit the multiplexer ID of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_multiplexer_id(message_name, signal_name, multiplexer_id)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_signal_choices(self, message_name: str, signal_name: str, choices: Dict[int, str]) -> tuple[bool, str]:
        """
        Edit the value table (choices) of a signal in a given message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_signal_choices(message_name, signal_name, choices)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def delete_signal(self, message_name: str, signal_name: str) -> tuple[bool, str]:
        """
        Delete a signal from a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.delete_signal(message_name, signal_name)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_name(self, old_message_name: str, new_message_name: str) -> tuple[bool, str]:
        """
        Edit the name of a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_name(old_message_name, new_message_name)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def delete_message(self, message_name: str) -> tuple[bool, str]:
        """
        Delete a message from the database.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.delete_message(message_name)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_frame_id(self, message_name: str, new_frame_id: int) -> tuple[bool, str]:
        """
        Edit the frame ID of a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_frame_id(message_name, new_frame_id)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_is_extended_frame(self, message_name: str, is_extended: bool) -> tuple[bool, str]:
        """
        Edit whether a message uses extended frame format.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_is_extended_frame(message_name, is_extended)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_senders(self, message_name: str, new_senders: list) -> tuple[bool, str]:
        """
        Edit the senders of a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_senders(message_name, new_senders)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_send_type(self, message_name: str, new_send_type: str) -> tuple[bool, str]:
        """
        Edit the send type of a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_send_type(message_name, new_send_type)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_frame_format(self, message_name: str, new_frame_format: str) -> tuple[bool, str]:
        """
        Edit the frame format of a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_frame_format(message_name, new_frame_format)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error
        
    def edit_message_cycle_time(self, message_name: str, new_cycle_time: int) -> tuple[bool, str]:
        """
        Edit the cycle time of a message.
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_cycle_time(message_name, new_cycle_time)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error

    def edit_message_receivers(self, message_name: str, new_receivers: list) -> tuple[bool, str]:
        """
        Edit the receivers of a message
        Returns (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_message_receivers(message_name, new_receivers)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
        return success, error
        
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
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.add_signal(message_name, signal_data)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
            # Track the addition in the change tracker if available
            if hasattr(self.handler, 'change_tracker'):
                self.handler.change_tracker.add_signal_addition(message_name, signal_data['name'])
            
        return success, error
        
    def edit_node_name(self, old_node_name: str, new_node_name: str) -> tuple[bool, str]:
        """
        Edit the name of a node.
        
        Args:
            old_node_name (str): The current name of the node
            new_node_name (str): The new name to assign to the node
            
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
            
        # Delegate to EditHandler
        success, error = self.edit_handler.edit_node_name(old_node_name, new_node_name)
        
        if success:
            # Update the database in DBC_IO_Handler
            self.handler.update_database()
            
            # Track the change in the change tracker if available
            if hasattr(self.handler, 'change_tracker'):
                self.handler.change_tracker.add_node_name_change(old_node_name, new_node_name)
            
        return success, error

    def edit_node_comment(self, node_name: str, new_comment: str) -> tuple[bool, str]:
        """
        Edit the comment of a node.
        Args:
            node_name (str): The name of the node
            new_comment (str): The new comment to assign
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
        # Get old comment for change tracking
        old_comment = None
        for node in self.handler.database.nodes:
            if hasattr(node, 'name') and node.name == node_name:
                old_comment = getattr(node, 'comment', '')
                break
        success, error = self.edit_handler.edit_node_comment(node_name, new_comment)
        if success:
            self.handler.update_database()
            if hasattr(self.handler, 'change_tracker'):
                self.handler.change_tracker.add_node_comment_change(node_name, old_comment, new_comment)
        return success, error

    def edit_node_address(self, node_name: str, new_address: str) -> tuple[bool, str]:
        """
        Edit the address of a node.
        Args:
            node_name (str): The name of the node
            new_address (str): The new address to assign (in hex format, e.g. "0xFE")
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"

        # Get old address for change tracking
        old_address = None
        for node in self.handler.database.nodes:
            if hasattr(node, 'name') and node.name == node_name:
                if hasattr(node, 'dbc') and hasattr(node.dbc, 'attributes'):
                    if 'NmStationAddress' in node.dbc.attributes:
                        old_address = node.dbc.attributes['NmStationAddress'].value
                break

        success, error = self.edit_handler.edit_node_address(node_name, new_address)
        if success:
            self.handler.update_database()
            if hasattr(self.handler, 'change_tracker'):
                self.handler.change_tracker.add_node_address_change(node_name, old_address, new_address)
        return success, error

    def add_message(self, node_name: str, message_data: dict) -> tuple[bool, str]:
        """
        Add a new message to the database for the given node.
        Args:
            node_name (str): Name of the node to add the message to
            message_data (dict): Dictionary containing the message data
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.edit_handler:
            return False, "Edit handler not initialized"
        success, error = self.edit_handler.add_message(node_name, message_data)
        if success:
            self.handler.update_database()
            if hasattr(self.handler, 'change_tracker'):
                self.handler.change_tracker.add_message_addition(node_name, message_data['name'])
        return success, error 