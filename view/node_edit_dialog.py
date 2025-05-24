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
    node_deleted = pyqtSignal(str)  # Signal emitted when node is deleted
    
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
        # Always show '0x' prefix and only allow editing after it
        initial_address = self.node_address
        if initial_address and not initial_address.startswith('0x'):
            initial_address = f"0x{initial_address}"
        elif not initial_address:
            initial_address = '0x'
        self.address_edit = QLineEdit(initial_address)
        self.address_edit.setPlaceholderText("Enter node address (e.g., 0xFE)")
        self.address_edit.setFont(QFont("Arial", 10))
        # --- Begin: Enable/disable address field based on NmStationAddress definition ---
        handler = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_handler'):
                handler = parent.current_handler
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        address_editable = False
        if handler and hasattr(handler, 'database') and handler.database:
            db = handler.database
            if hasattr(db, 'dbc') and hasattr(db.dbc, 'attribute_definitions'):
                address_editable = 'NmStationAddress' in db.dbc.attribute_definitions
        self.address_edit.setEnabled(address_editable)
        # --- End: Enable/disable address field ---
        form_layout.addRow("Node Address:", self.address_edit)
        
        # --- Begin: Enforce 0x prefix logic ---
        self.address_edit.textChanged.connect(self._enforce_0x_prefix)
        self.address_edit.cursorPositionChanged.connect(self._enforce_cursor_after_prefix)
        # --- End: Enforce 0x prefix logic ---
        
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
        
        # Delete Node button
        self.delete_button = QPushButton("Delete Node")
        self.delete_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_button.clicked.connect(self.confirm_delete_node)
        button_layout.addWidget(self.delete_button)
        
        main_layout.addLayout(button_layout)
        
    def _enforce_0x_prefix(self, text):
        # Always keep '0x' at the start
        if not text.startswith('0x'):
            # Remove any leading '0X' or other prefix, then add '0x'
            hex_part = text[2:] if text.lower().startswith('0x') else text.lstrip('xX')
            self.address_edit.blockSignals(True)
            self.address_edit.setText('0x' + hex_part)
            self.address_edit.blockSignals(False)
        elif text == '0x':
            # Allow empty after prefix
            pass
        # Optionally, you can restrict to valid hex digits after '0x' here

    def _enforce_cursor_after_prefix(self, old_pos, new_pos):
        # Prevent cursor from moving before or into the '0x' prefix
        if new_pos < 2:
            self.address_edit.setCursorPosition(2)

    def validate_and_accept(self):
        """Validate the inputs and accept if valid"""
        new_name = self.name_edit.text().strip()
        new_comment = self.comment_edit.toPlainText().strip()
        new_address = self.address_edit.text().strip()
        # Always ensure address starts with '0x'
        if new_address and not new_address.startswith('0x'):
            new_address = '0x' + new_address.lstrip('xX')
        
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

    def confirm_delete_node(self):
        reply = QMessageBox.question(
            self,
            "Delete Node",
            "Are you sure you want to delete this node?\n"
            "All messages sent by this node and their signals will also be deleted.\n"
            "This action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.delete_node()

    def delete_node(self):
        handler = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_handler'):
                handler = parent.current_handler
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        if not handler or not hasattr(handler, 'edit_controller') or not handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for deleting node.")
            return
        success, error = handler.edit_controller.delete_node(self.node_name)
        if not success:
            QMessageBox.critical(self, "Delete Error", error)
            return
        QMessageBox.information(self, "Node Deleted", f"Node '{self.node_name}' and all its messages/signals have been deleted.")
        self.node_deleted.emit(self.node_name)
        self.accept() 