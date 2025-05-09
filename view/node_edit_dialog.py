from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

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
        self.save_button.clicked.connect(self.validate_and_save)
        button_layout.addWidget(self.save_button)
        
        main_layout.addLayout(button_layout)
        
    def validate_and_save(self):
        """Validate inputs and save changes"""
        new_name = self.name_edit.text().strip()
        
        # Validate name
        if not new_name:
            QMessageBox.warning(self, "Validation Error", "Node name cannot be empty.")
            return
            
        # Check if name actually changed
        if new_name == self.node_name:
            self.accept()  # Just close dialog if no changes made
            return
            
        # Emit signal with new name
        self.name_edited.emit(new_name)
        self.accept() 