from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QDialogButtonBox, QSpinBox, QFormLayout, QMessageBox)
from PyQt5.QtCore import pyqtSignal

class SignalEditDialog(QDialog):
    name_edited = pyqtSignal(str)
    length_edited = pyqtSignal(int)
    start_bit_edited = pyqtSignal(int)
    all_edited = pyqtSignal(str, int, int)  # name, length, start_bit

    def __init__(self, current_name, current_length=None, current_start_bit=None, signal_data=None, handler=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Signal")
        self.setMinimumWidth(350)
        self.current_name = current_name
        self.current_length = current_length
        self.current_start_bit = current_start_bit
        self.signal_data = signal_data
        self.handler = handler
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
        
        # Add help text for signal name rules
        help_label = QLabel("Signal name must:\n- Start with a letter\n- Contain only letters, numbers, and underscores\n- No spaces or special characters")
        help_label.setStyleSheet("color: #666; font-size: 10px;")
        layout.addWidget(help_label)
        
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
        button_box.accepted.connect(self.validate_and_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def is_name_duplicate(self, new_name):
        """Check if the signal name already exists in any message in the DBC file"""
        if not self.signal_data or not self.handler:
            return False
            
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
        new_name = self.name_edit.text().strip()
        new_length = self.length_spin.value()
        new_start_bit = self.start_bit_spin.value()
        
        # Validate DBC syntax
        is_valid, error_msg = self.is_valid_dbc_name(new_name)
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
            
        # Check for duplicate names across entire DBC file
        is_duplicate, message_name = self.is_name_duplicate(new_name)
        if is_duplicate:
            QMessageBox.warning(self, "Validation Error", 
                              f"A signal with the name '{new_name}' already exists in message '{message_name}'.\n"
                              "Signal names must be unique across the entire DBC file.")
            return

        # Check for signal overlap
        has_overlap, overlap_error = self.check_signal_overlap(new_start_bit, new_length)
        if has_overlap:
            QMessageBox.warning(self, "Validation Error", 
                              f"Signal position invalid: {overlap_error}")
            return

        # Check message constraints
        is_valid_pos, pos_error = self.check_message_constraints(new_start_bit, new_length)
        if not is_valid_pos:
            QMessageBox.warning(self, "Validation Error", 
                              f"Signal position invalid: {pos_error}")
            return
            
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