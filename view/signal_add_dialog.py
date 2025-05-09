from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QSpinBox, QDoubleSpinBox,
                             QComboBox, QCheckBox, QFormLayout, QGroupBox,
                             QTabWidget, QMessageBox, QListWidget, QListWidgetItem,
                             QScrollArea, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
import re

class SignalAddDialog(QDialog):
    """Dialog for adding a new signal to a message"""
    signal_added = pyqtSignal(dict)  # Signal emitted when a signal is successfully added
    
    def __init__(self, message_data, handler, parent=None):
        super().__init__(parent)
        self.message_data = message_data
        self.handler = handler
        self.setup_ui()
        self.setup_validators()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Add Signal to {self.message_data['name']}")
        self.setMinimumSize(500, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create validation message area at the top
        self.validation_label = QLabel("")
        self.validation_label.setWordWrap(True)
        self.validation_label.setStyleSheet("color: red;")
        self.validation_label.setVisible(False)
        main_layout.addWidget(self.validation_label)
        
        # Create tabs for organizing input fields
        tab_widget = QTabWidget()
        
        # Basic Properties Tab
        basic_tab = QWidget()
        basic_layout = QVBoxLayout(basic_tab)
        
        # Signal name
        name_group = QGroupBox("Signal Name")
        name_layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter signal name")
        self.name_edit.textChanged.connect(self.validate_form)
        name_layout.addRow("Name:", self.name_edit)
        name_group.setLayout(name_layout)
        basic_layout.addWidget(name_group)
        
        # Signal position and size
        position_group = QGroupBox("Position and Size")
        position_layout = QFormLayout()
        
        self.start_bit_spin = QSpinBox()
        self.start_bit_spin.setMinimum(0)
        self.start_bit_spin.setMaximum(63)  # Maximum bit position for 8-byte message
        self.start_bit_spin.valueChanged.connect(self.validate_form)
        position_layout.addRow("Start Bit:", self.start_bit_spin)
        
        self.length_spin = QSpinBox()
        self.length_spin.setMinimum(1)
        self.length_spin.setMaximum(64)  # Maximum length for a signal
        self.length_spin.setValue(8)  # Default to 8 bits
        self.length_spin.valueChanged.connect(self.validate_form)
        position_layout.addRow("Length (bits):", self.length_spin)
        
        self.byte_order_combo = QComboBox()
        self.byte_order_combo.addItems(["Intel (Little Endian)", "Motorola (Big Endian)"])
        self.byte_order_combo.currentIndexChanged.connect(self.validate_form)
        position_layout.addRow("Byte Order:", self.byte_order_combo)
        
        position_group.setLayout(position_layout)
        basic_layout.addWidget(position_group)
        
        # Data type
        type_group = QGroupBox("Data Type")
        type_layout = QFormLayout()
        
        self.is_signed_check = QCheckBox("Signed Value")
        type_layout.addRow("", self.is_signed_check)
        
        self.is_float_check = QCheckBox("Float Value")
        self.is_float_check.toggled.connect(self.on_float_toggled)
        type_layout.addRow("", self.is_float_check)
        
        type_group.setLayout(type_layout)
        basic_layout.addWidget(type_group)
        
        # Add basic tab
        tab_widget.addTab(basic_tab, "Basic Properties")
        
        # Value Properties Tab
        value_tab = QWidget()
        value_layout = QVBoxLayout(value_tab)
        
        value_group = QGroupBox("Value Properties")
        value_form = QFormLayout()
        
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setDecimals(10)
        self.scale_spin.setRange(-1e9, 1e9)
        self.scale_spin.setValue(1.0)  # Default scale
        value_form.addRow("Scale:", self.scale_spin)
        
        self.offset_spin = QDoubleSpinBox()
        self.offset_spin.setDecimals(10)
        self.offset_spin.setRange(-1e9, 1e9)
        self.offset_spin.setValue(0.0)  # Default offset
        value_form.addRow("Offset:", self.offset_spin)
        
        self.min_spin = QDoubleSpinBox()
        self.min_spin.setDecimals(10)
        self.min_spin.setRange(-1e9, 1e9)
        value_form.addRow("Minimum:", self.min_spin)
        
        self.max_spin = QDoubleSpinBox()
        self.max_spin.setDecimals(10)
        self.max_spin.setRange(-1e9, 1e9)
        value_form.addRow("Maximum:", self.max_spin)
        
        self.unit_edit = QLineEdit()
        self.unit_edit.setPlaceholderText("e.g., km/h, °C, rpm")
        value_form.addRow("Unit:", self.unit_edit)
        
        value_group.setLayout(value_form)
        value_layout.addWidget(value_group)
        
        # Add value tab
        tab_widget.addTab(value_tab, "Value Properties")
        
        # Advanced Properties Tab
        advanced_tab = QWidget()
        advanced_layout = QVBoxLayout(advanced_tab)
        
        # Multiplexing group
        multiplex_group = QGroupBox("Multiplexing")
        multiplex_layout = QFormLayout()
        
        self.is_multiplexer_check = QCheckBox("Is Multiplexer")
        multiplex_layout.addRow("", self.is_multiplexer_check)
        
        self.multiplexer_id_spin = QSpinBox()
        self.multiplexer_id_spin.setMinimum(-1)
        self.multiplexer_id_spin.setMaximum(255)
        self.multiplexer_id_spin.setValue(-1)  # Default to not multiplexed
        multiplex_layout.addRow("Multiplexer ID (-1 = not multiplexed):", self.multiplexer_id_spin)
        
        multiplex_group.setLayout(multiplex_layout)
        advanced_layout.addWidget(multiplex_group)
        
        # Use message receivers info
        receivers_group = QGroupBox("Signal Receivers")
        receivers_layout = QVBoxLayout()
        
        # Information label
        receivers_info = QLabel("This signal will use the message's receivers.")
        receivers_info.setWordWrap(True)
        
        # Display current message receivers
        message_receivers = self.message_data.get('receivers', [])
        receivers_text = ', '.join(message_receivers) if message_receivers else "None"
        current_receivers = QLabel(f"Current message receivers: {receivers_text}")
        current_receivers.setWordWrap(True)
        
        receivers_layout.addWidget(receivers_info)
        receivers_layout.addWidget(current_receivers)
        
        receivers_group.setLayout(receivers_layout)
        advanced_layout.addWidget(receivers_group)
        
        # Add advanced tab
        tab_widget.addTab(advanced_tab, "Advanced Properties")
        
        # Add tab widget to main layout
        main_layout.addWidget(tab_widget)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.add_button = QPushButton("Add Signal")
        self.add_button.clicked.connect(self.add_signal)
        self.add_button.setDefault(True)
        button_layout.addWidget(self.add_button)
        
        main_layout.addLayout(button_layout)
        
        # Run initial validation
        self.validate_form()
    
    def setup_validators(self):
        """Setup input validators"""
        # We're using custom validation instead of QRegExpValidator
        # No need for additional setup
    
    def on_float_toggled(self, checked):
        """Handle when float checkbox is toggled"""
        if checked:
            # Float signals cannot be signed
            self.is_signed_check.setChecked(False)
            self.is_signed_check.setEnabled(False)
            
            # Float signals should have length of 32 or 64 bits
            if self.length_spin.value() != 32 and self.length_spin.value() != 64:
                self.length_spin.setValue(32)  # Default to 32-bit float
        else:
            self.is_signed_check.setEnabled(True)
        
        self.validate_form()
    
    def validate_form(self):
        """Validate all inputs and highlight any issues"""
        valid = True
        error_messages = []
        
        # Validate signal name
        signal_name = self.name_edit.text().strip()
        
        # Now make the number check more explicit in the validation flow
        if not signal_name:
            valid = False
            error_messages.append("Signal name cannot be empty")
            self.highlight_field(self.name_edit, True)
        elif signal_name[0].isdigit():
            valid = False
            error_messages.append("Signal name cannot start with a number")
            self.highlight_field(self.name_edit, True)
        elif not self.is_valid_signal_name(signal_name):
            valid = False
            error_message = self.get_name_validation_error(signal_name)
            error_messages.append(error_message)
            self.highlight_field(self.name_edit, True)
        elif self.is_duplicate_signal_name(signal_name):
            valid = False
            error_messages.append(f"Signal name '{signal_name}' already exists in the DBC file")
            self.highlight_field(self.name_edit, True)
        else:
            self.highlight_field(self.name_edit, False)
        
        # Validate signal position and size
        start_bit = self.start_bit_spin.value()
        length = self.length_spin.value()
        is_motorola = self.byte_order_combo.currentIndex() == 1  # 1 = Motorola
        max_message_bits = self.message_data['length'] * 8
        
        # Check if signal fits within message
        end_bit = self.calculate_end_bit(start_bit, length, is_motorola)
        if end_bit >= max_message_bits:
            valid = False
            error_messages.append(f"Signal exceeds message length ({max_message_bits} bits)")
            self.highlight_field(self.start_bit_spin, True)
            self.highlight_field(self.length_spin, True)
        else:
            self.highlight_field(self.start_bit_spin, False)
            self.highlight_field(self.length_spin, False)
        
        # Check for overlapping signals
        if self.is_overlapping_with_existing_signals(start_bit, length, is_motorola):
            valid = False
            error_messages.append("Signal overlaps with existing signals")
            self.highlight_field(self.start_bit_spin, True)
            self.highlight_field(self.length_spin, True)
        
        # Validate float signal properties
        if self.is_float_check.isChecked():
            if length != 32 and length != 64:
                valid = False
                error_messages.append("Float signals must be 32 or 64 bits in length")
                self.highlight_field(self.length_spin, True)
        
        # Display validation error messages and enable/disable add button
        if error_messages:
            self.validation_label.setText("• " + "\n• ".join(error_messages))
            self.validation_label.setVisible(True)
        else:
            self.validation_label.setVisible(False)
        
        self.add_button.setEnabled(valid)
        return valid
    
    def is_valid_signal_name(self, name):
        """
        Validate if the signal name follows DBC syntax rules
        Returns True if valid, False otherwise
        """
        if not name:
            return False
            
        # Check if name starts with a number - this is already here but making it explicit
        if name[0].isdigit():
            print(f"Invalid signal name '{name}': cannot start with a number")
            return False
            
        # Check for valid characters (letters, numbers, and underscores only)
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            return False
            
        return True
    
    def is_duplicate_signal_name(self, name):
        """Check if signal name already exists in the entire DBC file"""
        # Skip empty names
        if not name:
            return False
            
        # Use same method as in signal_edit_dialog.py
        if self.handler and hasattr(self.handler, 'get_signals'):
            try:
                # Get all signals from the DBC file
                all_signals = self.handler.get_signals()
                
                # Check for duplicates across all signals
                for signal in all_signals:
                    if signal['name'].lower() == name.lower():  # Case-insensitive check
                        print(f"Found duplicate signal '{name}' in message {signal.get('message_name', 'unknown')}")
                        return True
                        
                # No duplicates found
                return False
            except Exception as e:
                print(f"Error checking for duplicate signal names: {str(e)}")
                # Fall back to checking current message only
        
        # If handler.get_signals() is not available, fall back to checking just current message
        for signal in self.message_data['signals']:
            if signal['name'].lower() == name.lower():  # Case-insensitive check
                return True
                
        return False
    
    def calculate_end_bit(self, start_bit, length, is_motorola):
        """Calculate the end bit position based on start bit, length and byte order"""
        if not is_motorola:  # Intel (Little Endian)
            return start_bit + length - 1
        else:  # Motorola (Big Endian)
            # For Motorola format, we need special bit position calculation
            # This is a simplified calculation - actual implementations might vary
            return start_bit + length - 1
    
    def is_overlapping_with_existing_signals(self, start_bit, length, is_motorola):
        """Check if the signal overlaps with existing signals in the message"""
        # Get the bit range for the new signal
        new_signal_end_bit = self.calculate_end_bit(start_bit, length, is_motorola)
        new_signal_bits = set(range(start_bit, new_signal_end_bit + 1))
        
        # Check against all existing signals
        for signal in self.message_data['signals']:
            signal_start = signal['start']
            signal_length = signal['length']
            signal_is_motorola = signal['byte_order'] == 'big_endian'
            
            signal_end_bit = self.calculate_end_bit(signal_start, signal_length, signal_is_motorola)
            signal_bits = set(range(signal_start, signal_end_bit + 1))
            
            # Check for intersection
            if new_signal_bits.intersection(signal_bits):
                return True
        
        return False
    
    def highlight_field(self, field, is_error):
        """Highlight a field to indicate validation errors"""
        if is_error:
            field.setStyleSheet("background-color: #FFEBEB;")  # Light red background
        else:
            field.setStyleSheet("")  # Reset style
    
    def get_name_validation_error(self, name):
        """Get detailed error message for invalid signal name"""
        if not name:
            return "Signal name cannot be empty."
            
        # Check for valid characters
        return "Signal name can only contain letters, numbers, and underscores, and must start with a letter."
    
    def add_signal(self):
        """Add the signal based on the form inputs"""
        # Run validation again before adding
        if not self.validate_form():
            return
        
        # Get signal name
        signal_name = self.name_edit.text().strip()
        
        # Create signal data structure
        signal_data = {
            'name': signal_name,
            'start': self.start_bit_spin.value(),
            'length': self.length_spin.value(),
            'byte_order': 'little_endian' if self.byte_order_combo.currentIndex() == 0 else 'big_endian',
            'is_signed': self.is_signed_check.isChecked(),
            'is_float': self.is_float_check.isChecked(),
            'scale': self.scale_spin.value(),
            'offset': self.offset_spin.value(),
            'minimum': self.min_spin.value() if self.min_spin.value() != 0 else None,
            'maximum': self.max_spin.value() if self.max_spin.value() != 0 else None,
            'unit': self.unit_edit.text().strip(),
            'receivers': self.message_data.get('receivers', []),  # Use message receivers
            'comment': '',
            'choices': {},
        }
        
        # Add multiplexing info if applicable
        if self.is_multiplexer_check.isChecked():
            signal_data['is_multiplexer'] = True
        
        if self.multiplexer_id_spin.value() >= 0:
            signal_data['multiplexer_id'] = self.multiplexer_id_spin.value()
        
        # Emit signal with the new signal data
        self.signal_added.emit(signal_data)
        self.accept() 