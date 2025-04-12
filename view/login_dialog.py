from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QDialogButtonBox, QComboBox, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from utils.auth_service import AuthService
from model.user_orm import UserRole
import logging

class LoginDialog(QDialog):
    """Dialog for user login"""
    
    login_successful = pyqtSignal(dict)  # Signal emitted when login is successful
    
    def __init__(self, auth_service=None, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.auth_service = auth_service or AuthService()
        
        self.setWindowTitle("Login")
        self.setMinimumWidth(300)
        self.setModal(True)
        
        self.initUI()
    
    def initUI(self):
        """Initialize the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Create form layout for login fields
        form_layout = QFormLayout()
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        form_layout.addRow("Username:", self.username_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        layout.addLayout(form_layout)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        layout.addWidget(self.remember_checkbox)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.attempt_login)
        self.login_button.setDefault(True)
        
        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.show_register_dialog)
        
        # Cancel button
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    def attempt_login(self):
        """Attempt to login with provided credentials"""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        # Validate inputs
        if not username:
            QMessageBox.warning(self, "Login Error", "Username is required")
            return
            
        if not password:
            QMessageBox.warning(self, "Login Error", "Password is required")
            return
        
        # Attempt login
        success, message = self.auth_service.login(username, password)
        
        if success:
            # Get current user info
            user_info = self.auth_service.get_current_user()
            
            # Emit signal with user info
            self.login_successful.emit(user_info)
            
            # Show success message
            QMessageBox.information(self, "Login Successful", f"Welcome, {username}!")
            
            # Close dialog
            self.accept()
        else:
            # Show error message
            QMessageBox.warning(self, "Login Error", message)
    
    def show_register_dialog(self):
        """Show the registration dialog"""
        self.hide()  # Hide login dialog
        dialog = RegisterDialog(self.auth_service, self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            # If registration was successful, show login dialog again
            self.show()
        else:
            # If registration was cancelled, show login dialog again
            self.show()

class RegisterDialog(QDialog):
    """Dialog for user registration"""
    
    def __init__(self, auth_service, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.auth_service = auth_service
        
        self.setWindowTitle("Register")
        self.setMinimumWidth(350)
        self.setModal(True)
        
        self.initUI()
    
    def initUI(self):
        """Initialize the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Create form layout for registration fields
        form_layout = QFormLayout()
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Choose a username")
        form_layout.addRow("Username:", self.username_input)
        
        # Email field
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        form_layout.addRow("Email:", self.email_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Choose a password")
        self.password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Password:", self.password_input)
        
        # Confirm password field
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirm password")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        form_layout.addRow("Confirm Password:", self.confirm_password_input)
        
        # Role selection (default to basic user)
        self.role_combo = QComboBox()
        self.role_combo.addItem("Basic User", UserRole.BASIC_USER.value)
        self.role_combo.addItem("Module Owner", UserRole.MODULE_OWNER.value)
        self.role_combo.addItem("Netcom Engineer", UserRole.NETCOM_ENGINEER.value)
        form_layout.addRow("Role:", self.role_combo)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        buttons.accepted.connect(self.register_user)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def register_user(self):
        """Register a new user with provided information"""
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        role = self.role_combo.currentData()
        
        # Validate inputs
        if not username:
            QMessageBox.warning(self, "Registration Error", "Username is required")
            return
            
        if not email:
            QMessageBox.warning(self, "Registration Error", "Email is required")
            return
            
        if not password:
            QMessageBox.warning(self, "Registration Error", "Password is required")
            return
            
        if password != confirm_password:
            QMessageBox.warning(self, "Registration Error", "Passwords do not match")
            return
        
        # Attempt registration
        success, message, user_id = self.auth_service.register_user(username, email, password, role)
        
        if success:
            # Show success message
            QMessageBox.information(
                self,
                "Registration Successful",
                "Your account has been created. You can now login."
            )
            
            # Close dialog
            self.accept()
        else:
            # Show error message
            QMessageBox.warning(self, "Registration Error", message) 