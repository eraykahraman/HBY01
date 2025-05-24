from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox, QCheckBox, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class CreateMessageDialog(QDialog):
    message_created = pyqtSignal(str, int, bool, str)  # name, id, is_extended, frame_format

    def __init__(self, handler=None, parent=None, frame_format_choices=None):
        super().__init__(parent)
        self.handler = handler
        self.frame_format_choices = frame_format_choices
        self.setWindowTitle("Create Message")
        self.setMinimumWidth(350)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        # Priority ranges for extended frames
        self.priority_ranges = [
            {"priority": "000 (0x0)", "range_start": 0x00000000, "range_end": 0x03FFFFFF},
            {"priority": "001 (0x1)", "range_start": 0x04000000, "range_end": 0x07FFFFFF},
            {"priority": "010 (0x2)", "range_start": 0x08000000, "range_end": 0x0BFFFFFF},
            {"priority": "011 (0x3)", "range_start": 0x0C000000, "range_end": 0x0FFFFFFF},
            {"priority": "100 (0x4)", "range_start": 0x10000000, "range_end": 0x13FFFFFF},
            {"priority": "101 (0x5)", "range_start": 0x14000000, "range_end": 0x17FFFFFF},
            {"priority": "110 (0x6)", "range_start": 0x18000000, "range_end": 0x18FFFFFF},
            {"priority": "111 (0x7)", "range_start": 0x1C000000, "range_end": 0x1CFFFFFF},
        ]
        self.setup_ui()
        print("Frame format choices:", self.frame_format_choices)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter message name")
        self.name_edit.setFont(QFont("Arial", 10))
        form_layout.addRow("Message Name:", self.name_edit)

        # Extended Frame checkbox
        self.extended_frame_checkbox = QCheckBox()
        self.extended_frame_checkbox.stateChanged.connect(self.on_extended_frame_changed)
        form_layout.addRow("Extended Frame:", self.extended_frame_checkbox)

        # Priority dropdown (for extended frames)
        self.priority_combo = QComboBox()
        for p in self.priority_ranges:
            self.priority_combo.addItem(p["priority"])
        self.priority_combo.currentIndexChanged.connect(self.on_priority_changed)
        form_layout.addRow("Priority (Extended):", self.priority_combo)

        # Frame ID layout
        frame_id_layout = QHBoxLayout()
        self.frame_id_priority = QLineEdit()
        self.frame_id_priority.setFixedWidth(30)
        self.frame_id_priority.setReadOnly(True)
        self.frame_id_priority.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-right: none;
                padding: 2px;
            }
        """)
        frame_id_layout.addWidget(self.frame_id_priority)
        self.frame_id_edit = QLineEdit()
        self.frame_id_edit.setStyleSheet("""
            QLineEdit {
                border-left: none;
                padding: 2px;
            }
        """)
        self.frame_id_edit.textChanged.connect(self.on_frame_id_changed)
        frame_id_layout.addWidget(self.frame_id_edit)
        self.frame_id_decimal = QLabel()
        frame_id_layout.addWidget(self.frame_id_decimal)
        form_layout.addRow("Frame ID (hex):", frame_id_layout)

        # Frame Format
        self.frame_format_combo = QComboBox()
        if self.frame_format_choices:
            if isinstance(self.frame_format_choices, dict):
                for value in self.frame_format_choices.values():
                    self.frame_format_combo.addItem(str(value))
            elif isinstance(self.frame_format_choices, list):
                for value in self.frame_format_choices:
                    self.frame_format_combo.addItem(str(value))
        form_layout.addRow("Frame Format:", self.frame_format_combo)

        layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        self.create_button = QPushButton("Create")
        self.create_button.setFixedWidth(100)
        self.create_button.setDefault(True)
        self.create_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.create_button)
        layout.addLayout(button_layout)

    def on_extended_frame_changed(self):
        is_extended = self.extended_frame_checkbox.isChecked()
        self.priority_combo.setEnabled(is_extended)
        self.update_frame_id_display(self.get_frame_id_value())

    def on_priority_changed(self, index):
        self.update_frame_id_display(self.get_frame_id_value())

    def on_frame_id_changed(self):
        self.update_frame_id_display(self.get_frame_id_value())

    def get_frame_id_value(self):
        id_text = self.frame_id_edit.text().strip().lower()
        if id_text.startswith('0x'):
            id_text = id_text[2:]
        try:
            id_value = int(id_text, 16)
        except ValueError:
            id_value = 0
        return id_value

    def update_frame_id_display(self, frame_id):
        is_extended = self.extended_frame_checkbox.isChecked()
        if is_extended:
            priority_range = self.priority_ranges[self.priority_combo.currentIndex()]
            full_frame_id = priority_range["range_start"] | frame_id
            self.frame_id_priority.setText(f"{priority_range['priority'].split()[0]}")
            self.frame_id_edit.setText(f"{frame_id:06x}")
            self.frame_id_decimal.setText(f"(Dec: {full_frame_id})")
        else:
            self.frame_id_priority.setText("")
            self.frame_id_edit.setText(f"{frame_id:03x}")
            self.frame_id_decimal.setText(f"(Dec: {frame_id})")

    def validate_and_accept(self):
        name = self.name_edit.text().strip()
        is_valid, error_msg = self.validate_name(name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Name", error_msg)
            return
        # Duplicate name check
        if self.handler and hasattr(self.handler, 'get_messages'):
            existing_names = [msg['name'] for msg in self.handler.get_messages()]
            if name in existing_names:
                QMessageBox.warning(self, "Duplicate Name", f"A message with the name '{name}' already exists.")
                return
        # Frame ID validation
        id_text = self.frame_id_edit.text().strip().lower()
        if id_text.startswith('0x'):
            id_text = id_text[2:]
        try:
            id_value = int(id_text, 16)
        except ValueError:
            QMessageBox.warning(self, "Invalid ID", "Invalid frame ID format. Please enter a valid hexadecimal number.")
            return
        is_extended = self.extended_frame_checkbox.isChecked()
        if is_extended:
            priority_range = self.priority_ranges[self.priority_combo.currentIndex()]
            full_frame_id = priority_range["range_start"] | id_value
            if full_frame_id < priority_range["range_start"] or full_frame_id > priority_range["range_end"]:
                QMessageBox.warning(self, "Invalid ID", f"Frame ID does not match selected priority.\nFor priority {priority_range['priority']}, ID must be between 0x{priority_range['range_start']:08X} and 0x{priority_range['range_end']:08X}")
                return
            frame_id = full_frame_id
        else:
            if id_value > 0x7FF:
                QMessageBox.warning(self, "Invalid ID", "Standard frame ID cannot exceed 0x7FF (11 bits). Please enter a value between 0x0 and 0x7FF or enable extended frame.")
                return
            frame_id = id_value
        frame_format = self.frame_format_combo.currentText()
        self.message_created.emit(name, frame_id, is_extended, frame_format)
        self.accept()

    def validate_name(self, name: str) -> tuple[bool, str]:
        if not name:
            return False, "Name cannot be empty"
        if not name[0].isalpha():
            return False, "Name must start with a letter"
        if not all(c.isalnum() or c == '_' for c in name):
            return False, "Name can only contain letters, numbers, and underscores"
        return True, ""

    def reject(self):
        super().reject() 