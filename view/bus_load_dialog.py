from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QFormLayout, QSpinBox, QComboBox,
                            QMessageBox, QProgressBar)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from controller.bus_load_calculator import BusLoadCalculator

class BusLoadDialog(QDialog):
    """
    Dialog for calculating and displaying CAN bus load.
    """
    
    def __init__(self, messages, parent=None):
        """
        Initialize the bus load dialog.
        
        Args:
            messages (List[Dict]): List of message dictionaries from DBC_IO_Handler
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.messages = messages
        self.calculator = BusLoadCalculator()
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("CAN Bus Load Calculator")
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Bit rate selection
        bit_rate_group = QGroupBox("Bus Configuration")
        bit_rate_layout = QFormLayout(bit_rate_group)
        
        # Bit rate selection
        self.bit_rate_combo = QComboBox()
        self.bit_rate_combo.addItems([
            "125 kbps", "250 kbps", "500 kbps", "1 Mbps", 
            "2 Mbps", "5 Mbps", "8 Mbps", "Custom"
        ])
        self.bit_rate_combo.setCurrentText("500 kbps")
        self.bit_rate_combo.currentTextChanged.connect(self.on_bit_rate_changed)
        
        # Custom bit rate input
        self.custom_bit_rate = QSpinBox()
        self.custom_bit_rate.setRange(1000, 10000000)
        self.custom_bit_rate.setValue(500000)
        self.custom_bit_rate.setSingleStep(1000)
        self.custom_bit_rate.setSuffix(" bps")
        self.custom_bit_rate.setEnabled(False)
        
        bit_rate_layout.addRow("Bit Rate:", self.bit_rate_combo)
        bit_rate_layout.addRow("Custom Bit Rate:", self.custom_bit_rate)
        
        main_layout.addWidget(bit_rate_group)
        
        # Calculate button
        calculate_button = QPushButton("Calculate Bus Load")
        calculate_button.clicked.connect(self.calculate_bus_load)
        main_layout.addWidget(calculate_button)
        
        # Results section
        results_group = QGroupBox("Results")
        results_layout = QVBoxLayout(results_group)
        
        # Total bus load display
        total_load_layout = QHBoxLayout()
        total_load_layout.addWidget(QLabel("Total Bus Load:"))
        self.total_load_label = QLabel("0.00%")
        self.total_load_label.setFont(QFont("Arial", 14, QFont.Bold))
        total_load_layout.addWidget(self.total_load_label)
        total_load_layout.addStretch()
        
        # Progress bar for visual representation
        self.load_progress_bar = QProgressBar()
        self.load_progress_bar.setRange(0, 100)
        self.load_progress_bar.setValue(0)
        self.load_progress_bar.setTextVisible(True)
        self.load_progress_bar.setFormat("%p%")
        
        results_layout.addLayout(total_load_layout)
        results_layout.addWidget(self.load_progress_bar)
        
        # Message load table
        self.message_table = QTableWidget()
        self.setup_message_table()
        results_layout.addWidget(self.message_table)
        
        main_layout.addWidget(results_group)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)
        
    def setup_message_table(self):
        """Set up the message load table."""
        columns = [
            "Name", "ID", "Length", "Cycle Time", "Extended", "CAN FD", 
            "Transmission Time", "Load %"
        ]
        self.message_table.setColumnCount(len(columns))
        self.message_table.setHorizontalHeaderLabels(columns)
        
        # Set column widths
        header = self.message_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name column stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Length
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Cycle Time
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Extended
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # CAN FD
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Transmission Time
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Load %
        
        # Enable sorting
        self.message_table.setSortingEnabled(True)
        
    def on_bit_rate_changed(self, text):
        """Handle bit rate selection change."""
        if text == "Custom":
            self.custom_bit_rate.setEnabled(True)
        else:
            self.custom_bit_rate.setEnabled(False)
            # Extract bit rate from text (e.g., "500 kbps" -> 500000)
            if "kbps" in text:
                value = int(text.split()[0]) * 1000
            elif "Mbps" in text:
                value = int(text.split()[0]) * 1000000
            else:
                value = 500000  # Default
            self.custom_bit_rate.setValue(value)
            
    def calculate_bus_load(self):
        """Calculate and display the bus load."""
        # Get bit rate
        if self.bit_rate_combo.currentText() == "Custom":
            bit_rate = self.custom_bit_rate.value()
        else:
            # Extract bit rate from text
            text = self.bit_rate_combo.currentText()
            if "kbps" in text:
                bit_rate = int(text.split()[0]) * 1000
            elif "Mbps" in text:
                bit_rate = int(text.split()[0]) * 1000000
            else:
                bit_rate = 500000  # Default
                
        # Set bit rate in calculator
        self.calculator.set_bit_rate(bit_rate)
        
        # Calculate bus load
        total_load, message_loads = self.calculator.calculate_total_bus_load(self.messages)
        
        # Update UI
        self.total_load_label.setText(f"{total_load:.2f}%")
        self.load_progress_bar.setValue(min(100, int(total_load)))
        
        # Set progress bar color based on load
        if total_load < 50:
            self.load_progress_bar.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif total_load < 80:
            self.load_progress_bar.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.load_progress_bar.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        
        # Update message table
        self.message_table.setRowCount(len(message_loads))
        
        for row, msg in enumerate(message_loads):
            # Name
            self.message_table.setItem(row, 0, QTableWidgetItem(msg['name']))
            
            # ID (hex)
            id_item = QTableWidgetItem(f"0x{msg['id']:X}")
            id_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.message_table.setItem(row, 1, id_item)
            
            # Length
            length_item = QTableWidgetItem(str(msg['length']))
            length_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.message_table.setItem(row, 2, length_item)
            
            # Cycle Time
            cycle_time = msg['cycle_time']
            cycle_time_str = f"{cycle_time} ms" if cycle_time is not None and cycle_time > 0 else "N/A"
            cycle_time_item = QTableWidgetItem(cycle_time_str)
            cycle_time_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.message_table.setItem(row, 3, cycle_time_item)
            
            # Extended
            extended_item = QTableWidgetItem("Yes" if msg['is_extended'] else "No")
            extended_item.setTextAlignment(Qt.AlignCenter)
            self.message_table.setItem(row, 4, extended_item)
            
            # CAN FD
            fd_item = QTableWidgetItem("Yes" if msg['is_fd'] else "No")
            fd_item.setTextAlignment(Qt.AlignCenter)
            self.message_table.setItem(row, 5, fd_item)
            
            # Transmission Time
            tx_time_item = QTableWidgetItem(f"{msg['transmission_time_ms']:.3f} ms")
            tx_time_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.message_table.setItem(row, 6, tx_time_item)
            
            # Load %
            load_item = QTableWidgetItem(f"{msg['load_percentage']:.2f}%")
            load_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color code based on load
            if msg['load_percentage'] > 5:
                load_item.setBackground(QColor(255, 200, 200))  # Light red
            elif msg['load_percentage'] > 1:
                load_item.setBackground(QColor(255, 255, 200))  # Light yellow
                
            self.message_table.setItem(row, 7, load_item)
            
        # Sort by load percentage (descending)
        self.message_table.sortItems(7, Qt.DescendingOrder)
        
        # Show warning if load is high
        if total_load > 80:
            QMessageBox.warning(
                self, 
                "High Bus Load Warning", 
                f"The calculated bus load is {total_load:.2f}%, which is above the recommended threshold of 80%. "
                "This may lead to message delays or missed messages."
            )
        elif total_load > 50:
            QMessageBox.information(
                self, 
                "Moderate Bus Load", 
                f"The calculated bus load is {total_load:.2f}%, which is moderate. "
                "Consider monitoring the bus during operation to ensure reliable communication."
            ) 