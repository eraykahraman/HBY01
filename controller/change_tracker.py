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
    
    def get_changes_summary(self) -> str:
        """Get a formatted summary of all changes"""
        if not self._changes:
            return ""
            
        summary = "Changes made in this session:\n\n"
        for change in self._changes:
            summary += f"[{change['timestamp']}] Message: {change['message']}, Signal: {change['signal']}\n"
            for detail in change['changes']:
                if detail == 'Signal deleted':
                    summary += f"  • Signal was deleted\n"
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