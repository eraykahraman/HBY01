from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox, QComboBox)
from PyQt5.QtCore import Qt
from controller.user_controller import UserController
from database.models import UserRole

class UserAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Authentication")
        self.setModal(True)
        self.resize(350, 200)
        self.success = False
        self.username = None
        self.role = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        self.login_tab = QWidget()
        self.register_tab = QWidget()
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(self.register_tab, "Register")
        layout.addWidget(self.tabs)
        self._init_login_tab()
        self._init_register_tab()

    def _init_login_tab(self):
        form = QFormLayout()
        self.login_username = QLineEdit()
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.handle_login)
        form.addRow("Username:", self.login_username)
        form.addRow("Password:", self.login_password)
        form.addRow(self.login_btn)
        self.login_tab.setLayout(form)

    def _init_register_tab(self):
        form = QFormLayout()
        self.register_username = QLineEdit()
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        
        # Add role selection
        self.role_combo = QComboBox()
        self.role_combo.addItems([role.value for role in UserRole])
        self.role_combo.setCurrentText(UserRole.GENERIC_USER.value)
        
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        
        form.addRow("Username:", self.register_username)
        form.addRow("Password:", self.register_password)
        form.addRow("Role:", self.role_combo)
        form.addRow(self.register_btn)
        self.register_tab.setLayout(form)

    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        success, message, role = UserController.login(username, password)
        if success:
            self.success = True
            self.username = username
            self.role = role
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", message)

    def handle_register(self):
        username = self.register_username.text().strip()
        password = self.register_password.text()
        role = self.role_combo.currentText()
        success, message, role = UserController.register(username, password, role)
        if success:
            QMessageBox.information(self, "Registration Successful", message)
            self.tabs.setCurrentIndex(0)  # Switch to login tab
        else:
            QMessageBox.critical(self, "Registration Failed", message)

    def show_registration(self):
        """Show registration fields"""
        self.role_layout.setVisible(True)
        self.register_button.setVisible(True)
        self.login_button.setText("Cancel")
        self.login_button.clicked.disconnect()
        self.login_button.clicked.connect(self.reject)
        
    def show_login(self):
        """Show login fields"""
        self.role_layout.setVisible(False)
        self.register_button.setVisible(True)
        self.login_button.setText("Login")
        self.login_button.clicked.disconnect()
        self.login_button.clicked.connect(self.handle_login) 