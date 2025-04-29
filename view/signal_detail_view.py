from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFrame, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from controller.edit_controller import EditController
from view.signal_edit_dialog import SignalEditDialog
from controller.dbc_io_handler import DBC_IO_Handler
from PyQt5.QtCore import pyqtSignal

class SignalValuesDialog(QDialog):
    """Dialog for displaying signal value choices"""
    def __init__(self, signal_data, parent=None):
        super().__init__(parent)
        self.signal_data = signal_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Signal Values: {self.signal_data['name']}")
        self.setMinimumSize(500, 400)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with signal name
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        signal_name_label = QLabel(f"Value Table for {self.signal_data['name']}")
        signal_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(signal_name_label)
        
        main_layout.addWidget(header_frame)
        
        # Create table for values
        table = QTableWidget()
        table.setColumnCount(3)
        table.setHorizontalHeaderLabels(["Raw Value", "Hex Value", "Description"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Set column widths
        table.setColumnWidth(0, 100)
        table.setColumnWidth(1, 100)
        
        # Style the table
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        # Get the choices
        choices = self.signal_data.get('choices', {})
        if choices and isinstance(choices, dict):
            # Set number of rows
            table.setRowCount(len(choices))
            
            # Add choices to table
            for i, (value, description) in enumerate(sorted(choices.items())):
                # Create raw value item
                raw_value_item = QTableWidgetItem(str(value))
                raw_value_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 0, raw_value_item)
                
                # Create hex value item
                try:
                    hex_value = f"0x{int(value):X}"
                except (ValueError, TypeError):
                    hex_value = "N/A"
                hex_value_item = QTableWidgetItem(hex_value)
                hex_value_item.setTextAlignment(Qt.AlignCenter)
                table.setItem(i, 1, hex_value_item)
                
                # Create description item
                description_item = QTableWidgetItem(str(description))
                table.setItem(i, 2, description_item)
                
                # Add alternating row colors
                if i % 2 == 0:
                    for col in range(3):
                        table.item(i, col).setBackground(QColor("#f9f9f9"))
        else:
            # No choices available
            table.setRowCount(1)
            no_data_item = QTableWidgetItem("No value table defined for this signal")
            no_data_item.setTextAlignment(Qt.AlignCenter)
            table.setSpan(0, 0, 1, 3)
            table.setItem(0, 0, no_data_item)
        
        # Add table to layout with a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(table)
        main_layout.addWidget(scroll_area)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)

class SignalDetailView(QDialog):
    signal_edited = pyqtSignal(dict, dict)  # old_signal, new_signal
    
    def __init__(self, signal_data, handler, parent=None):
        super().__init__(parent)
        self.signal_data = signal_data.copy()  # Make a copy to track changes
        self.handler = handler
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Signal Details: {self.signal_data['name']}")
        self.setMinimumSize(700, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with signal name
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        self.signal_name_label = QLabel(self.signal_data['name'])
        self.signal_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(self.signal_name_label)
        
        message_info = QLabel(f"Message: {self.signal_data['message_name']} (ID: 0x{self.signal_data['message_id']:X})")
        message_info.setFont(QFont("Arial", 10))
        header_layout.addWidget(message_info)
        
        # Add Edit button
        edit_button = QPushButton("Edit")
        edit_button.setToolTip("Edit signal name")
        edit_button.setMinimumWidth(80)
        edit_button.clicked.connect(self.open_edit_dialog)
        header_layout.addWidget(edit_button)
        
        # Check if signal has choices for later use
        has_choices = self.signal_data.get('choices') and isinstance(self.signal_data.get('choices'), dict) and len(self.signal_data.get('choices')) > 0
        
        main_layout.addWidget(header_frame)
        
        # Create buttons bar (always show it, regardless of choices)
        buttons_frame = QFrame()
        buttons_frame.setFrameShape(QFrame.StyledPanel)
        buttons_frame.setStyleSheet("background-color: #f5f5f5; border-radius: 5px;")
        buttons_layout = QHBoxLayout(buttons_frame)
        buttons_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add value table button
        values_button = QPushButton("Value Table")
        values_button.setToolTip("View detailed value table for this signal")
        values_button.setMinimumWidth(120)
        values_button.setStyleSheet("""
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """)
        values_button.clicked.connect(self.show_values_dialog)
        buttons_layout.addWidget(values_button)
        
        # Add count label to show how many values are defined
        if has_choices:
            choices_count = len(self.signal_data.get('choices', {}))
            values_count_label = QLabel(f"{choices_count} values defined")
            values_count_label.setStyleSheet("color: #666; font-style: italic;")
        else:
            values_count_label = QLabel("No values defined")
            values_count_label.setStyleSheet("color: #999; font-style: italic;")
        buttons_layout.addWidget(values_count_label)
        
        buttons_layout.addStretch()
        main_layout.addWidget(buttons_frame)
        
        # Create table widget
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Property", "Value"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        # Helper function to format value
        def format_value(value):
            if value is None:
                return "Not specified"
            if isinstance(value, bool):
                return "Yes" if value else "No"
            if isinstance(value, (dict, list)) and not value:
                return "None"
            if isinstance(value, dict):
                if len(value) > 5:
                    return f"{len(value)} values defined (use 'Value Table' button to view)"
                return ", ".join([f"{k}: {v}" for k, v in value.items()])
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value)
        
        # Define property groups and their items
        property_groups = [
            {
                "name": "Basic Information",
                "items": [
                    ("Name", self.signal_data['name'], True),
                    ("Length", str(self.signal_data['length']), True),
                    ("Start Bit", str(self.signal_data['start']), True),
                    ("Byte Order", self.signal_data.get('byte_order', 'Not specified'), False),
                    ("Value Type", self.signal_data.get('value_type', 'Not specified'), False),
                    ("Factor", str(self.signal_data.get('factor', 1)), False),
                    ("Offset", str(self.signal_data.get('offset', 0)), False),
                    ("Minimum", str(self.signal_data.get('minimum', 'Not specified')), False),
                    ("Maximum", str(self.signal_data.get('maximum', 'Not specified')), False),
                    ("Unit", self.signal_data.get('unit', 'Not specified'), False),
                    ("Comment", self.signal_data.get('comment', 'Not specified'), False)
                ]
            }
        ]
        
        # Add rows to table
        total_rows = sum(len(group["items"]) for group in property_groups)
        table.setRowCount(total_rows)
        
        current_row = 0
        for group in property_groups:
            # Add group header
            header_item = QTableWidgetItem(group["name"])
            header_item.setBackground(QColor("#f0f0f0"))
            header_item.setFont(QFont("Arial", 10, QFont.Bold))
            table.setItem(current_row, 0, header_item)
            table.setSpan(current_row, 0, 1, 2)
            current_row += 1
            
            # Add group items
            for prop_name, prop_value, is_editable in group["items"]:
                # Property name
                name_item = QTableWidgetItem(prop_name)
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(current_row, 0, name_item)
                
                # Property value
                value_item = QTableWidgetItem(format_value(prop_value))
                if not is_editable:
                    value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
                table.setItem(current_row, 1, value_item)
                
                current_row += 1
        
        # Add table to layout with a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setWidget(table)
        main_layout.addWidget(scroll_area)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        # Connect cell change signal
        table.cellChanged.connect(self._on_cell_changed)
        
    def _on_cell_changed(self, row, column):
        if column != 1:  # Only handle value column changes
            return
            
        table = self.findChild(QTableWidget)
        if not table:
            return
            
        property_name = table.item(row, 0).text()
        new_value = table.item(row, 1).text()
        
        try:
            if property_name == "Length":
                new_length = int(new_value)
                success, error = self.handler.edit_controller.edit_signal_length(
                    self.signal_data['message_name'],
                    self.signal_data['name'],
                    new_length
                )
                if success:
                    self.signal_data['length'] = new_length
                else:
                    QMessageBox.critical(self, "Error", error)
                    table.item(row, 1).setText(str(self.signal_data['length']))
                    
            elif property_name == "Start Bit":
                new_start_bit = int(new_value)
                success, error = self.handler.edit_controller.edit_signal_start_bit(
                    self.signal_data['message_name'],
                    self.signal_data['name'],
                    new_start_bit
                )
                if success:
                    self.signal_data['start'] = new_start_bit
                else:
                    QMessageBox.critical(self, "Error", error)
                    table.item(row, 1).setText(str(self.signal_data['start']))
                    
        except ValueError:
            QMessageBox.critical(self, "Error", f"Invalid value for {property_name}. Must be a valid integer.")
            if property_name == "Length":
                table.item(row, 1).setText(str(self.signal_data['length']))
            elif property_name == "Start Bit":
                table.item(row, 1).setText(str(self.signal_data['start']))

    def show_values_dialog(self):
        """Show the values dialog if the signal has choices defined"""
        values_dialog = SignalValuesDialog(self.signal_data, self)
        values_dialog.exec_()

    def open_edit_dialog(self):
        dialog = SignalEditDialog(
            self.signal_data['name'],
            self.signal_data['length'],
            self.signal_data['start'],
            self.signal_data,
            self.handler,
            self
        )
        dialog.name_edited.connect(self.handle_name_edited)
        dialog.length_edited.connect(self.handle_length_edited)
        dialog.start_bit_edited.connect(self.handle_start_bit_edited)
        dialog.byte_order_edited.connect(self.handle_byte_order_edited)
        dialog.is_signed_edited.connect(self.handle_is_signed_edited)
        dialog.scale_edited.connect(self.handle_scale_edited)
        dialog.offset_edited.connect(self.handle_offset_edited)
        dialog.minimum_edited.connect(self.handle_minimum_edited)
        dialog.maximum_edited.connect(self.handle_maximum_edited)
        dialog.unit_edited.connect(self.handle_unit_edited)
        dialog.exec_()

    def handle_name_edited(self, new_name):
        if new_name == self.signal_data['name']:
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
        
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_name(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_name
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data and UI
        self.signal_data['name'] = new_name
        self.signal_name_label.setText(new_name)
        self.setWindowTitle(f"Signal Details: {new_name}")
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_length_edited(self, new_length):
        if new_length == self.signal_data['length']:
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_length(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_length
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['length'] = new_length
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_start_bit_edited(self, new_start_bit):
        if new_start_bit == self.signal_data['start']:
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_start_bit(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_start_bit
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['start'] = new_start_bit
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_byte_order_edited(self, new_byte_order):
        if new_byte_order == self.signal_data.get('byte_order'):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_byte_order(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_byte_order
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['byte_order'] = new_byte_order
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_is_signed_edited(self, is_signed):
        if is_signed == self.signal_data.get('is_signed'):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_is_signed(
            self.signal_data['message_name'],
            self.signal_data['name'],
            is_signed
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['is_signed'] = is_signed
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_scale_edited(self, new_scale):
        if new_scale == float(self.signal_data.get('scale', 1.0)):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_scale(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_scale
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['scale'] = new_scale
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_offset_edited(self, new_offset):
        if new_offset == float(self.signal_data.get('offset', 0.0)):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_offset(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_offset
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['offset'] = new_offset
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_minimum_edited(self, new_minimum):
        if new_minimum == self.signal_data.get('minimum'):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_minimum(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_minimum
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['minimum'] = new_minimum
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_maximum_edited(self, new_maximum):
        if new_maximum == self.signal_data.get('maximum'):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_maximum(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_maximum
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['maximum'] = new_maximum
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def handle_unit_edited(self, new_unit):
        if new_unit == self.signal_data.get('unit', ''):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_signal = self.signal_data.copy()
        success, error = self.handler.edit_controller.edit_signal_unit(
            self.signal_data['message_name'],
            self.signal_data['name'],
            new_unit
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.signal_data['unit'] = new_unit
        
        # Emit signal with old and new signal data
        self.signal_edited.emit(old_signal, self.signal_data)

    def find_handler(self):
        # Traverse parent chain to find handler (assumes parent is MessageDetailView or similar)
        parent = self.parent()
        while parent:
            if hasattr(parent, 'message_data') and hasattr(parent, 'parent'):
                # MessageDetailView: parent().parent() is likely DBCDisplayView
                grandparent = parent.parent()
                if hasattr(grandparent, 'current_handler'):
                    return grandparent.current_handler
            parent = parent.parent() if hasattr(parent, 'parent') else None
        return None 