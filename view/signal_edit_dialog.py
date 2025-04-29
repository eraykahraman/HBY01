from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QDialogButtonBox, QSpinBox, QFormLayout, QMessageBox,
                            QComboBox, QCheckBox, QDoubleSpinBox, QTextEdit, QListWidget,
                            QListWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt

class SignalEditDialog(QDialog):
    name_edited = pyqtSignal(str)
    length_edited = pyqtSignal(int)
    start_bit_edited = pyqtSignal(int)
    byte_order_edited = pyqtSignal(str)
    is_signed_edited = pyqtSignal(bool)
    scale_edited = pyqtSignal(float)
    offset_edited = pyqtSignal(float)
    minimum_edited = pyqtSignal(float)
    maximum_edited = pyqtSignal(float)
    unit_edited = pyqtSignal(str)
    comment_edited = pyqtSignal(str)
    receivers_edited = pyqtSignal(list)  # New signal for receivers

    def __init__(self, current_name, current_length, current_start_bit, signal_data, handler, parent=None):
        super().__init__(parent)
        self.current_name = current_name
        self.current_length = current_length
        self.current_start_bit = current_start_bit
        self.signal_data = signal_data
        self.handler = handler
        
        self.setWindowTitle("Edit Signal")
        self.setMinimumWidth(500)  # Increased width to accommodate receivers list
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Create a horizontal layout for the main form and receivers list
        main_layout = QHBoxLayout()
        form_layout = QFormLayout()

        # Current name (display only)
        current_name_label = QLabel(self.current_name)
        form_layout.addRow("Current Name:", current_name_label)

        # New name
        self.new_name_edit = QLineEdit()
        self.new_name_edit.setText(self.current_name)
        form_layout.addRow("New Name:", self.new_name_edit)

        # Length
        self.length_spin = QSpinBox()
        self.length_spin.setRange(1, 64)
        self.length_spin.setValue(self.current_length)
        form_layout.addRow("Length (bits):", self.length_spin)

        # Start bit
        self.start_bit_spin = QSpinBox()
        self.start_bit_spin.setRange(0, 63)
        self.start_bit_spin.setValue(self.current_start_bit)
        form_layout.addRow("Start Bit:", self.start_bit_spin)

        # Byte order
        self.byte_order_combo = QComboBox()
        self.byte_order_combo.addItems(['little_endian', 'big_endian'])
        current_byte_order = self.signal_data.get('byte_order', 'little_endian')
        self.byte_order_combo.setCurrentText(current_byte_order)
        form_layout.addRow("Byte Order:", self.byte_order_combo)

        # Is signed
        self.is_signed_check = QCheckBox()
        self.is_signed_check.setChecked(self.signal_data.get('is_signed', False))
        form_layout.addRow("Is Signed:", self.is_signed_check)

        # Scale
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(-1e9, 1e9)
        self.scale_spin.setDecimals(6)
        self.scale_spin.setValue(float(self.signal_data.get('scale', 1.0)))
        form_layout.addRow("Scale:", self.scale_spin)

        # Offset
        self.offset_spin = QDoubleSpinBox()
        self.offset_spin.setRange(-1e9, 1e9)
        self.offset_spin.setDecimals(6)
        self.offset_spin.setValue(float(self.signal_data.get('offset', 0.0)))
        form_layout.addRow("Offset:", self.offset_spin)

        # Minimum
        self.minimum_spin = QDoubleSpinBox()
        self.minimum_spin.setRange(-1e9, 1e9)
        self.minimum_spin.setDecimals(6)
        if 'minimum' in self.signal_data:
            self.minimum_spin.setValue(float(self.signal_data['minimum']))
        form_layout.addRow("Minimum:", self.minimum_spin)

        # Maximum
        self.maximum_spin = QDoubleSpinBox()
        self.maximum_spin.setRange(-1e9, 1e9)
        self.maximum_spin.setDecimals(6)
        if 'maximum' in self.signal_data:
            self.maximum_spin.setValue(float(self.signal_data['maximum']))
        form_layout.addRow("Maximum:", self.maximum_spin)

        # Unit
        self.unit_edit = QLineEdit()
        self.unit_edit.setText(self.signal_data.get('unit', ''))
        form_layout.addRow("Unit:", self.unit_edit)

        # Comment (new)
        self.comment_edit = QTextEdit()
        self.comment_edit.setPlaceholderText("Enter signal comment...")
        self.comment_edit.setText(self.signal_data.get('comment', ''))
        self.comment_edit.setMaximumHeight(100)  # Limit height to 3-4 lines
        form_layout.addRow("Comment:", self.comment_edit)

        # Receivers list
        receivers_layout = QVBoxLayout()
        receivers_label = QLabel("Receivers:")
        receivers_layout.addWidget(receivers_label)
        
        self.receivers_list = QListWidget()
        self.receivers_list.setSelectionMode(QListWidget.MultiSelection)
        
        # Get all available nodes from handler
        all_nodes = [node['name'] for node in self.handler.get_nodes()]
        current_receivers = self.signal_data.get('receivers', [])
        
        # Add nodes to list widget
        for node in all_nodes:
            item = QListWidgetItem(node)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if node in current_receivers else Qt.Unchecked)
            self.receivers_list.addItem(item)
            
        receivers_layout.addWidget(self.receivers_list)
        
        # Add form layout and receivers layout to main layout
        main_layout.addLayout(form_layout)
        main_layout.addLayout(receivers_layout)
        
        layout.addLayout(main_layout)

        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.validate_and_accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_selected_receivers(self):
        """Get list of selected receivers from the list widget"""
        selected_receivers = []
        for i in range(self.receivers_list.count()):
            item = self.receivers_list.item(i)
            if item.checkState() == Qt.Checked:
                selected_receivers.append(item.text())
        return selected_receivers

    def is_name_duplicate(self, new_name):
        """Check if the signal name already exists in any message in the DBC file"""
        if not self.signal_data or not self.handler:
            return False, None
            
        # Get all signals from the DBC file
        all_signals = self.handler.get_signals()
        
        # Check for duplicates across all signals except the current one
        for signal in all_signals:
            if signal['name'] == new_name and new_name != self.current_name:
                return True, signal['message_name']  # Return True and the message name where duplicate exists
                
        return False, None

    def is_valid_dbc_name(self, name):
        """
        Validate if the signal name follows DBC syntax rules
        Returns: (bool, str) - (is_valid, error_message)
        """
        if not name:
            return False, "Signal name cannot be empty."
            
        # Check if name starts with a number
        if name[0].isdigit():
            return False, "Signal name cannot start with a number."
            
        # Check for valid characters (letters, numbers, and underscores only)
        import re
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            return False, "Signal name can only contain letters, numbers, and underscores, and must start with a letter."
            
        return True, ""

    def check_signal_overlap(self, start_bit, length):
        """
        Check if the signal position overlaps with other signals in the same message
        Returns: (bool, str) - (has_overlap, error_message)
        """
        if not self.signal_data or not self.handler:
            return False, ""

        # Get the current message
        current_message = None
        for message in self.handler.get_messages():
            if message['name'] == self.signal_data['message_name']:
                current_message = message
                break

        if not current_message:
            return False, ""

        # Calculate the bits that would be occupied by this signal
        new_signal_bits = set(range(start_bit, start_bit + length))

        # Check overlap with other signals in the same message
        for signal in current_message['signals']:
            # Skip the current signal being edited
            if signal['name'] == self.current_name:
                continue

            # Calculate bits occupied by other signal
            other_signal_bits = set(range(signal['start'], signal['start'] + signal['length']))

            # Check for intersection
            overlap = new_signal_bits.intersection(other_signal_bits)
            if overlap:
                return True, f"Signal would overlap with signal '{signal['name']}' at bit(s) {sorted(list(overlap))}"

        return False, ""

    def check_message_constraints(self, start_bit, length):
        """
        Check if the signal fits within message constraints
        Returns: (bool, str) - (is_valid, error_message)
        """
        if not self.signal_data or not self.handler:
            return False, "Cannot validate message constraints: missing data"

        # Get the current message
        current_message = None
        for message in self.handler.get_messages():
            if message['name'] == self.signal_data['message_name']:
                current_message = message
                break

        if not current_message:
            return False, "Cannot find current message"

        # Calculate message length in bits (length is in bytes)
        message_length_bits = current_message['length'] * 8

        # Check if signal would exceed message length
        if start_bit + length > message_length_bits:
            return False, f"Signal would exceed message length. Maximum allowed end bit is {message_length_bits - 1}"

        return True, ""

    def validate_and_accept(self):
        # Get values from UI
        new_name = self.new_name_edit.text()
        new_length = self.length_spin.value()
        new_start_bit = self.start_bit_spin.value()
        new_byte_order = self.byte_order_combo.currentText()
        new_is_signed = self.is_signed_check.isChecked()
        new_scale = self.scale_spin.value()
        new_offset = self.offset_spin.value()
        new_minimum = self.minimum_spin.value() if self.minimum_spin.value() != 0 else None
        new_maximum = self.maximum_spin.value() if self.maximum_spin.value() != 0 else None
        new_unit = self.unit_edit.text()
        new_comment = self.comment_edit.toPlainText()

        # Validate name
        if not new_name:
            QMessageBox.warning(self, "Validation Error", "Signal name cannot be empty.")
            return

        # Check if name is valid DBC name
        is_valid, error_msg = self.is_valid_dbc_name(new_name)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return

        # Check for duplicate name
        if new_name != self.current_name:
            is_duplicate, message_name = self.is_name_duplicate(new_name)
            if is_duplicate:
                QMessageBox.warning(self, "Validation Error", 
                                  f"A signal with the name '{new_name}' already exists in message '{message_name}'.")
                return

        # Check signal overlap and message constraints
        has_overlap, overlap_error = self.check_signal_overlap(new_start_bit, new_length)
        if has_overlap:
            QMessageBox.warning(self, "Validation Error", overlap_error)
            return

        is_valid_pos, constraint_error = self.check_message_constraints(new_start_bit, new_length)
        if not is_valid_pos:
            QMessageBox.warning(self, "Validation Error", constraint_error)
            return

        # Validate min/max
        if new_minimum is not None and new_maximum is not None and new_minimum > new_maximum:
            QMessageBox.warning(self, "Validation Error", "Minimum value cannot be greater than maximum value.")
            return

        # Get selected receivers
        new_receivers = self.get_selected_receivers()
        
        # Validate receivers
        if not new_receivers:
            response = QMessageBox.question(
                self,
                "No Receivers Selected",
                "No receivers are selected for this signal. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if response == QMessageBox.No:
                return

        # Emit signals for changed values
        if new_name != self.current_name:
            self.name_edited.emit(new_name)
        if new_length != self.current_length:
            self.length_edited.emit(new_length)
        if new_start_bit != self.current_start_bit:
            self.start_bit_edited.emit(new_start_bit)
        if new_byte_order != self.signal_data.get('byte_order', 'little_endian'):
            self.byte_order_edited.emit(new_byte_order)
        if new_is_signed != self.signal_data.get('is_signed', False):
            self.is_signed_edited.emit(new_is_signed)
        if new_scale != float(self.signal_data.get('scale', 1.0)):
            self.scale_edited.emit(new_scale)
        if new_offset != float(self.signal_data.get('offset', 0.0)):
            self.offset_edited.emit(new_offset)
        if new_minimum != self.signal_data.get('minimum'):
            self.minimum_edited.emit(new_minimum if new_minimum is not None else 0.0)
        if new_maximum != self.signal_data.get('maximum'):
            self.maximum_edited.emit(new_maximum if new_maximum is not None else 0.0)
        if new_unit != self.signal_data.get('unit', ''):
            self.unit_edited.emit(new_unit)
        if new_comment != self.signal_data.get('comment', ''):
            self.comment_edited.emit(new_comment)

        # Emit receivers_edited signal if changed
        current_receivers = set(self.signal_data.get('receivers', []))
        if set(new_receivers) != current_receivers:
            self.receivers_edited.emit(new_receivers)

        self.accept() 