from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QLabel, QMessageBox, QCheckBox, QComboBox, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator

class CreateMessageDialog(QDialog):
    message_created = pyqtSignal(str, int, bool, str, int, str, int, list, str)  # name, id, is_extended, frame_format, length, send_type, cycle_time, receivers, comment

    def __init__(self, handler=None, parent=None, frame_format_choices=None, send_type_choices=None, current_send_type=None, cycle_time=None):
        super().__init__(parent)
        self.handler = handler
        self.frame_format_choices = frame_format_choices
        self.send_type_choices = send_type_choices
        self.current_send_type = current_send_type
        self.cycle_time = cycle_time
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

        # Message Length field
        self.length_edit = QLineEdit()
        self.length_edit.setPlaceholderText("Enter message length in bytes (1-8)")
        self.length_edit.setFont(QFont("Arial", 10))
        self.length_edit.setValidator(QIntValidator(1, 8, self))
        form_layout.addRow("Message Length (bytes):", self.length_edit)

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

        # Send Type
        self.send_type_combo = QComboBox()
        # Populate send type combo box as in MessageEditDialog
        if self.send_type_choices:
            if isinstance(self.send_type_choices, dict):
                for value in self.send_type_choices.values():
                    self.send_type_combo.addItem(str(value))
            elif isinstance(self.send_type_choices, list):
                for value in self.send_type_choices:
                    self.send_type_combo.addItem(str(value))
        elif self.current_send_type:
            self.send_type_combo.addItem(str(self.current_send_type))
        # Set current value if it exists
        if self.current_send_type:
            index = self.send_type_combo.findText(self.current_send_type)
            if index >= 0:
                self.send_type_combo.setCurrentIndex(index)
            else:
                self.send_type_combo.addItem(self.current_send_type)
                self.send_type_combo.setCurrentText(self.current_send_type)
        form_layout.addRow("Send Type:", self.send_type_combo)

        # Cycle Time - only show if it's defined in the DBC file
        self.cycle_time_edit = None
        if self.cycle_time is not None:
            self.cycle_time_edit = QLineEdit()
            self.cycle_time_edit.setText(str(self.cycle_time))
            self.cycle_time_edit.setPlaceholderText("Enter cycle time (ms)")
            cycle_time_layout = QHBoxLayout()
            cycle_time_layout.addWidget(self.cycle_time_edit)
            ms_label = QLabel("ms")
            cycle_time_layout.addWidget(ms_label)
            form_layout.addRow("Cycle Time:", cycle_time_layout)

        # Comment field
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Enter comment (optional)")
        self.comment_edit.setFont(QFont("Arial", 10))
        form_layout.addRow("Comment:", self.comment_edit)

        # Receivers
        receivers_layout = QVBoxLayout()
        self.receivers_list = QListWidget()
        self.receivers_list.setSelectionMode(QListWidget.MultiSelection)
        self.receivers_list.setMaximumHeight(100)
        # Populate with all available nodes from handler
        available_nodes = [node['name'] for node in self.handler.get_nodes()] if self.handler and hasattr(self.handler, 'get_nodes') else []
        for node in available_nodes:
            item = QListWidgetItem(node)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.receivers_list.addItem(item)
        receivers_layout.addWidget(self.receivers_list)
        form_layout.addRow("Receivers:", receivers_layout)

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
        # Message Length validation
        length_text = self.length_edit.text().strip()
        try:
            length_value = int(length_text)
            if length_value < 1 or length_value > 8:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Invalid Length", "Message length must be an integer between 1 and 8.")
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
        send_type = self.send_type_combo.currentText()
        # Cycle time validation (if field is present)
        cycle_time_value = None
        if self.cycle_time_edit is not None:
            cycle_time_text = self.cycle_time_edit.text().strip()
            if cycle_time_text:
                try:
                    cycle_time_value = int(cycle_time_text)
                except ValueError:
                    cycle_time_value = None
        # If blank, use attribute definition default if available
        if cycle_time_value is None and self.handler and hasattr(self.handler, 'get_attribute_definitions'):
            attr_defs = self.handler.get_attribute_definitions() if callable(self.handler.get_attribute_definitions) else getattr(self.handler, 'attribute_definitions', None)
            if attr_defs and 'GenMsgCycleTime' in attr_defs:
                default = getattr(attr_defs['GenMsgCycleTime'], 'default_value', None)
                if default is not None:
                    try:
                        cycle_time_value = int(default)
                    except Exception:
                        cycle_time_value = 0
            else:
                cycle_time_value = 0
        elif cycle_time_value is None:
            cycle_time_value = 0
        # Collect selected receivers
        receivers = []
        if self.receivers_list is not None:
            for i in range(self.receivers_list.count()):
                item = self.receivers_list.item(i)
                if item.checkState() == 2:  # Qt.Checked
                    receivers.append(item.text())
        comment = self.comment_edit.text().strip()
        self.message_created.emit(name, frame_id, is_extended, frame_format, length_value, send_type, cycle_time_value, receivers, comment)
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

    def format_send_type_choices(self):
        if not self.send_type_choices:
            return "Not specified"
        if isinstance(self.send_type_choices, dict):
            return ", ".join([f"{k}: {v}" for k, v in self.send_type_choices.items()])
        elif isinstance(self.send_type_choices, list):
            return ", ".join([str(v) for v in self.send_type_choices])
        else:
            return str(self.send_type_choices) 