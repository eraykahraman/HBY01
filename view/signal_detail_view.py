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
            ("Basic Properties", [
                ("Name", self.signal_data['name']),
                ("Message", self.signal_data['message_name']),
                ("Message ID", f"0x{self.signal_data['message_id']:X}")
            ]),
            ("Bit Properties", [
                ("Start Bit", str(self.signal_data['start'])),
                ("Length", f"{self.signal_data['length']} bits"),
                ("Byte Order", self.signal_data['byte_order']),
                ("Signed", "Yes" if self.signal_data['is_signed'] else "No")
            ]),
            ("Scaling Properties", [
                ("Scale", str(self.signal_data['scale'])),
                ("Offset", str(self.signal_data['offset'])),
                ("Minimum", format_value(self.signal_data['minimum'])),
                ("Maximum", format_value(self.signal_data['maximum'])),
                ("Unit", format_value(self.signal_data['unit']))
            ]),
            ("Multiplexing", [
                ("Is Multiplexer", format_value(self.signal_data.get('is_multiplexer', False))),
                ("Multiplexer ID", format_value(self.signal_data.get('multiplexer_id'))),
                ("Multiplexer Signal", format_value(self.signal_data.get('multiplexer_signal'))),
                ("Multiplexer Values", format_value(self.signal_data.get('multiplexer_values')))
            ]),
            ("Value Properties", [
                ("Is Float", format_value(self.signal_data.get('is_float', False))),
                ("Decimal Places", format_value(self.signal_data.get('decimal'))),
                ("Choices", format_value(self.signal_data.get('choices')))
            ]),
            ("J1939 Properties", [
                ("SPN", format_value(self.signal_data.get('spn'))),
                ("PGN", format_value(self.signal_data.get('pgn'))),
                ("Source Address (SA)", format_value(self.signal_data.get('sa'))),
                ("Destination Address (DA)", format_value(self.signal_data.get('da'))),
                ("Priority", format_value(self.signal_data.get('priority'))),
                ("Address", format_value(self.signal_data.get('address'))),
                ("Is J1939", format_value(self.signal_data.get('is_j1939', False)))
            ]),
            ("Communication", [
                ("Receivers", ", ".join(self.signal_data['receivers']) if self.signal_data['receivers'] else "None")
            ]),
            ("Documentation", [
                ("Comment", self.signal_data['comment'] if self.signal_data['comment'] else "No comment")
            ])
        ]
        
        # Calculate total number of rows needed
        total_rows = sum(len(items) + 1 for _, items in property_groups)  # +1 for each group header
        table.setRowCount(total_rows)
        
        # Add properties to table
        current_row = 0
        for group_name, items in property_groups:
            # Add group header
            header_item = QTableWidgetItem(group_name)
            header_item.setBackground(Qt.lightGray)
            header_item.setFont(QFont("Arial", 11, QFont.Bold))
            table.setItem(current_row, 0, header_item)
            table.setSpan(current_row, 0, 1, 2)
            current_row += 1
            
            # Add group items
            for prop_name, prop_value in items:
                name_item = QTableWidgetItem(prop_name)
                name_item.setFont(QFont("Arial", 10))
                value_item = QTableWidgetItem(str(prop_value))
                value_item.setFont(QFont("Arial", 10))
                
                table.setItem(current_row, 0, name_item)
                table.setItem(current_row, 1, value_item)
                current_row += 1
        
        # Add table to scroll area
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
        
    def show_values_dialog(self):
        """Show the values dialog if the signal has choices defined"""
        values_dialog = SignalValuesDialog(self.signal_data, self)
        values_dialog.exec_()

    def open_edit_dialog(self):
        dialog = SignalEditDialog(self.signal_data['name'], self)
        dialog.name_edited.connect(self.handle_name_edited)
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