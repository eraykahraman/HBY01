from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QFrame, QSizePolicy, QWidget, QScrollArea)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QBrush

class SignalLayoutView(QDialog):
    def __init__(self, message_data, parent=None):
        super().__init__(parent)
        self.message_data = message_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Signal Layout: {self.message_data['name']}")
        self.setMinimumSize(600, 400)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with message info
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        header_layout = QHBoxLayout(header_frame)
        
        message_name_label = QLabel(f"{self.message_data['name']} (ID: 0x{self.message_data['frame_id']:X})")
        message_name_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(message_name_label)
        
        main_layout.addWidget(header_frame)
        
        # Create bit matrix table
        self.matrix_table = QTableWidget()
        self.matrix_table.setRowCount(8)  # 8 bits per byte
        self.matrix_table.setColumnCount(8)  # 8 bytes max for CAN message
        
        # Set headers
        bit_headers = ["7", "6", "5", "4", "3", "2", "1", "0"]
        self.matrix_table.setHorizontalHeaderLabels(bit_headers)
        byte_headers = [str(i) for i in range(8)]
        self.matrix_table.setVerticalHeaderLabels(byte_headers)
        
        # Set cell sizes
        for i in range(8):
            self.matrix_table.setColumnWidth(i, 60)
            self.matrix_table.setRowHeight(i, 40)
        
        # Style the table
        self.matrix_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
                gridline-color: #a0a0a0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        # Initialize empty cells
        for row in range(8):
            for col in range(8):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.matrix_table.setItem(row, col, item)
        
        # Fill in signal data
        self.populate_signal_layout()
        
        main_layout.addWidget(self.matrix_table)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def populate_signal_layout(self):
        """Populate the matrix with signal data"""
        # Define some colors for different signals
        colors = [
            "#FFB6C1", "#98FB98", "#87CEFA", "#DDA0DD",
            "#F0E68C", "#E6E6FA", "#FFE4B5", "#B8860B"
        ]
        
        for signal_index, signal in enumerate(self.message_data['signals']):
            start_bit = signal['start']
            length = signal['length']
            color = colors[signal_index % len(colors)]
            
            # Calculate the cells this signal occupies
            for bit in range(length):
                if signal['byte_order'] == 'little_endian':
                    current_bit = start_bit + bit
                else:
                    # For big endian, bits are arranged differently
                    current_bit = start_bit - bit
                
                byte_index = current_bit // 8
                bit_index = 7 - (current_bit % 8)  # Reverse bit order in byte
                
                if 0 <= byte_index < 8 and 0 <= bit_index < 8:
                    item = self.matrix_table.item(byte_index, bit_index)
                    if item:
                        item.setText(signal['name'])
                        item.setBackground(QBrush(QColor(color)))
                        # Set tooltip with signal details
                        tooltip = f"Signal: {signal['name']}\n"
                        tooltip += f"Start Bit: {signal['start']}\n"
                        tooltip += f"Length: {signal['length']} bits\n"
                        tooltip += f"Byte Order: {signal['byte_order']}\n"
                        tooltip += f"Signed: {'Yes' if signal['is_signed'] else 'No'}"
                        item.setToolTip(tooltip)

class SignalLayoutViewWidget(QWidget):
    """Signal layout visualization as a widget (non-dialog version)"""
    def __init__(self, message_data):
        super().__init__()
        self.message_data = message_data
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with instructions
        instructions_label = QLabel("Visual representation of signals in the message frame:")
        instructions_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(instructions_label)
        
        # Create bit matrix table
        self.matrix_table = QTableWidget()
        self.matrix_table.setRowCount(8)  # 8 bits per byte
        self.matrix_table.setColumnCount(8)  # 8 bytes max for CAN message
        
        # Set headers
        bit_headers = ["7", "6", "5", "4", "3", "2", "1", "0"]
        self.matrix_table.setHorizontalHeaderLabels(bit_headers)
        byte_headers = [str(i) for i in range(8)]
        self.matrix_table.setVerticalHeaderLabels(byte_headers)
        
        # Set cell sizes
        for i in range(8):
            self.matrix_table.setColumnWidth(i, 60)
            self.matrix_table.setRowHeight(i, 40)
        
        # Style the table
        self.matrix_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
                gridline-color: #a0a0a0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        
        # Initialize empty cells
        for row in range(8):
            for col in range(8):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.matrix_table.setItem(row, col, item)
        
        # Fill in signal data
        self.populate_signal_layout()
        
        # Add table to a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.matrix_table)
        
        main_layout.addWidget(scroll_area)
    
    def populate_signal_layout(self):
        """Populate the matrix with signal data"""
        # Define some colors for different signals
        colors = [
            "#FFB6C1", "#98FB98", "#87CEFA", "#DDA0DD",
            "#F0E68C", "#E6E6FA", "#FFE4B5", "#B8860B"
        ]
        
        for signal_index, signal in enumerate(self.message_data['signals']):
            start_bit = signal['start']
            length = signal['length']
            color = colors[signal_index % len(colors)]
            
            # Calculate the cells this signal occupies
            for bit in range(length):
                if signal['byte_order'] == 'little_endian':
                    current_bit = start_bit + bit
                else:
                    # For big endian, bits are arranged differently
                    current_bit = start_bit - bit
                
                byte_index = current_bit // 8
                bit_index = 7 - (current_bit % 8)  # Reverse bit order in byte
                
                if 0 <= byte_index < 8 and 0 <= bit_index < 8:
                    item = self.matrix_table.item(byte_index, bit_index)
                    if item:
                        item.setText(signal['name'])
                        item.setBackground(QBrush(QColor(color)))
                        # Set tooltip with signal details
                        tooltip = f"Signal: {signal['name']}\n"
                        tooltip += f"Start Bit: {signal['start']}\n"
                        tooltip += f"Length: {signal['length']} bits\n"
                        tooltip += f"Byte Order: {signal['byte_order']}\n"
                        tooltip += f"Signed: {'Yes' if signal['is_signed'] else 'No'}"
                        item.setToolTip(tooltip) 