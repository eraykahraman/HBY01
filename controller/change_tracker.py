from datetime import datetime

class ChangeTracker:
    def __init__(self):
        self._changes = []
        
    def add_signal_change(self, message_name: str, old_signal: dict, new_signal: dict):
        """Add a signal change to the tracker"""
        changes = []
        # Compare and track specific changes
        for key in new_signal:
            old_value = old_signal.get(key)
            new_value = new_signal.get(key)
            
            # Skip if both values are None or empty strings
            if (old_value is None or old_value == '') and (new_value is None or new_value == ''):
                continue
                
            # Skip if values are equal
            if old_value == new_value:
                continue
                
            # Format the values for display
            old_display = 'None' if old_value is None else str(old_value)
            new_display = 'None' if new_value is None else str(new_value)
            
            changes.append(f"{key}: {old_display} → {new_display}")
        
        if changes:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            change_entry = {
                'timestamp': timestamp,
                'message': message_name,
                'signal': new_signal['name'],
                'changes': changes
            }
            self._changes.append(change_entry)
            
    def add_signal_receivers_change(self, message_name: str, signal_updates: list):
        """
        Add changes to signal receivers in a message
        
        Args:
            message_name: Name of the message containing the signals
            signal_updates: List of dictionaries with signal_name, old_receivers, and new_receivers
        """
        if not signal_updates:
            return
            
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for update in signal_updates:
            signal_name = update['signal_name']
            old_receivers = update['old_receivers']
            new_receivers = update['new_receivers']
            
            # Format the changes
            old_display = 'None' if not old_receivers else str(old_receivers)
            new_display = 'None' if not new_receivers else str(new_receivers)
            
            change_entry = {
                'timestamp': timestamp,
                'message': message_name,
                'signal': signal_name,
                'changes': [f"receivers: {old_display} → {new_display}"]
            }
            self._changes.append(change_entry)
            
    def add_signal_deletion(self, message_name: str, signal_name: str):
        """Add a signal deletion to the tracker"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        change_entry = {
            'timestamp': timestamp,
            'message': message_name,
            'signal': signal_name,
            'changes': ['Signal deleted']
        }
        self._changes.append(change_entry)

    def add_message_change(self, old_message: dict, new_message: dict):
        """Add a message change to the tracker"""
        changes = []
        # Compare and track specific changes
        for key in new_message:
            old_value = old_message.get(key)
            new_value = new_message.get(key)
            
            # Skip if both values are None or empty strings
            if (old_value is None or old_value == '') and (new_value is None or new_value == ''):
                continue
                
            # Skip if values are equal
            if old_value == new_value:
                continue
                
            # Format the values for display
            old_display = 'None' if old_value is None else str(old_value)
            new_display = 'None' if new_value is None else str(new_value)
            
            changes.append(f"{key}: {old_display} → {new_display}")
        
        if changes:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            change_entry = {
                'timestamp': timestamp,
                'message': new_message['name'],
                'changes': changes,
                'type': 'message'  # Add type to distinguish from signal changes
            }
            self._changes.append(change_entry)

    def add_message_deletion(self, message_name: str):
        """Add a message deletion to the tracker"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        change_entry = {
            'timestamp': timestamp,
            'message': message_name,
            'changes': ['Message deleted'],
            'type': 'message'  # Add type to distinguish from signal changes
        }
        self._changes.append(change_entry)
    
    def get_changes_summary(self) -> str:
        """Get a formatted summary of all changes"""
        if not self._changes:
            return ""
            
        summary = "Changes made in this session:\n\n"
        for change in self._changes:
            if change.get('type') == 'message':
                # Message changes
                summary += f"[{change['timestamp']}] Message: {change['message']}\n"
            else:
                # Signal changes
                summary += f"[{change['timestamp']}] Message: {change['message']}, Signal: {change['signal']}\n"
            
            for detail in change['changes']:
                if detail in ['Signal deleted', 'Message deleted']:
                    summary += f"  • {detail}\n"
                else:
                    summary += f"  • {detail}\n"
            summary += "\n"
        
        return summary
    
    def clear_changes(self):
        """Clear all tracked changes"""
        self._changes = []
        
    def has_changes(self) -> bool:
        """Check if there are any tracked changes"""
        return len(self._changes) > 0 