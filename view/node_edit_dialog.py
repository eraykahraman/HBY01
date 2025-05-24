from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFormLayout, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import re

class NodeEditDialog(QDialog):
    """Dialog for editing a node"""
    name_edited = pyqtSignal(str)  # Signal emitted when node name is edited
    comment_edited = pyqtSignal(str)  # Signal emitted when node comment is edited
    address_edited = pyqtSignal(str)  # Signal emitted when node address is edited
    
    def __init__(self, node_name, node_comment=None, node_address=None, parent=None):
        super().__init__(parent)
        self.node_name = node_name
        self.node_comment = node_comment or ""
        self.node_address = node_address or ""
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Edit Node: {self.node_name}")
        self.setMinimumWidth(400)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Form layout for editing fields
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Node name edit field
        self.name_edit = QLineEdit(self.node_name)
        self.name_edit.setPlaceholderText("Enter node name")
        self.name_edit.setFont(QFont("Arial", 10))
        form_layout.addRow("Node Name:", self.name_edit)
        
        # Node address edit field
        self.address_edit = QLineEdit(self.node_address)
        self.address_edit.setPlaceholderText("Enter node address (e.g., 0xFE)")
        self.address_edit.setFont(QFont("Arial", 10))
        form_layout.addRow("Node Address:", self.address_edit)
        
        # Comment edit field
        self.comment_edit = QTextEdit(self.node_comment)
        self.comment_edit.setPlaceholderText("Enter node comment (optional)")
        self.comment_edit.setFont(QFont("Arial", 10))
        self.comment_edit.setFixedHeight(60)
        form_layout.addRow("Comment:", self.comment_edit)
        
        # Add validation rules label
        rules_label = QLabel(
            "Name rules:\n"
            "• Must start with a letter\n"
            "• Can contain letters, numbers, underscore, and dot\n"
            "• Cannot exceed 64 characters\n"
            "• Cannot be 'vector', 'multiplexer', or 'multiplexed'"
        )
        rules_label.setStyleSheet("color: gray; font-size: 9pt;")
        form_layout.addRow(rules_label)
        
        main_layout.addLayout(form_layout)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addStretch()
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setFixedWidth(100)
        self.save_button.setDefault(True)
        self.save_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
    def validate_and_accept(self):
        """Validate the inputs and accept if valid"""
        new_name = self.name_edit.text().strip()
        new_comment = self.comment_edit.toPlainText().strip()
        new_address = self.address_edit.text().strip()
        
        # Validate name
        is_valid, error_message = self.validate_name(new_name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Name", error_message)
            return
            
        # Validate address
        is_valid, error_message = self.validate_address(new_address)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Address", error_message)
            return
            
        # Check if any changes were made
        if (new_name == self.node_name and 
            new_comment == (self.node_comment or "") and 
            new_address == (self.node_address or "")):
            self.accept()  # Just close dialog if no changes made
            return
            
        # Emit signals for changes
        if new_name != self.node_name:
            self.name_edited.emit(new_name)
            
        if new_comment != (self.node_comment or ""):
            if len(new_comment) > 256:
                QMessageBox.warning(self, "Invalid Comment", "Comment cannot exceed 256 characters.")
                return
            self.comment_edited.emit(new_comment)
            
        if new_address != (self.node_address or ""):
            self.address_edited.emit(new_address)
            
        self.accept()

    def validate_name(self, name: str) -> tuple[bool, str]:
        """
        Validate the node name
        Args:
            name (str): The name to validate
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Node name cannot be empty."
        name = name.strip()
        if name[0].isdigit():
            return False, "Node name cannot start with a number."
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_.]*$', name):
            return False, "Node name can only contain letters, numbers, underscore, and dot. Must start with a letter."
        if len(name) > 64:
            return False, "Node name cannot exceed 64 characters."
        if name.lower() in ["vector", "multiplexer", "multiplexed"]:
            return False, "Node name cannot be 'vector', 'multiplexer', or 'multiplexed'."
        return True, ""
        
    def validate_address(self, address: str) -> tuple[bool, str]:
        """
        Validate the node address
        Args:
            address (str): The address to validate (in hex format, e.g. "0xFE")
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        if not address:  # Empty address is valid (means no address)
            return True, ""
            
        try:
            # Convert hex string to integer
            if address.startswith('0x'):
                value = int(address, 16)
            else:
                value = int(address)
                
            # Validate range (0-254 for J1939)
            if not 0 <= value <= 254:
                return False, "Node address must be between 0x00 and 0xFE"
                
            return True, ""
            
        except ValueError:
            return False, "Invalid address format. Must be a valid hex number (e.g., '0xFE')" 