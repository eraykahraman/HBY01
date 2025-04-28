from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QDialogButtonBox
from PyQt5.QtCore import pyqtSignal

class SignalEditDialog(QDialog):
    name_edited = pyqtSignal(str)

    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Signal Name")
        self.setMinimumWidth(350)
        self.current_name = current_name
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"Current Name: {self.current_name}"))
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(self.current_name)
        layout.addWidget(QLabel("New Name:"))
        layout.addWidget(self.name_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        new_name = self.name_edit.text().strip()
        self.name_edited.emit(new_name)
        super().accept() 