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