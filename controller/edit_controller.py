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