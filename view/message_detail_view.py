from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QTabWidget, 
                            QWidget, QGridLayout, QGroupBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

class MessageDetailView(QDialog):
    """Popup dialog to display detailed message information"""
    
    def __init__(self, parent=None, message=None, dbc_file_path=None):
        super().__init__(parent)
        self.message = message
        self.dbc_file_path = dbc_file_path
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface for the message detail popup"""
        self.setWindowTitle(f"Message Details: {self.message.name}")
        self.setMinimumSize(800, 600)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Add DBC file information at the top
        if self.dbc_file_path:
            # Create a header showing the DBC file name
            dbc_file_name = self.dbc_file_path.split('/')[-1].split('\\')[-1]
            dbc_label = QLabel(f"<h3>DBC File: {dbc_file_name}</h3>")
            dbc_label.setStyleSheet("""
                background-color: #f0f0f0;
                padding: 5px 10px;
                border-radius: 4px;
                border: 1px solid #cccccc;
                color: #0066cc;
            """)
            dbc_label.setAlignment(Qt.AlignCenter)
            main_layout.addWidget(dbc_label)
        
        # Create tab widget for organizing content
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        overview_tab = QWidget()
        signals_tab = QWidget()
        
        tab_widget.addTab(overview_tab, "Message Overview")
        tab_widget.addTab(signals_tab, "Signals")
        
        # Setup Overview Tab
        overview_layout = QVBoxLayout(overview_tab)
        
        # Message Properties group
        props_group = QGroupBox("Message Properties")
        props_layout = QGridLayout()
        props_group.setLayout(props_layout)
        
        # Add message properties
        row = 0
        property_data = [
            ("Name", self.message.name),
            ("ID (Hex)", f"0x{self.message.frame_id:X}"),
            ("ID (Decimal)", str(self.message.frame_id)),
            ("Length (Bytes)", str(self.message.length)),
            ("Extended Frame", "Yes" if getattr(self.message, 'is_extended_frame', False) else "No"),
            ("Signal Count", str(len(self.message.signals))),
        ]
        
        # Add any additional properties if they exist
        if hasattr(self.message, 'cycle_time'):
            property_data.append(("Cycle Time (ms)", str(self.message.cycle_time) if self.message.cycle_time is not None else "N/A"))
            
        if hasattr(self.message, 'senders') and self.message.senders:
            property_data.append(("Senders", ", ".join(self.message.senders)))
            
        if hasattr(self.message, 'bus_name') and self.message.bus_name:
            property_data.append(("Bus Name", self.message.bus_name))
            
        if hasattr(self.message, 'comment') and self.message.comment:
            property_data.append(("Comment", self.message.comment))
        
        # Display all properties in grid
        for label_text, value_text in property_data:
            label = QLabel(f"<b>{label_text}:</b>")
            value = QLabel(value_text)
            props_layout.addWidget(label, row, 0)
            props_layout.addWidget(value, row, 1)
            row += 1
            
        overview_layout.addWidget(props_group)
        overview_layout.addStretch()
        
        # Setup Signals Tab
        signals_layout = QVBoxLayout(signals_tab)
        
        # Create signals table
        signals_table = QTableWidget()
        signals_layout.addWidget(signals_table)
        
        # Configure signals table
        signals_table.setColumnCount(10)
        signals_table.setHorizontalHeaderLabels([
            "Name", "Start Bit", "Length", "Byte Order", "Signed", 
            "Scale", "Offset", "Min", "Max", "Unit"
        ])
        signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        signals_table.horizontalHeader().setStretchLastSection(True)
        
        # Populate signals table
        signals_table.setRowCount(len(self.message.signals))
        for row, signal in enumerate(self.message.signals):
            # Name
            signals_table.setItem(row, 0, QTableWidgetItem(signal.name))
            
            # Start Bit
            signals_table.setItem(row, 1, QTableWidgetItem(str(signal.start)))
            
            # Length
            signals_table.setItem(row, 2, QTableWidgetItem(str(signal.length)))
            
            # Byte Order
            byte_order = getattr(signal, 'byte_order', "Unknown")
            signals_table.setItem(row, 3, QTableWidgetItem(byte_order))
            
            # Signed
            is_signed = getattr(signal, 'is_signed', False)
            signals_table.setItem(row, 4, QTableWidgetItem("Yes" if is_signed else "No"))
            
            # Scale
            scale = getattr(signal, 'scale', 1.0)
            signals_table.setItem(row, 5, QTableWidgetItem(str(scale)))
            
            # Offset
            offset = getattr(signal, 'offset', 0.0)
            signals_table.setItem(row, 6, QTableWidgetItem(str(offset)))
            
            # Min
            minimum = getattr(signal, 'minimum', "N/A")
            signals_table.setItem(row, 7, QTableWidgetItem(str(minimum) if minimum is not None else "N/A"))
            
            # Max
            maximum = getattr(signal, 'maximum', "N/A")
            signals_table.setItem(row, 8, QTableWidgetItem(str(maximum) if maximum is not None else "N/A"))
            
            # Unit
            unit = getattr(signal, 'unit', "")
            signals_table.setItem(row, 9, QTableWidgetItem(unit if unit else ""))
        
        # Make signals table support sorting
        signals_table.setSortingEnabled(True)
            
        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        main_layout.addWidget(close_btn) 