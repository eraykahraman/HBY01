from PyQt5.QtWidgets import (QDialog, QTabWidget, QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QMessageBox)
from controller.user_controller import UserController

class UserAuthDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Authentication")
        self.setModal(True)
        self.resize(350, 200)
        self.success = False
        self.username = None
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
        self.register_btn = QPushButton("Register")
        self.register_btn.clicked.connect(self.handle_register)
        form.addRow("Username:", self.register_username)
        form.addRow("Password:", self.register_password)
        form.addRow(self.register_btn)
        self.register_tab.setLayout(form)

    def handle_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()
        success, message = UserController.login(username, password)
        if success:
            self.success = True
            self.username = username
            self.accept()
        else:
            QMessageBox.critical(self, "Login Failed", message)

    def handle_register(self):
        username = self.register_username.text().strip()
        password = self.register_password.text()
        success, message = UserController.register(username, password)
        if success:
            QMessageBox.information(self, "Registration Successful", message)
            self.tabs.setCurrentIndex(0)
        else:
            QMessageBox.critical(self, "Registration Failed", message) 