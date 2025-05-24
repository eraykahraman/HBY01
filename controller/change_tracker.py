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
        
    def add_signal_addition(self, message_name: str, signal_name: str):
        """
        Track the addition of a signal to a message
        
        Args:
            message_name (str): Name of the message the signal was added to
            signal_name (str): Name of the added signal
        """
        timestamp = self._get_timestamp()
        change_entry = {
            'timestamp': timestamp,
            'message': message_name,
            'signal': signal_name,
            'changes': ['Signal added']
        }
        self._changes.append(change_entry)
        
    def add_node_name_change(self, old_name: str, new_name: str):
        """
        Track the change of a node name
        
        Args:
            old_name (str): Previous node name
            new_name (str): New node name
        """
        timestamp = self._get_timestamp()
        change_entry = {
            'timestamp': timestamp,
            'changes': [f"Node name: {old_name} → {new_name}"],
            'type': 'node'  # Add type to distinguish from other changes
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
                summary += f"[{change['timestamp']}] Message: {change['message']}\n"
            elif change.get('type') == 'node':
                summary += f"[{change['timestamp']}] Node change\n"
            elif change.get('type') == 'node_comment':
                summary += f"[{change['timestamp']}] Node: {change['node']}\n"
            elif change.get('type') == 'node_address':
                summary += f"[{change['timestamp']}] Node: {change['node']}\n"
            elif change.get('type') == 'message_addition':
                summary += f"[{change['timestamp']}] Message: {change['message']} (Node: {change['node']})\n"
            else:
                # Handle signal changes
                if 'message' in change and 'signal' in change:
                    summary += f"[{change['timestamp']}] Message: {change['message']}, Signal: {change['signal']}\n"
                else:
                    # Fallback for any other type of change
                    summary += f"[{change['timestamp']}] Change\n"
                    
            for detail in change['changes']:
                summary += f"  • {detail}\n"
            summary += "\n"
        return summary
    
    def clear_changes(self):
        """Clear all tracked changes"""
        self._changes = []
        
    def has_changes(self) -> bool:
        """Check if there are any tracked changes"""
        return len(self._changes) > 0 

    def _get_timestamp(self) -> str:
        """Get a formatted timestamp for changes"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

    def add_node_comment_change(self, node_name: str, old_comment: str, new_comment: str):
        """
        Track the change of a node comment
        Args:
            node_name (str): Node name
            old_comment (str): Previous comment
            new_comment (str): New comment
        """
        timestamp = self._get_timestamp()
        change_entry = {
            'timestamp': timestamp,
            'node': node_name,
            'changes': [f"Node comment: '{old_comment}' → '{new_comment}'"],
            'type': 'node_comment'
        }
        self._changes.append(change_entry)

    def add_node_address_change(self, node_name: str, old_address: str, new_address: str):
        """
        Track the change of a node address
        Args:
            node_name (str): Node name
            old_address (str): Previous address
            new_address (str): New address
        """
        timestamp = self._get_timestamp()
        change_entry = {
            'timestamp': timestamp,
            'node': node_name,
            'changes': [f"Node address: {old_address} → {new_address}"],
            'type': 'node_address'
        }
        self._changes.append(change_entry)

    def add_message_addition(self, node_name: str, message_name: str, frame_id: int = None, sender_node: str = None):
        """
        Track the addition of a message to a node
        Args:
            node_name (str): Name of the node
            message_name (str): Name of the added message
            frame_id (int): Frame ID of the message
            sender_node (str): Name of the sender node
        """
        timestamp = self._get_timestamp()
        changes = ['Message added']
        if frame_id is not None:
            changes.append(f"Frame ID: 0x{frame_id:X}")
        if sender_node is not None:
            changes.append(f"Sender: {sender_node}")
            
        change_entry = {
            'timestamp': timestamp,
            'node': node_name,
            'message': message_name,
            'changes': changes,
            'type': 'message_addition'
        }
        self._changes.append(change_entry) 