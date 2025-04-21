from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFrame, QSizePolicy,
                            QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .signal_layout_view import SignalLayoutView

class MessageDetailView(QDialog):
    def __init__(self, message_data, parent=None):
        super().__init__(parent)
        self.message_data = message_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Message Details: {self.message_data['name']}")
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with message name
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        message_name_label = QLabel(self.message_data['name'])
        message_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(message_name_label)
        
        message_id_label = QLabel(f"ID: 0x{self.message_data['frame_id']:X}")
        message_id_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(message_id_label)
        
        header_layout.addStretch()
        
        # Add Show Signals button to header
        self.show_signals_button = QPushButton("Show Signals")
        self.show_signals_button.setFixedWidth(100)
        self.show_signals_button.clicked.connect(self.toggle_signals_view)
        header_layout.addWidget(self.show_signals_button)
        
        # Add Signal Layout button to header
        self.show_layout_button = QPushButton("Signal Layout")
        self.show_layout_button.setFixedWidth(100)
        self.show_layout_button.clicked.connect(self.show_signal_layout)
        header_layout.addWidget(self.show_layout_button)
        
        main_layout.addWidget(header_frame)
        
        # Create stacked widget for switching between details and signals
        self.stacked_widget = QStackedWidget()
        
        # Create and add details table
        self.details_table = self.create_details_table()
        self.stacked_widget.addWidget(self.details_table)
        
        # Create and add signals table
        self.signals_table = self.create_signals_table()
        self.stacked_widget.addWidget(self.signals_table)
        
        main_layout.addWidget(self.stacked_widget)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_details_table(self):
        """Create the details table widget"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
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
                return ", ".join([f"{k}: {v}" for k, v in value.items()])
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value)
        
        # Check if any signal is a multiplexer
        is_multiplexed = False
        for signal in self.message_data['signals']:
            if signal.get('is_multiplexer', False):
                is_multiplexed = True
                break
        
        # Get J1939 specifics if available
        j1939_specifics = self.message_data.get('j1939_specifics', {}) or {}
        if not isinstance(j1939_specifics, dict):
            j1939_specifics = {}
        
        # Determine protocol type
        protocol = "Standard CAN"
        if self.message_data.get('is_fd', False):
            protocol = "CAN FD"
        elif j1939_specifics:
            protocol = "J1939"
        
        # Define all properties with their values
        properties = [
            # Basic Properties
            ("Basic Properties", None),  # Header
            ("Name", self.message_data['name']),
            ("Frame ID", f"0x{self.message_data['frame_id']:X}"),
            ("Length", f"{self.message_data['length']} bytes"),
            ("Protocol", protocol),
            ("Signals Count", str(len(self.message_data['signals']))),
            ("Comment", self.message_data['comment'] if self.message_data['comment'] else "No comment"),
            
            # Senders
            ("Senders", None),  # Header
            ("Senders List", ", ".join(self.message_data['senders']) if self.message_data['senders'] else "None"),
            
            # Frame Format
            ("Frame Format", None),  # Header
            ("Extended Frame", format_value(self.message_data.get('is_extended_frame', False))),
            ("CAN FD", format_value(self.message_data.get('is_fd', False))),
            ("Bus Name", format_value(self.message_data.get('bus_name'))),
            
            # Header Information
            ("Header Information", None),  # Header
            ("Header ID", f"0x{self.message_data.get('header_id', 0):X}" if self.message_data.get('header_id') is not None else "Not specified"),
            ("Header Byte Order", format_value(self.message_data.get('header_byte_order'))),
            ("Unused Bit Pattern", f"0x{self.message_data.get('unused_bit_pattern', 0):X}"),
            
            # Timing Information
            ("Timing Information", None),  # Header
            ("Send Type", format_value(self.message_data.get('send_type'))),
            ("Cycle Time", f"{self.message_data.get('cycle_time')} ms" if self.message_data.get('cycle_time') is not None else "Not specified"),
            
            # Multiplexing
            ("Multiplexing", None),  # Header
            ("Is Multiplexed", format_value(is_multiplexed)),
        ]
        
        # J1939 Properties
        properties.extend([
            ("J1939 Properties", None),  # Header
            ("PGN", format_value(j1939_specifics.get('pgn'))),
            ("Priority", format_value(j1939_specifics.get('priority'))),
            ("Source Address", format_value(j1939_specifics.get('source_address'))),
            ("Destination Address", format_value(j1939_specifics.get('destination_address'))),
            ("PDU Format", format_value(j1939_specifics.get('pdu_format'))),
            ("PDU Specific", format_value(j1939_specifics.get('pdu_specific'))),
            ("Name", format_value(j1939_specifics.get('name'))),
            ("ID", format_value(j1939_specifics.get('id'))),
        ])
        
        # DBC Specifics
        dbc_specifics = self.message_data.get('dbc_specifics', {}) or {}
        if dbc_specifics and isinstance(dbc_specifics, dict):
            properties.extend([
                ("DBC Specifics", None),  # Header
            ])
            for key, value in dbc_specifics.items():
                properties.append((key, format_value(value)))
        
        # AUTOSAR Specifics
        autosar_specifics = self.message_data.get('autosar_specifics', {}) or {}
        if autosar_specifics and isinstance(autosar_specifics, dict):
            properties.extend([
                ("AUTOSAR Specifics", None),  # Header
            ])
            for key, value in autosar_specifics.items():
                properties.append((key, format_value(value)))
        
        # Contained Messages
        properties.append(("Contained Messages", None))  # Header
        
        # Add contained messages if they exist
        if self.message_data.get('contained_messages') and len(self.message_data['contained_messages']) > 0:
            for i, contained_msg in enumerate(self.message_data['contained_messages']):
                properties.append((f"Contained Message {i+1}", f"{contained_msg['name']} (ID: 0x{contained_msg['frame_id']:X}, Length: {contained_msg['length']} bytes)"))
        else:
            properties.append(("Contained Messages", "None"))
        
        # Set table rows
        table.setRowCount(len(properties))
        
        # Add all rows to table
        for row, (prop_name, prop_value) in enumerate(properties):
            # Check if this is a header row
            if prop_value is None:
                header_item = QTableWidgetItem(prop_name)
                header_item.setBackground(Qt.lightGray)
                header_item.setFont(QFont("Arial", 11, QFont.Bold))
                table.setItem(row, 0, header_item)
                table.setSpan(row, 0, 1, 2)
            else:
                name_item = QTableWidgetItem(prop_name)
                name_item.setFont(QFont("Arial", 10))
                value_item = QTableWidgetItem(str(prop_value))
                value_item.setFont(QFont("Arial", 10))
                
                table.setItem(row, 0, name_item)
                table.setItem(row, 1, value_item)
        
        scroll_area.setWidget(table)
        return scroll_area
        
    def create_signals_table(self):
        """Create the signals table widget"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        table = QTableWidget()
        columns = [
            "Name", "Start Bit", "Length", "Byte Order", "Signed",
            "Scale", "Offset", "Minimum", "Maximum", "Unit", 
            "Is Multiplexer", "Multiplexer ID", "Is Float", "Choices",
            "SPN", "Receivers"
        ]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        # Enable manual column resizing
        for i in range(len(columns)):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column
        table.horizontalHeader().setStretchLastSection(True)
        
        # Set column widths
        column_widths = {
            "Name": 150,
            "Start Bit": 80,
            "Length": 80,
            "Byte Order": 100,
            "Signed": 80,
            "Scale": 80,
            "Offset": 80,
            "Minimum": 80,
            "Maximum": 80,
            "Unit": 80,
            "Is Multiplexer": 100,
            "Multiplexer ID": 100,
            "Is Float": 80,
            "Choices": 150,
            "SPN": 80,
            "Receivers": 200
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            table.setColumnWidth(i, column_widths.get(col, 100))
        
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
                return ""
            if isinstance(value, bool):
                return "Yes" if value else "No"
            if isinstance(value, (dict, list)) and not value:
                return ""
            if isinstance(value, dict):
                return ", ".join([f"{k}: {v}" for k, v in value.items()])
            return str(value)
        
        # Add signals data
        signals = self.message_data['signals']
        table.setRowCount(len(signals))
        
        for row, signal in enumerate(signals):
            # Count choices if available
            choices_str = ""
            if signal.get('choices') and isinstance(signal.get('choices'), dict):
                choices = signal.get('choices')
                choices_str = ", ".join([f"{k}={v}" for k, v in choices.items()])
                if len(choices_str) > 50:
                    choices_str = f"{len(choices)} choices"
            
            items = [
                QTableWidgetItem(signal['name']),
                QTableWidgetItem(str(signal['start'])),
                QTableWidgetItem(str(signal['length'])),
                QTableWidgetItem(signal['byte_order']),
                QTableWidgetItem(format_value(signal['is_signed'])),
                QTableWidgetItem(str(signal['scale'])),
                QTableWidgetItem(str(signal['offset'])),
                QTableWidgetItem(str(signal['minimum']) if signal['minimum'] is not None else ''),
                QTableWidgetItem(str(signal['maximum']) if signal['maximum'] is not None else ''),
                QTableWidgetItem(signal['unit'] if signal['unit'] else ''),
                QTableWidgetItem(format_value(signal.get('is_multiplexer', False))),
                QTableWidgetItem(format_value(signal.get('multiplexer_id'))),
                QTableWidgetItem(format_value(signal.get('is_float', False))),
                QTableWidgetItem(choices_str),
                QTableWidgetItem(format_value(signal.get('spn'))),
                QTableWidgetItem(', '.join(signal['receivers']) if signal['receivers'] else '')
            ]
            
            for col, item in enumerate(items):
                table.setItem(row, col, item)
        
        scroll_area.setWidget(table)
        return scroll_area

    def toggle_signals_view(self):
        """Toggle between details and signals view"""
        current_index = self.stacked_widget.currentIndex()
        new_index = 1 if current_index == 0 else 0
        self.stacked_widget.setCurrentIndex(new_index)
        self.show_signals_button.setText("Show Details" if new_index == 1 else "Show Signals")
        
    def show_signal_layout(self):
        """Show the signal layout view"""
        layout_view = SignalLayoutView(self.message_data, self)
        layout_view.show()  # Use show() to allow multiple windows