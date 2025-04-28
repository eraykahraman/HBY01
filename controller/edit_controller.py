from controller.dbc_io_handler import DBC_IO_Handler

class EditController:
    @staticmethod
    def edit_signal_name(handler: DBC_IO_Handler, message_name: str, old_signal_name: str, new_signal_name: str) -> tuple[bool, str]:
        """
        Edit the name of a signal in a given message.
        Returns (success, error_message)
        """
        if not new_signal_name or not new_signal_name.strip():
            return False, "Signal name cannot be empty."
        messages = handler.get_messages()
        for msg in messages:
            if msg['name'] == message_name:
                # Check for uniqueness
                if any(s['name'] == new_signal_name for s in msg['signals']):
                    return False, f"A signal with the name '{new_signal_name}' already exists in this message."
                # Find and update the signal
                for signal in msg['signals']:
                    if signal['name'] == old_signal_name:
                        signal['name'] = new_signal_name
                        # Also update in the global signals list
                        for s in handler.signals:
                            if s['name'] == old_signal_name and s['message_name'] == message_name:
                                s['name'] = new_signal_name
                        # Use the per-file EditHandler instance
                        if hasattr(handler, 'edit_handler') and handler.edit_handler:
                            handler.edit_handler.edit_signal_name_in_db(message_name, old_signal_name, new_signal_name)
                        handler.signals_changed.emit(handler.signals)
                        handler.messages_changed.emit(handler.messages)
                        return True, ""
                return False, f"Signal '{old_signal_name}' not found in message '{message_name}'."
        return False, f"Message '{message_name}' not found." 