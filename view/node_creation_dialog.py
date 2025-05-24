from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QDialogButtonBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QValidator
import re

class HexValidator(QValidator):
    """Custom validator for hexadecimal input"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def validate(self, text, pos):
        """Validate the input text"""
        if not text.startswith("0x"):
            return (QValidator.Invalid, text, pos)
            
        # Allow empty input after 0x
        if text == "0x":
            return (QValidator.Acceptable, text, pos)
            
        # Check if the rest is valid hex
        hex_part = text[2:]
        if not hex_part:
            return (QValidator.Acceptable, text, pos)
            
        if re.match(r'^[0-9A-Fa-f]*$', hex_part):
            # Check if value is within range (0-255)
            try:
                value = int(hex_part, 16)
                if 0 <= value <= 255:
                    return (QValidator.Acceptable, text, pos)
            except ValueError:
                pass
                
        return (QValidator.Invalid, text, pos)

class HexLineEdit(QLineEdit):
    """Custom QLineEdit for hexadecimal input with fixed 0x prefix"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPlaceholderText("Enter node address (0x00-0xFF)")
        self.setText("0x")
        self.setValidator(HexValidator())
        self.textChanged.connect(self.on_text_changed)
        
    def on_text_changed(self, text):
        """Handle text changes to maintain 0x prefix"""
        if not text.startswith("0x"):
            # If 0x was deleted, add it back
            if text.startswith("x"):
                self.setText("0x" + text[1:])
            else:
                self.setText("0x" + text)
                
    def keyPressEvent(self, event):
        """Handle key press events to prevent deleting 0x prefix"""
        if event.key() == Qt.Key_Backspace:
            # If trying to delete 0x, ignore the event
            if self.cursorPosition() <= 2:
                return
        super().keyPressEvent(event)
        
    def get_value(self):
        """Get the hexadecimal value as an integer"""
        text = self.text().strip()
        if text == "0x":
            return None
        try:
            return int(text, 16)
        except ValueError:
            return None

class NodeCreationDialog(QDialog):
    def __init__(self, parent=None, existing_nodes=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Node")
        self.existing_nodes = existing_nodes or []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Create form layout for input fields
        form_layout = QFormLayout()
        
        # Node name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter node name")
        self.name_input.textChanged.connect(self.validate_name)
        form_layout.addRow("Node Name:", self.name_input)
        
        # Check if NmStationAddress is defined in the current DBC
        handler = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_handler'):
                handler = parent.current_handler
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        self.show_address = False
        if handler and hasattr(handler, 'database') and hasattr(handler.database, 'dbc') and hasattr(handler.database.dbc, 'attribute_definitions'):
            if 'NmStationAddress' in handler.database.dbc.attribute_definitions:
                self.show_address = True
        # Node address input (conditionally shown)
        if self.show_address:
            self.address_input = HexLineEdit()
            form_layout.addRow("Node Address:", self.address_input)
        else:
            self.address_input = None
        
        # Comment input
        self.comment_input = QLineEdit()
        self.comment_input.setPlaceholderText("Enter node comment (optional)")
        form_layout.addRow("Comment:", self.comment_input)
        
        # Add form layout to main layout
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def validate_name(self, name):
        """Validate the node name according to DBC naming rules"""
        # DBC name rules:
        # 1. Must start with a letter
        # 2. Can contain letters, numbers, and underscores
        # 3. No spaces or special characters
        if not name:
            return False
            
        # Check if name starts with a letter
        if not name[0].isalpha():
            return False
            
        # Check if name contains only valid characters
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            return False
            
        return True
        
    def validate_and_accept(self):
        """Validate input before accepting the dialog"""
        name = self.name_input.text().strip()
        
        # Check if name is empty
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Node name cannot be empty!")
            return
            
        # Validate name format
        if not self.validate_name(name):
            QMessageBox.warning(self, "Invalid Input", 
                "Node name must:\n"
                "- Start with a letter\n"
                "- Contain only letters, numbers, and underscores\n"
                "- No spaces or special characters")
            return
            
        # Check for duplicate names
        if any(node['name'] == name for node in self.existing_nodes):
            QMessageBox.warning(self, "Invalid Input", f"Node '{name}' already exists!")
            return
            
        self.accept()
        
    def get_node_data(self):
        """Get the entered node data, only include address if NmStationAddress is defined in the DBC."""
        # Find the handler from parent chain
        handler = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_handler'):
                handler = parent.current_handler
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        node_data = {
            'name': self.name_input.text().strip(),
            'comment': self.comment_input.text().strip()
        }
        # Only include address if NmStationAddress is defined and address_input exists
        if self.address_input is not None:
            node_data['address'] = self.address_input.get_value()
        return node_data 