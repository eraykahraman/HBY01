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
        
        # Define all properties with their values
        properties = [
            # Basic Properties
            ("Basic Properties", None),  # Header
            ("Name", self.message_data['name']),
            ("Frame ID", f"0x{self.message_data['frame_id']:X}"),
            ("Length", f"{self.message_data['length']} bytes"),
            ("Comment", self.message_data['comment'] if self.message_data['comment'] else "No comment"),
            
            # Senders
            ("Senders", None),  # Header
            ("Senders List", ", ".join(self.message_data['senders']) if self.message_data['senders'] else "None"),
            
            # Frame Format
            ("Frame Format", None),  # Header
            ("Extended Frame", "Yes" if self.message_data.get('is_extended_frame', False) else "No"),
            ("CAN FD", "Yes" if self.message_data.get('is_fd', False) else "No"),
            ("Bus Name", self.message_data.get('bus_name', "Not specified")),
            
            # Header Information
            ("Header Information", None),  # Header
            ("Header ID", f"0x{self.message_data.get('header_id', 0):X}" if self.message_data.get('header_id') is not None else "Not specified"),
            ("Header Byte Order", self.message_data.get('header_byte_order', "Not specified")),
            ("Unused Bit Pattern", f"0x{self.message_data.get('unused_bit_pattern', 0):X}"),
            
            # Timing Information
            ("Timing Information", None),  # Header
            ("Send Type", self.message_data.get('send_type', "Not specified")),
            ("Cycle Time", f"{self.message_data.get('cycle_time', 'Not specified')} ms" if self.message_data.get('cycle_time') is not None else "Not specified"),
            
            # Contained Messages
            ("Contained Messages", None),  # Header
        ]
        
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
        table.setColumnCount(11)
        columns = [
            "Name", "Start Bit", "Length", "Byte Order", "Signed",
            "Scale", "Offset", "Minimum", "Maximum", "Unit", "Receivers"
        ]
        table.setHorizontalHeaderLabels(columns)
        
        # Enable manual column resizing
        for i in range(len(columns)):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column
        table.horizontalHeader().setStretchLastSection(True)
        
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
        
        # Add signals data
        signals = self.message_data['signals']
        table.setRowCount(len(signals))
        
        for row, signal in enumerate(signals):
            items = [
                QTableWidgetItem(signal['name']),
                QTableWidgetItem(str(signal['start'])),
                QTableWidgetItem(str(signal['length'])),
                QTableWidgetItem(signal['byte_order']),
                QTableWidgetItem('Yes' if signal['is_signed'] else 'No'),
                QTableWidgetItem(str(signal['scale'])),
                QTableWidgetItem(str(signal['offset'])),
                QTableWidgetItem(str(signal['minimum']) if signal['minimum'] is not None else ''),
                QTableWidgetItem(str(signal['maximum']) if signal['maximum'] is not None else ''),
                QTableWidgetItem(signal['unit'] if signal['unit'] else ''),
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
        
    def format_signals_list(self, signals):
        """Format the signals list for display"""
        if not signals:
            return "No signals"
            
        signal_list = []
        for signal in signals:
            # Format each signal with its key properties
            signal_info = [
                f"Name: {signal['name']}",
                f"  • Start Bit: {signal['start']}",
                f"  • Length: {signal['length']} bits",
                f"  • Byte Order: {signal['byte_order']}",
                f"  • Signed: {'Yes' if signal['is_signed'] else 'No'}"
            ]
            
            # Add optional properties if they exist
            if signal['unit']:
                signal_info.append(f"  • Unit: {signal['unit']}")
            if signal['scale'] != 1.0:
                signal_info.append(f"  • Scale: {signal['scale']}")
            if signal['offset'] != 0.0:
                signal_info.append(f"  • Offset: {signal['offset']}")
            if signal['minimum'] is not None:
                signal_info.append(f"  • Min: {signal['minimum']}")
            if signal['maximum'] is not None:
                signal_info.append(f"  • Max: {signal['maximum']}")
            if signal['comment']:
                signal_info.append(f"  • Comment: {signal['comment']}")
            
            # Add receivers if any
            if signal['receivers']:
                signal_info.append(f"  • Receivers: {', '.join(signal['receivers'])}")
            
            # Join the signal info with newlines and add to the list
            signal_list.append("\n".join(signal_info))
            
        # Join all signals with double newlines for better readability
        return "\n\n".join(signal_list)

    def show_signal_layout(self):
        """Show the signal layout view"""
        layout_view = SignalLayoutView(self.message_data, self)
        layout_view.show()  # Use show() to allow multiple windows 