from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SignalDetailView(QDialog):
    def __init__(self, signal_data, parent=None):
        super().__init__(parent)
        self.signal_data = signal_data
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
        
        signal_name_label = QLabel(self.signal_data['name'])
        signal_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(signal_name_label)
        
        message_info = QLabel(f"Message: {self.signal_data['message_name']} (ID: 0x{self.signal_data['message_id']:X})")
        message_info.setFont(QFont("Arial", 10))
        header_layout.addWidget(message_info)
        
        main_layout.addWidget(header_frame)
        
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