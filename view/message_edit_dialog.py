from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QMessageBox, QFormLayout, QCheckBox, QComboBox,
                            QListWidget, QListWidgetItem, QWidget)
from PyQt5.QtCore import pyqtSignal, Qt

class MessageEditDialog(QDialog):
    name_edited = pyqtSignal(str)
    frame_id_edited = pyqtSignal(int)
    extended_frame_edited = pyqtSignal(bool)
    message_deleted = pyqtSignal(str)  # message_name
    senders_edited = pyqtSignal(list)  # new_senders
    send_type_edited = pyqtSignal(str)  # new_send_type
    frame_format_edited = pyqtSignal(str)  # new_frame_format
    cycle_time_edited = pyqtSignal(int)  # new_cycle_time in ms

    def __init__(self, current_name, message_data, handler, parent=None):
        super().__init__(parent)
        self.current_name = current_name
        self.message_data = message_data
        self.handler = handler
        self.available_nodes = [node['name'] for node in handler.get_nodes()] if handler else []
        
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

        # Extended Frame
        self.extended_frame_checkbox = QCheckBox()
        self.extended_frame_checkbox.setChecked(self.message_data.get('is_extended_frame', False))
        self.extended_frame_checkbox.stateChanged.connect(self.on_extended_frame_changed)
        form_layout.addRow("Extended Frame:", self.extended_frame_checkbox)

        # Priority field (for extended frames)
        self.priority_combo = QComboBox()
        for p in self.priority_ranges:
            self.priority_combo.addItem(p["priority"])
        self.priority_combo.currentIndexChanged.connect(self.on_priority_changed)
        form_layout.addRow("Priority (Extended):", self.priority_combo)

        # Frame ID
        frame_id_layout = QHBoxLayout()
        
        # Priority part of frame ID (read-only)
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
        
        # Main part of frame ID (editable)
        self.frame_id_edit = QLineEdit()
        self.frame_id_edit.setStyleSheet("""
            QLineEdit {
                border-left: none;
                padding: 2px;
            }
        """)
        self.frame_id_edit.textChanged.connect(self.on_frame_id_changed)
        frame_id_layout.addWidget(self.frame_id_edit)
        
        # Add a label to show decimal value
        self.frame_id_decimal = QLabel()
        frame_id_layout.addWidget(self.frame_id_decimal)
        
        # Initialize frame ID fields
        current_frame_id = self.message_data.get('frame_id', 0)
        self.update_frame_id_display(current_frame_id)
        
        form_layout.addRow("Frame ID (hex):", frame_id_layout)

        # Senders
        senders_layout = QVBoxLayout()
        self.senders_list = QListWidget()
        self.senders_list.setSelectionMode(QListWidget.MultiSelection)
        self.senders_list.setMaximumHeight(100)
        
        # Add all available nodes
        for node in self.available_nodes:
            item = QListWidgetItem(node)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if node in self.message_data.get('senders', []) else Qt.Unchecked)
            self.senders_list.addItem(item)
            
        senders_layout.addWidget(self.senders_list)
        form_layout.addRow("Senders:", senders_layout)

        # Send Type
        self.send_type_combo = QComboBox()
        
        # Get send type choices from message data if available
        send_type_choices = self.message_data.get('send_type_choices')
        current_send_type = self.message_data.get('send_type')
        
        if send_type_choices:
            # Add items to combo box from defined choices
            if isinstance(send_type_choices, dict):
                # If it's a dictionary, add all values
                for value in send_type_choices.values():
                    self.send_type_combo.addItem(str(value))
            elif isinstance(send_type_choices, list):
                # If it's a list, add all items
                for value in send_type_choices:
                    self.send_type_combo.addItem(str(value))
        elif current_send_type:
            # If no choices but we have a current send type, just add the current one
            self.send_type_combo.addItem(str(current_send_type))
            
        # Set current value if it exists
        if current_send_type:
            index = self.send_type_combo.findText(current_send_type)
            if index >= 0:
                self.send_type_combo.setCurrentIndex(index)
            else:
                # If not in list, add it
                self.send_type_combo.addItem(current_send_type)
                self.send_type_combo.setCurrentText(current_send_type)
                
        form_layout.addRow("Send Type:", self.send_type_combo)

        # Frame Format
        self.frame_format_combo = QComboBox()
        
        # Get frame format choices from message data if available
        frame_format_choices = self.message_data.get('frame_format_choices')
        current_frame_format = self.message_data.get('frame_format')
        
        if frame_format_choices:
            # Add items to combo box from defined choices
            if isinstance(frame_format_choices, dict):
                # If it's a dictionary, add all values
                for value in frame_format_choices.values():
                    self.frame_format_combo.addItem(str(value))
            elif isinstance(frame_format_choices, list):
                # If it's a list, add all items
                for value in frame_format_choices:
                    self.frame_format_combo.addItem(str(value))
        elif current_frame_format:
            # If no choices but we have a current frame format, just add the current one
            self.frame_format_combo.addItem(str(current_frame_format))
            
        # Set current value if it exists
        if current_frame_format:
            index = self.frame_format_combo.findText(current_frame_format)
            if index >= 0:
                self.frame_format_combo.setCurrentIndex(index)
            else:
                # If not in list, add it
                self.frame_format_combo.addItem(current_frame_format)
                self.frame_format_combo.setCurrentText(current_frame_format)
                
        form_layout.addRow("Frame Format:", self.frame_format_combo)
        
        # Cycle Time - only show if it's defined in the DBC file
        current_cycle_time = self.message_data.get('cycle_time')
        if current_cycle_time is not None:
            # Create cycle time input field
            self.cycle_time_edit = QLineEdit()
            self.cycle_time_edit.setText(str(current_cycle_time))
            self.cycle_time_edit.setPlaceholderText("Enter cycle time (ms)")
            
            # Create layout for cycle time with unit label
            cycle_time_layout = QHBoxLayout()
            cycle_time_layout.addWidget(self.cycle_time_edit)
            
            # Add "ms" label
            ms_label = QLabel("ms")
            cycle_time_layout.addWidget(ms_label)
            
            form_layout.addRow("Cycle Time:", cycle_time_layout)
        else:
            # If cycle time is not defined in DBC, don't add the field
            self.cycle_time_edit = None

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
        
        # Initialize UI state
        self.on_extended_frame_changed()
        self.update_priority_from_frame_id(current_frame_id)

    def update_frame_id_display(self, frame_id):
        """Update the frame ID display fields"""
        if self.extended_frame_checkbox.isChecked():
            # For extended frame, split into priority and remaining bits
            priority_bits = (frame_id >> 26) & 0x7
            remaining_bits = frame_id & 0x03FFFFFF
            # Show full priority part (0x18 for priority 6)
            priority_hex = (frame_id >> 24) & 0x1F  # Get the full priority section
            self.frame_id_priority.setText(f"{priority_hex:02X}")
            self.frame_id_edit.setText(f"{remaining_bits:06x}")
        else:
            # For standard frame, show full ID
            self.frame_id_priority.setText("")
            self.frame_id_edit.setText(f"{frame_id:03x}")
        self.update_decimal_label(frame_id)

    def on_frame_id_changed(self):
        """Handle frame ID text changes"""
        try:
            text = self.frame_id_edit.text().lower().strip()
            if text.startswith("0x"):
                text = text[2:]
            
            # Parse the editable part
            if text:
                id_value = int(text, 16)
                if self.extended_frame_checkbox.isChecked():
                    # For extended frame, combine with priority
                    priority_text = self.frame_id_priority.text()
                    if priority_text:
                        priority_value = int(priority_text, 16) << 24
                        frame_id = priority_value | (id_value & 0x00FFFFFF)
                    else:
                        frame_id = id_value & 0x1FFFFFFF
                else:
                    frame_id = id_value & 0x7FF
                self.update_decimal_label(frame_id)
        except ValueError:
            self.frame_id_decimal.setText("(Invalid hex)")

    def on_priority_changed(self, index):
        """Handle priority selection change"""
        if not self.extended_frame_checkbox.isChecked():
            return
            
        try:
            # Get current ID value from editable part
            text = self.frame_id_edit.text().lower().strip()
            if text.startswith("0x"):
                text = text[2:]
            id_value = int(text, 16) if text else 0
            
            # Combine with new priority
            priority_range = self.priority_ranges[index]
            frame_id = (priority_range["range_start"] & 0x1F000000) | (id_value & 0x00FFFFFF)
            
            # Update display
            self.update_frame_id_display(frame_id)
        except ValueError:
            pass

    def on_extended_frame_changed(self):
        """Handle extended frame checkbox state change"""
        is_extended = self.extended_frame_checkbox.isChecked()
        self.priority_combo.setEnabled(is_extended)
        self.priority_combo.setVisible(is_extended)
        self.frame_id_priority.setVisible(is_extended)
        self.layout().itemAt(0).layout().labelForField(self.priority_combo).setVisible(is_extended)
        
        # Update frame ID display format
        try:
            text = self.frame_id_edit.text().lower().strip()
            if text.startswith("0x"):
                text = text[2:]
            frame_id = int(text, 16) if text else 0
            
            if is_extended:
                # When switching to extended, apply selected priority
                priority_range = self.priority_ranges[self.priority_combo.currentIndex()]
                frame_id = (priority_range["range_start"] & 0x1C000000) | (frame_id & 0x03FFFFFF)
            else:
                # When switching to standard, mask to 11 bits
                frame_id = frame_id & 0x7FF
            
            self.update_frame_id_display(frame_id)
        except ValueError:
            self.update_frame_id_display(0)

    def get_frame_id_value(self):
        """Get frame ID value from the edit fields"""
        try:
            if self.extended_frame_checkbox.isChecked():
                # For extended frame, combine priority and ID parts
                priority_range = self.priority_ranges[self.priority_combo.currentIndex()]
                id_text = self.frame_id_edit.text().lower().strip()
                if id_text.startswith("0x"):
                    id_text = id_text[2:]
                id_value = int(id_text, 16) if id_text else 0
                return (priority_range["range_start"] & 0x1C000000) | (id_value & 0x03FFFFFF)
            else:
                # For standard frame, just get the ID value
                text = self.frame_id_edit.text().lower().strip()
                if text.startswith("0x"):
                    text = text[2:]
                return int(text, 16) if text else 0
        except ValueError:
            return 0

    def update_decimal_label(self, frame_id):
        """Update the decimal value label"""
        self.frame_id_decimal.setText(f"(Dec: {frame_id})")

    def update_priority_from_frame_id(self, frame_id):
        """Update priority combo box based on frame ID"""
        if not self.extended_frame_checkbox.isChecked():
            return
            
        # Extract priority bits (28-26)
        priority_bits = (frame_id >> 26) & 0x7
        self.priority_combo.setCurrentIndex(priority_bits)

    def validate_and_accept(self):
        # Get values from UI
        new_name = self.new_name_edit.text()
        frame_id_text = self.frame_id_edit.text()
        is_extended = self.extended_frame_checkbox.isChecked()

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

        # Validate frame ID
        try:
            # Handle both "0x123" and "123" formats
            frame_id_text = frame_id_text.lower().strip()
            if frame_id_text.startswith("0x"):
                frame_id_text = frame_id_text[2:]
            id_value = int(frame_id_text, 16)
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Invalid frame ID format. Please enter a valid hexadecimal number.")
            return

        # First handle extended frame changes
        if is_extended != self.message_data.get('is_extended_frame', False):
            if is_extended:
                priority_range = self.priority_ranges[self.priority_combo.currentIndex()]
                full_frame_id = priority_range["range_start"] | id_value
                if full_frame_id > priority_range["range_end"]:
                    QMessageBox.warning(self, "Validation Error", 
                        f"Extended frame ID cannot exceed 0x{priority_range['range_end']:08X} (for this priority).\n"
                        f"Please enter a value between 0x0 and 0x{priority_range['range_end'] - priority_range['range_start']:06X}.")
                    return
                frame_id = full_frame_id
                self.frame_id_edit.setText(f"{id_value:06x}")
            else:
                if id_value > 0x7FF:  # 11-bit max
                    QMessageBox.warning(self, "Validation Error", 
                        "Cannot switch to standard frame: frame ID exceeds 11 bits (0x7FF).\n"
                        "Please reduce the frame ID or keep extended frame enabled.")
                    return
            self.extended_frame_edited.emit(is_extended)

        # Then validate frame ID based on current extended frame status
        if is_extended:
            priority_range = self.priority_ranges[self.priority_combo.currentIndex()]
            full_frame_id = priority_range["range_start"] | id_value
            if full_frame_id < priority_range["range_start"] or full_frame_id > priority_range["range_end"]:
                QMessageBox.warning(self, "Validation Error", 
                    f"Frame ID does not match selected priority.\n"
                    f"For priority {priority_range['priority']}, ID must be between "
                    f"0x{priority_range['range_start']:08X} and 0x{priority_range['range_end']:08X}")
                return
            frame_id = full_frame_id
        else:
            if id_value > 0x7FF:  # 11-bit max
                QMessageBox.warning(self, "Validation Error", 
                    "Standard frame ID cannot exceed 0x7FF (11 bits).\n"
                    "Please enter a value between 0x0 and 0x7FF or enable extended frame.")
                return
            frame_id = id_value

        # Get selected senders
        selected_senders = []
        for i in range(self.senders_list.count()):
            item = self.senders_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_senders.append(item.text())

        # Enforce sender selection rules
        if not selected_senders:
            QMessageBox.warning(self, "Validation Error", "Please select at least one sender.")
            return
        if len(selected_senders) > 1:
            QMessageBox.warning(self, "Validation Error", "Please select only one sender.")
            return

        # Get the selected send type
        new_send_type = self.send_type_combo.currentText()
        
        # Emit send_type_edited signal if changed
        if new_send_type != self.message_data.get('send_type', ""):
            self.send_type_edited.emit(new_send_type)

        # Get the selected frame format
        new_frame_format = self.frame_format_combo.currentText()
        
        # Emit frame_format_edited signal if changed
        if new_frame_format != self.message_data.get('frame_format', ""):
            self.frame_format_edited.emit(new_frame_format)

        # Get and validate cycle time only if the field exists
        if self.cycle_time_edit is not None:
            cycle_time_text = self.cycle_time_edit.text().strip()
            new_cycle_time = None
            if cycle_time_text:
                try:
                    new_cycle_time = int(cycle_time_text)
                    if new_cycle_time < 0:
                        QMessageBox.warning(self, "Validation Error", "Cycle time cannot be negative.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "Validation Error", "Invalid cycle time format. Please enter a valid integer value.")
                    return
                    
            # Emit cycle_time_edited signal if changed
            current_cycle_time = self.message_data.get('cycle_time')
            if new_cycle_time != current_cycle_time:
                self.cycle_time_edited.emit(new_cycle_time)

        # Emit senders signal if changed
        if set(selected_senders) != set(self.message_data.get('senders', [])):
            self.senders_edited.emit(selected_senders)

        # Emit remaining signals
        if new_name != self.current_name:
            self.name_edited.emit(new_name)

        if frame_id != self.message_data.get('frame_id', 0):
            self.frame_id_edited.emit(frame_id)

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