from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFrame, QSizePolicy,
                            QStackedWidget, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from .signal_detail_view import SignalDetailView
from .message_detail_view import MessageDetailView

class NodeDetailView(QDialog):
    def __init__(self, node_data, node_messages, node_signals, parent=None):
        super().__init__(parent)
        self.node_data = node_data
        self.node_messages = node_messages  # Contains tx_messages and rx_messages
        self.node_signals = node_signals    # Contains tx_signals and rx_signals
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Node Details: {self.node_data['name']}")
        self.setMinimumSize(800, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with node name
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        node_name_label = QLabel(self.node_data['name'])
        node_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(node_name_label)
        
        # Add node statistics
        tx_messages_count = len(self.node_messages['tx_messages'])
        rx_messages_count = len(self.node_messages['rx_messages'])
        tx_signals_count = len(self.node_signals['tx_signals'])
        rx_signals_count = len(self.node_signals['rx_signals'])
        
        stats_label = QLabel(f"Tx Messages: {tx_messages_count} | Rx Messages: {rx_messages_count} | Tx Signals: {tx_signals_count} | Rx Signals: {rx_signals_count}")
        stats_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(stats_label)
        
        header_layout.addStretch()
        
        main_layout.addWidget(header_frame)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add Details tab
        details_tab = self.create_details_tab()
        tab_widget.addTab(details_tab, "Details")
        
        # Add Messages tab
        messages_tab = self.create_messages_tab()
        tab_widget.addTab(messages_tab, "Messages")
        
        # Add Signals tab
        signals_tab = self.create_signals_tab()
        tab_widget.addTab(signals_tab, "Signals")
        
        main_layout.addWidget(tab_widget)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_details_tab(self):
        """Create the details tab with node properties"""
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
        
        # Define property groups and their items
        property_groups = [
            ("Basic Properties", [
                ("Name", self.node_data['name']),
                ("Comment", format_value(self.node_data.get('comment')))
            ]),
            ("Message Statistics", [
                ("Tx Messages Count", len(self.node_messages['tx_messages'])),
                ("Rx Messages Count", len(self.node_messages['rx_messages'])),
                ("Tx Signals Count", len(self.node_signals['tx_signals'])),
                ("Rx Signals Count", len(self.node_signals['rx_signals']))
            ]),
            ("J1939 Properties", [
                ("Address", format_value(self.node_data.get('address'))),
                ("Function Name", format_value(self.node_data.get('function_name'))),
                ("Manufacturer Code", format_value(self.node_data.get('manufacturer_code'))),
                ("Identity Number", format_value(self.node_data.get('identity_number'))),
                ("Industry Group", format_value(self.node_data.get('industry_group'))),
                ("Vehicle System", format_value(self.node_data.get('vehicle_system'))),
                ("Vehicle System Instance", format_value(self.node_data.get('vehicle_system_instance'))),
                ("Function", format_value(self.node_data.get('function'))),
                ("Function Instance", format_value(self.node_data.get('function_instance'))),
                ("ECU Instance", format_value(self.node_data.get('ecu_instance'))),
                ("Manufacturer Ext", format_value(self.node_data.get('manufacturer_ext'))),
                ("ECU Ext Reference", format_value(self.node_data.get('ecu_ext_ref'))),
                ("Is J1939", format_value(self.node_data.get('is_j1939', False)))
            ])
        ]
        
        # DBC Specifics if available
        dbc_specifics = self.node_data.get('dbc_specifics')
        if dbc_specifics and isinstance(dbc_specifics, dict):
            dbc_properties = []
            for key, value in dbc_specifics.items():
                dbc_properties.append((key, format_value(value)))
            property_groups.append(("DBC Specifics", dbc_properties))
        
        # AUTOSAR Specifics if available
        autosar_specifics = self.node_data.get('autosar_specifics')
        if autosar_specifics and isinstance(autosar_specifics, dict):
            autosar_properties = []
            for key, value in autosar_specifics.items():
                autosar_properties.append((key, format_value(value)))
            property_groups.append(("AUTOSAR Specifics", autosar_properties))
        
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
        
        scroll_area.setWidget(table)
        return scroll_area
        
    def create_messages_tab(self):
        """Create the messages tab with Tx and Rx messages"""
        tab_widget = QTabWidget()
        
        # Create Tx Messages tab
        tx_tab = self.create_message_list_tab(self.node_messages['tx_messages'], "Tx")
        tab_widget.addTab(tx_tab, f"Tx Messages ({len(self.node_messages['tx_messages'])})")
        
        # Create Rx Messages tab
        rx_tab = self.create_message_list_tab(self.node_messages['rx_messages'], "Rx")
        tab_widget.addTab(rx_tab, f"Rx Messages ({len(self.node_messages['rx_messages'])})")
        
        return tab_widget
        
    def create_message_list_tab(self, messages, direction):
        """Create a tab with a list of messages"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        table = QTableWidget()
        columns = ["Name", "ID", "Length", "Signals Count", "Cycle Time", "Send Type", "Comment"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        # Set column properties
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
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
        
        # Set column widths
        column_widths = {
            "Name": 200,
            "ID": 100,
            "Length": 80,
            "Signals Count": 100,
            "Cycle Time": 100,
            "Send Type": 100,
            "Comment": 300
        }
        
        for i, col in enumerate(columns):
            table.setColumnWidth(i, column_widths.get(col, 100))
        
        # Add messages
        table.setRowCount(len(messages))
        
        for row, msg in enumerate(messages):
            # Create items for each column
            name_item = QTableWidgetItem(msg['name'])
            id_item = QTableWidgetItem(f"0x{msg['frame_id']:X}")
            length_item = QTableWidgetItem(str(msg['length']))
            signals_count_item = QTableWidgetItem(str(len(msg['signals'])))
            
            cycle_time = msg.get('cycle_time')
            cycle_time_item = QTableWidgetItem(f"{cycle_time} ms" if cycle_time is not None else "")
            
            send_type_item = QTableWidgetItem(msg.get('send_type', ''))
            comment_item = QTableWidgetItem(msg.get('comment', ''))
            
            # Add items to the table
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, id_item)
            table.setItem(row, 2, length_item)
            table.setItem(row, 3, signals_count_item)
            table.setItem(row, 4, cycle_time_item)
            table.setItem(row, 5, send_type_item)
            table.setItem(row, 6, comment_item)
        
        # Connect double-click handler to open message details
        table.itemDoubleClicked.connect(lambda item: self.show_message_details(messages[item.row()]))
        
        scroll_area.setWidget(table)
        return scroll_area
        
    def create_signals_tab(self):
        """Create the signals tab with Tx and Rx signals"""
        tab_widget = QTabWidget()
        
        # Create Tx Signals tab
        tx_tab = self.create_signal_list_tab(self.node_signals['tx_signals'], "Tx")
        tab_widget.addTab(tx_tab, f"Tx Signals ({len(self.node_signals['tx_signals'])})")
        
        # Create Rx Signals tab
        rx_tab = self.create_signal_list_tab(self.node_signals['rx_signals'], "Rx")
        tab_widget.addTab(rx_tab, f"Rx Signals ({len(self.node_signals['rx_signals'])})")
        
        return tab_widget
        
    def create_signal_list_tab(self, signals, direction):
        """Create a tab with a list of signals"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        table = QTableWidget()
        columns = ["Name", "Message", "Start Bit", "Length", "Byte Order", "Scale", "Offset", "Unit", "Comment"]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        # Set column properties
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Interactive)
        header.setStretchLastSection(True)
        
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
        
        # Set column widths
        column_widths = {
            "Name": 150,
            "Message": 200,
            "Start Bit": 80,
            "Length": 80,
            "Byte Order": 100,
            "Scale": 80,
            "Offset": 80,
            "Unit": 80,
            "Comment": 200
        }
        
        for i, col in enumerate(columns):
            table.setColumnWidth(i, column_widths.get(col, 100))
        
        # Add signals
        table.setRowCount(len(signals))
        
        for row, signal in enumerate(signals):
            # Create items for each column
            name_item = QTableWidgetItem(signal['name'])
            message_item = QTableWidgetItem(signal['message_name'])
            start_bit_item = QTableWidgetItem(str(signal['start']))
            length_item = QTableWidgetItem(str(signal['length']))
            byte_order_item = QTableWidgetItem(signal['byte_order'])
            scale_item = QTableWidgetItem(str(signal['scale']))
            offset_item = QTableWidgetItem(str(signal['offset']))
            unit_item = QTableWidgetItem(signal.get('unit', ''))
            comment_item = QTableWidgetItem(signal.get('comment', ''))
            
            # Add items to the table
            table.setItem(row, 0, name_item)
            table.setItem(row, 1, message_item)
            table.setItem(row, 2, start_bit_item)
            table.setItem(row, 3, length_item)
            table.setItem(row, 4, byte_order_item)
            table.setItem(row, 5, scale_item)
            table.setItem(row, 6, offset_item)
            table.setItem(row, 7, unit_item)
            table.setItem(row, 8, comment_item)
        
        # Connect double-click handler to open signal details
        table.itemDoubleClicked.connect(lambda item: self.show_signal_details(signals[item.row()]))
        
        scroll_area.setWidget(table)
        return scroll_area
        
    def show_message_details(self, message):
        """Show details for a message"""
        message_detail = MessageDetailView(message, self)
        message_detail.show()
        
    def show_signal_details(self, signal):
        """Show details for a signal"""
        signal_detail = SignalDetailView(signal, self)
        signal_detail.show() 