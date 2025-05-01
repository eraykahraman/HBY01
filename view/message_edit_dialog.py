from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QMessageBox, QFormLayout)
from PyQt5.QtCore import pyqtSignal, Qt

class MessageEditDialog(QDialog):
    name_edited = pyqtSignal(str)
    message_deleted = pyqtSignal(str)  # message_name

    def __init__(self, current_name, message_data, handler, parent=None):
        super().__init__(parent)
        self.current_name = current_name
        self.message_data = message_data
        self.handler = handler
        
        # Prevent dialog from accepting when Enter is pressed
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # Ensure no default button is set
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        
        # Disable default button behavior
        self.setWindowFlags(self.windowFlags() | Qt.MSWindowsFixedSizeDialogHint)
        
        self.setWindowTitle("Edit Message")
        self.setMinimumWidth(400)
        self.setup_ui()
        
        # Clear default focus
        self.setFocus()

    def setup_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Current name (display only)
        current_name_label = QLabel(self.current_name)
        form_layout.addRow("Current Name:", current_name_label)

        # New name
        self.new_name_edit = QLineEdit()
        self.new_name_edit.setText(self.current_name)
        form_layout.addRow("New Name:", self.new_name_edit)

        layout.addLayout(form_layout)

        # Buttons
        button_layout = QHBoxLayout()
        
        # Add delete button
        delete_button = QPushButton("Delete Message")
        delete_button.setAutoDefault(False)
        delete_button.setDefault(False)
        delete_button.setFocusPolicy(Qt.NoFocus)
        delete_button.setStyleSheet("background-color: #ff6b6b; color: white;")
        delete_button.clicked.connect(self.delete_message)
        button_layout.addWidget(delete_button)
        
        button_layout.addStretch()
        
        ok_button = QPushButton("OK")
        ok_button.setAutoDefault(False)
        ok_button.setDefault(False)
        ok_button.setFocusPolicy(Qt.NoFocus)
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.setAutoDefault(False)
        cancel_button.setDefault(False)
        cancel_button.setFocusPolicy(Qt.NoFocus)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def validate_and_accept(self):
        # Get values from UI
        new_name = self.new_name_edit.text()

        # Validate name
        if not new_name:
            QMessageBox.warning(self, "Validation Error", "Message name cannot be empty.")
            return

        # Check if name is valid DBC name
        is_valid, error_msg = self.is_valid_dbc_name(new_name)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        # Check for duplicate name
        if new_name != self.current_name:
            is_duplicate = self.is_name_duplicate(new_name)
            if is_duplicate:
                QMessageBox.warning(self, "Validation Error", 
                                  f"A message with the name '{new_name}' already exists.")
                return

        # Emit signal for changed name
        if new_name != self.current_name:
            self.name_edited.emit(new_name)

        self.accept()

    def is_valid_dbc_name(self, name: str) -> tuple[bool, str]:
        """Check if the name is a valid DBC name"""
        if not name:
            return False, "Name cannot be empty"
        if not name[0].isalpha():
            return False, "Name must start with a letter"
        if not all(c.isalnum() or c == '_' for c in name):
            return False, "Name can only contain letters, numbers, and underscores"
        return True, ""

    def is_name_duplicate(self, name: str) -> bool:
        """Check if the name already exists in the database"""
        if not self.handler:
            return False
            
        # Get all messages from the handler
        messages = self.handler.get_messages()
        
        # Check if any message (except the current one) has this name
        for message in messages:
            if message['name'] == name and message['name'] != self.current_name:
                return True
                
        return False

    def delete_message(self):
        """Handle message deletion"""
        reply = QMessageBox.question(
            self,
            "Delete Message",
            f"Are you sure you want to delete message '{self.current_name}'?\nThis action cannot be undone.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.message_deleted.emit(self.current_name)
            self.accept() 