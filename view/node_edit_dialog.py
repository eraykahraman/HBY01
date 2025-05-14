from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
import re

class NodeEditDialog(QDialog):
    """Dialog for editing a node"""
    name_edited = pyqtSignal(str)  # Signal emitted when node name is edited
    
    def __init__(self, node_name, parent=None):
        super().__init__(parent)
        self.node_name = node_name
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
        """Validate the name and accept if valid"""
        new_name = self.name_edit.text().strip()
        is_valid, error_message = self.validate_name(new_name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Name", error_message)
            return
        if new_name == self.node_name:
            self.accept()  # Just close dialog if no changes made
            return
        self.name_edited.emit(new_name)
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