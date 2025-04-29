from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QDialogButtonBox, QSpinBox, QFormLayout)
from PyQt5.QtCore import pyqtSignal

class SignalEditDialog(QDialog):
    name_edited = pyqtSignal(str)
    length_edited = pyqtSignal(int)
    start_bit_edited = pyqtSignal(int)
    all_edited = pyqtSignal(str, int, int)  # name, length, start_bit

    def __init__(self, current_name, current_length=None, current_start_bit=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Signal")
        self.setMinimumWidth(350)
        self.current_name = current_name
        self.current_length = current_length
        self.current_start_bit = current_start_bit
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create form layout for better organization
        form_layout = QFormLayout()
        
        # Current name display
        current_name_label = QLabel(f"Current Name: {self.current_name}")
        layout.addWidget(current_name_label)
        
        # Name edit field
        self.name_edit = QLineEdit(self)
        self.name_edit.setText(self.current_name)
        form_layout.addRow("New Name:", self.name_edit)
        
        # Length edit field
        self.length_spin = QSpinBox(self)
        self.length_spin.setRange(1, 64)  # Typical range for CAN signal length
        if self.current_length is not None:
            self.length_spin.setValue(self.current_length)
        form_layout.addRow("Length (bits):", self.length_spin)
        
        # Start bit edit field
        self.start_bit_spin = QSpinBox(self)
        self.start_bit_spin.setRange(0, 63)  # Typical range for CAN signal start bit
        if self.current_start_bit is not None:
            self.start_bit_spin.setValue(self.current_start_bit)
        form_layout.addRow("Start Bit:", self.start_bit_spin)
        
        layout.addLayout(form_layout)
        
        # Add button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept(self):
        new_name = self.name_edit.text().strip()
        new_length = self.length_spin.value()
        new_start_bit = self.start_bit_spin.value()
        
        # Emit individual signals
        if new_name != self.current_name:
            self.name_edited.emit(new_name)
        if self.current_length is not None and new_length != self.current_length:
            self.length_edited.emit(new_length)
        if self.current_start_bit is not None and new_start_bit != self.current_start_bit:
            self.start_bit_edited.emit(new_start_bit)
            
        # Emit combined signal
        self.all_edited.emit(new_name, new_length, new_start_bit)
        
        super().accept() 