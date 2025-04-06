from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTreeWidget, QTreeWidgetItem,
                            QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter, QStackedWidget, QPushButton)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from controller.dbc_io_handler import DBC_IO_Handler
from view.signal_detail_view import SignalDetailView
from view.message_detail_view import MessageDetailView
from view.bus_load_dialog import BusLoadDialog

class DBCDisplayView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_handler = None
        self.bus_load_button = None  # Initialize as None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(5)
        
        # File info section
        self.file_name_label = QLabel()
        self.file_name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.file_name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 2px;
                background-color: #f0f0f0;
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        self.file_name_label.hide()  # Hide label initially
        
        # Add buttons row
        self.buttons_layout = QHBoxLayout()  # Make it instance variable
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.addStretch()
        
        # Add file name label and buttons to layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.file_name_label)
        top_layout.addLayout(self.buttons_layout)
        layout.addLayout(top_layout)
        
        # Create splitter for main content
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Tree view
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setMinimumWidth(200)  # Set minimum width for tree
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QTreeWidget::item {
                height: 25px;
            }
            QTreeWidget::item:hover {
                background-color: #e8e8e8;
            }
            QTreeWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.main_splitter.addWidget(self.tree_widget)
        
        # Create stacked widget for tables
        self.tables_stack = QStackedWidget()
        
        # Signals table
        self.signals_table = QTableWidget()
        self.signals_table.setStyleSheet("""
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
        self.setup_signals_table()
        self.tables_stack.addWidget(self.signals_table)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setStyleSheet(self.signals_table.styleSheet())
        self.setup_messages_table()
        self.tables_stack.addWidget(self.messages_table)
        
        # Nodes table
        self.nodes_table = QTableWidget()
        self.nodes_table.setStyleSheet(self.signals_table.styleSheet())
        self.setup_nodes_table()
        self.tables_stack.addWidget(self.nodes_table)
        
        # Add tables stack to splitter
        self.main_splitter.addWidget(self.tables_stack)
        
        # Set initial sizes (30:70 ratio)
        self.main_splitter.setSizes([300, 700])
        
        layout.addWidget(self.main_splitter)
        
        # Initially hide both tree and tables
        self.main_splitter.hide()

    def setup_signals_table(self):
        """Setup the signals table structure"""
        columns = [
            "Name", "Message", "Message ID", "Start Bit", "Length", "Byte Order",
            "Signed", "Scale", "Offset", "Minimum", "Maximum", "Unit", "Comment", "Receivers"
        ]
        self.signals_table.setColumnCount(len(columns))
        self.signals_table.setHorizontalHeaderLabels(columns)
        header = self.signals_table.horizontalHeader()
        
        # Enable manual column resizing
        self.signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Set stretch for the last column (Receivers) to use remaining space
        header.setStretchLastSection(True)
        
        # Set minimum width for numeric columns
        numeric_columns = ["Start Bit", "Length", "Scale", "Offset", "Minimum", "Maximum"]
        for i, col in enumerate(columns):
            if col in numeric_columns:
                self.signals_table.setColumnWidth(i, 80)
        
        # Connect double-click signal to show signal details
        self.signals_table.itemDoubleClicked.connect(self.on_signal_double_clicked)
        
        self.signals_table.setVisible(False)  # Hide table initially

    def setup_messages_table(self):
        """Setup the messages table structure"""
        columns = [
            "Name", "ID", "Length", "Signals Count", "Senders", "Extended", "CAN FD", 
            "Bus", "Cycle Time", "Send Type", "Comment"
        ]
        self.messages_table.setColumnCount(len(columns))
        self.messages_table.setHorizontalHeaderLabels(columns)
        header = self.messages_table.horizontalHeader()
        
        # Enable manual column resizing for all columns
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column (Comment) to use remaining space
        header.setStretchLastSection(True)
        
        # Set initial widths for columns
        column_widths = {
            "Name": 150,     # Wider for message names
            "ID": 100,      # Wider to fit hex values
            "Length": 80,    # Fixed size for byte length
            "Signals Count": 100,  # Increased to fit content
            "Senders": 150,  # Wider for multiple sender names
            "Extended": 80,  # Yes/No field
            "CAN FD": 80,   # Yes/No field
            "Bus": 100,     # Bus name
            "Cycle Time": 100,  # Cycle time in ms
            "Send Type": 100,  # Send type
            "Comment": 300   # Wide for comments
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            self.messages_table.setColumnWidth(i, column_widths.get(col, 150))
        
        # Connect double-click signal to show message details
        self.messages_table.itemDoubleClicked.connect(self.on_message_double_clicked)
        
        self.messages_table.setVisible(False)  # Hide table initially

    def setup_nodes_table(self):
        """Setup the nodes table structure"""
        columns = [
            "Name", "Tx Messages Count", "Rx Messages Count", "Tx Signals Count", "Rx Signals Count", "Comment"
        ]
        self.nodes_table.setColumnCount(len(columns))
        self.nodes_table.setHorizontalHeaderLabels(columns)
        header = self.nodes_table.horizontalHeader()
        
        # Enable manual column resizing for all columns
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column (Comment) to use remaining space
        header.setStretchLastSection(True)
        
        # Set initial widths for columns
        column_widths = {
            "Name": 150,
            "Tx Messages Count": 120,
            "Rx Messages Count": 120,
            "Tx Signals Count": 120,
            "Rx Signals Count": 120,
            "Comment": 300
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            self.nodes_table.setColumnWidth(i, column_widths.get(col, 150))
        
        self.nodes_table.setVisible(False)  # Hide table initially

    def update_signals_table(self, signals):
        """Update the signals table with data"""
        # Temporarily disable sorting while updating
        self.signals_table.setSortingEnabled(False)
        
        # Clear existing items
        self.signals_table.setRowCount(0)
        self.signals_table.setRowCount(len(signals))
        
        # Store signals data for later use
        self.signals_data = signals
        
        # Prepare all items first
        table_items = []
        for signal in signals:
            row_items = [
                QTableWidgetItem(signal['name']),
                QTableWidgetItem(signal['message_name']),
                QTableWidgetItem(f"0x{signal['message_id']:X}"),
                QTableWidgetItem(str(signal['start'])),
                QTableWidgetItem(str(signal['length'])),
                QTableWidgetItem(signal['byte_order']),
                QTableWidgetItem('Yes' if signal['is_signed'] else 'No'),
                QTableWidgetItem(str(signal['scale'])),
                QTableWidgetItem(str(signal['offset'])),
                QTableWidgetItem(str(signal['minimum']) if signal['minimum'] is not None else ''),
                QTableWidgetItem(str(signal['maximum']) if signal['maximum'] is not None else ''),
                QTableWidgetItem(signal['unit'] if signal['unit'] else ''),
                QTableWidgetItem(signal['comment'] if signal['comment'] else ''),
                QTableWidgetItem(', '.join(signal['receivers']) if signal['receivers'] else '')
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.signals_table.setItem(row, col, item)
        
        # Re-enable sorting
        self.signals_table.setSortingEnabled(True)
        self.signals_table.setVisible(True)
        self.tables_stack.setCurrentWidget(self.signals_table)

    def update_messages_table(self, messages):
        """Update the messages table with data"""
        # Temporarily disable sorting while updating
        self.messages_table.setSortingEnabled(False)
        
        # Clear existing items
        self.messages_table.setRowCount(0)
        self.messages_table.setRowCount(len(messages))
        
        # Store messages data for later use
        self.messages_data = messages
        
        # Prepare all items first
        table_items = []
        for msg in messages:
            # Format cycle time if available
            cycle_time = msg.get('cycle_time')
            cycle_time_str = f"{cycle_time} ms" if cycle_time is not None else ""
            
            row_items = [
                QTableWidgetItem(msg['name']),
                QTableWidgetItem(f"0x{msg['frame_id']:X}"),
                QTableWidgetItem(str(msg['length'])),
                QTableWidgetItem(str(len(msg['signals']))),
                QTableWidgetItem(', '.join(msg['senders']) if msg['senders'] else ''),
                QTableWidgetItem('Yes' if msg.get('is_extended_frame', False) else 'No'),
                QTableWidgetItem('Yes' if msg.get('is_fd', False) else 'No'),
                QTableWidgetItem(msg.get('bus_name', '')),
                QTableWidgetItem(cycle_time_str),
                QTableWidgetItem(msg.get('send_type', '')),
                QTableWidgetItem(msg['comment'] if msg['comment'] else '')
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.messages_table.setItem(row, col, item)
        
        # Re-enable sorting
        self.messages_table.setSortingEnabled(True)
        self.messages_table.setVisible(True)
        self.tables_stack.setCurrentWidget(self.messages_table)

    def update_nodes_table(self, nodes):
        """Update the nodes table with data"""
        # Temporarily disable sorting while updating
        self.nodes_table.setSortingEnabled(False)
        
        # Clear existing items
        self.nodes_table.setRowCount(0)
        self.nodes_table.setRowCount(len(nodes))
        
        # Prepare all items first
        table_items = []
        for node in nodes:
            # Get node messages and signals
            node_messages = self.current_handler.get_node_messages(node['name'])
            node_signals = self.current_handler.get_node_signals(node['name'])
            
            row_items = [
                QTableWidgetItem(node['name']),
                QTableWidgetItem(str(len(node_messages['tx_messages']))),
                QTableWidgetItem(str(len(node_messages['rx_messages']))),
                QTableWidgetItem(str(len(node_signals['tx_signals']))),
                QTableWidgetItem(str(len(node_signals['rx_signals']))),
                QTableWidgetItem(node['comment'] if node['comment'] else '')
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.nodes_table.setItem(row, col, item)
        
        # Re-enable sorting
        self.nodes_table.setSortingEnabled(True)
        self.nodes_table.setVisible(True)
        self.tables_stack.setCurrentWidget(self.nodes_table)

    def on_tree_item_clicked(self, item):
        """Handle tree item clicks"""
        if not self.current_handler:
            return
            
        # Check if the clicked item is the Signals, Messages, or Network Nodes root
        if item.text(0) == "Signals":
            signals = self.current_handler.get_signals()
            self.update_signals_table(signals)
        elif item.text(0) == "Messages":
            messages = self.current_handler.get_messages()
            self.update_messages_table(messages)
        elif item.text(0) == "Network Nodes":
            nodes = self.current_handler.get_nodes()
            self.update_nodes_table(nodes)
        else:
            # Check if this is a signal item by looking at its parent
            parent = item.parent()
            if parent and parent.text(0) in ["Signals", "Tx Signals", "Rx Signals"]:
                # Find the signal data
                signal_name = item.text(0)
                signal_data = None
                
                # If it's under a node's Tx/Rx signals
                if parent.text(0) in ["Tx Signals", "Rx Signals"]:
                    node_item = parent.parent()
                    if node_item:
                        node_name = node_item.text(0)
                        node_signals = self.current_handler.get_node_signals(node_name)
                        # Search in tx_signals or rx_signals based on parent text
                        signals_list = node_signals['tx_signals'] if parent.text(0) == "Tx Signals" else node_signals['rx_signals']
                        for signal in signals_list:
                            if signal['name'] == signal_name:
                                signal_data = signal
                                break
                # If it's under the main Signals root
                elif parent.text(0) == "Signals":
                    # Extract signal name from the text (format: "name (message_name - ID: 0xXX)")
                    signal_name = signal_name.split(" (")[0]
                    signals = self.current_handler.get_signals()
                    for signal in signals:
                        if signal['name'] == signal_name:
                            signal_data = signal
                            break
                # If it's under a message's signals
                elif parent.text(0) == "Signals" and parent.parent():
                    message_item = parent.parent()
                    message_name = message_item.text(0).split(" (ID:")[0]
                    messages = self.current_handler.get_messages()
                    for msg in messages:
                        if msg['name'] == message_name:
                            for signal in msg['signals']:
                                if signal['name'] == signal_name:
                                    # Add message info to signal data
                                    signal_data = signal.copy()
                                    signal_data['message_name'] = msg['name']
                                    signal_data['message_id'] = msg['frame_id']
                                    break
                            break
                
                # Show signal detail view if signal data was found
                if signal_data:
                    signal_detail = SignalDetailView(signal_data, self)
                    signal_detail.show()
            
            # Check if this is a message item
            elif self.is_message_item(item):
                message_data = self.get_message_data_from_item(item)
                if message_data:
                    message_detail = MessageDetailView(message_data, self)
                    message_detail.show()
            else:
                self.signals_table.setVisible(False)
                self.messages_table.setVisible(False)
                self.nodes_table.setVisible(False)
        
    def on_signal_double_clicked(self, item):
        """Handle double-click on a signal in the signals table"""
        if not self.current_handler or not hasattr(self, 'signals_data'):
            return
            
        # Get the row of the clicked item
        row = item.row()
        
        # Get the signal data for this row
        signal_data = self.signals_data[row]
        
        # Show the signal detail view
        signal_detail = SignalDetailView(signal_data, self)
        signal_detail.show()  # Use show() instead of exec_() to allow multiple windows
        
    def on_message_double_clicked(self, item):
        """Handle double-click on a message in the messages table"""
        if not self.current_handler or not hasattr(self, 'messages_data'):
            return
            
        # Get the row of the clicked item
        row = item.row()
        
        # Get the message data for this row
        message_data = self.messages_data[row]
        
        # Show the message detail view
        message_detail = MessageDetailView(message_data, self)
        message_detail.show()  # Use show() to allow multiple windows

    def organize_node_messages(self, node_name: str, messages: list) -> tuple[list, list]:
        """
        Organize messages into Tx and Rx lists for a given node
        
        Args:
            node_name: Name of the node
            messages: List of all messages
            
        Returns:
            tuple[list, list]: (tx_messages, rx_messages)
        """
        tx_messages = []
        rx_messages = []
        
        for msg in messages:
            # Check if node is a sender
            if node_name in msg['senders']:
                tx_messages.append(msg)
            
            # Check if node is a receiver of any signal
            is_receiver = False
            for signal in msg['signals']:
                if node_name in signal['receivers']:
                    is_receiver = True
                    break
            
            if is_receiver:
                rx_messages.append(msg)
                
        return tx_messages, rx_messages

    def add_message_to_tree(self, parent_item: QTreeWidgetItem, message: dict):
        """
        Add a message to the tree under the specified parent
        
        Args:
            parent_item: Parent tree item
            message: Message dictionary
        """
        msg_item = QTreeWidgetItem()
        msg_item.setText(0, f"{message['name']} (ID: 0x{message['frame_id']:X})")
        msg_item.setIcon(0, self.get_message_icon())
        parent_item.addChild(msg_item)

    def add_signal_to_tree(self, parent_item: QTreeWidgetItem, signal: dict):
        """
        Add a signal to the tree under the specified parent
        
        Args:
            parent_item: Parent tree item
            signal: Signal dictionary
        """
        signal_item = QTreeWidgetItem()
        signal_item.setText(0, signal['name'])
        signal_item.setIcon(0, self.get_signal_icon())
        parent_item.addChild(signal_item)

    def update_display(self, handler: DBC_IO_Handler):
        """Update the display with information from the handler"""
        if not handler or not handler.is_valid():
            self.clear_display()
            return
            
        self.current_handler = handler
            
        # Update file name and show the label
        file_info = handler.get_file_info()
        self.file_name_label.setText(f"File: {file_info['file_name']}")
        self.file_name_label.show()
        
        # Add bus load calculator button
        if not self.bus_load_button:
            self.bus_load_button = QPushButton("Bus Load Calculator")
            self.bus_load_button.setToolTip("Calculate CAN bus load based on message properties")
            self.bus_load_button.clicked.connect(self.show_bus_load_calculator)
            # Insert before the stretch
            self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, self.bus_load_button)
        
        # Show the main splitter when file is loaded
        self.main_splitter.show()
        
        # Update tree
        self.tree_widget.clear()
        
        # Create root items
        nodes_root = QTreeWidgetItem(self.tree_widget)
        nodes_root.setText(0, "Network Nodes")
        nodes_root.setExpanded(False)
        
        messages_root = QTreeWidgetItem(self.tree_widget)
        messages_root.setText(0, "Messages")
        messages_root.setExpanded(False)
        
        signals_root = QTreeWidgetItem(self.tree_widget)
        signals_root.setText(0, "Signals")
        signals_root.setExpanded(False)
        
        # Get all nodes
        nodes = handler.get_nodes()
        
        # Add nodes with their messages and signals
        for node in nodes:
            node_item = QTreeWidgetItem()
            node_item.setText(0, node['name'])
            if node['comment']:
                node_item.setToolTip(0, node['comment'])
            node_item.setIcon(0, self.get_node_icon())
            nodes_root.addChild(node_item)
            
            # Get messages and signals for this node from handler
            node_messages = handler.get_node_messages(node['name'])
            node_signals = handler.get_node_signals(node['name'])
            
            # Add Tx Messages group
            tx_messages_group = QTreeWidgetItem()
            tx_messages_group.setText(0, "Tx Messages")
            node_item.addChild(tx_messages_group)
            for msg in node_messages['tx_messages']:
                self.add_message_to_tree(tx_messages_group, msg)
            
            # Add Rx Messages group
            rx_messages_group = QTreeWidgetItem()
            rx_messages_group.setText(0, "Rx Messages")
            node_item.addChild(rx_messages_group)
            for msg in node_messages['rx_messages']:
                self.add_message_to_tree(rx_messages_group, msg)
            
            # Add Tx Signals group
            tx_signals_group = QTreeWidgetItem()
            tx_signals_group.setText(0, "Tx Signals")
            node_item.addChild(tx_signals_group)
            for signal in node_signals['tx_signals']:
                self.add_signal_to_tree(tx_signals_group, signal)
            
            # Add Rx Signals group
            rx_signals_group = QTreeWidgetItem()
            rx_signals_group.setText(0, "Rx Signals")
            node_item.addChild(rx_signals_group)
            for signal in node_signals['rx_signals']:
                self.add_signal_to_tree(rx_signals_group, signal)

        # Add messages to Messages root
        messages = handler.get_messages()
        for msg in messages:
            msg_item = QTreeWidgetItem()
            msg_item.setText(0, f"{msg['name']} (ID: 0x{msg['frame_id']:X})")
            msg_item.setIcon(0, self.get_message_icon())
            messages_root.addChild(msg_item)
            
            # Add message details as child items
            details_item = QTreeWidgetItem()
            details_item.setText(0, f"Length: {msg['length']} bytes")
            msg_item.addChild(details_item)
            
            if msg['comment']:
                comment_item = QTreeWidgetItem()
                comment_item.setText(0, f"Comment: {msg['comment']}")
                msg_item.addChild(comment_item)
                
            if msg['senders']:
                senders_item = QTreeWidgetItem()
                senders_item.setText(0, f"Senders: {', '.join(msg['senders'])}")
                msg_item.addChild(senders_item)
            
            # Add signals group under message
            if msg['signals']:
                signals_item = QTreeWidgetItem()
                signals_item.setText(0, "Signals")
                msg_item.addChild(signals_item)
                
                # Add each signal with its details
                for signal in msg['signals']:
                    signal_item = QTreeWidgetItem()
                    signal_item.setText(0, signal['name'])
                    signal_item.setIcon(0, self.get_signal_icon())
                    signals_item.addChild(signal_item)
                    
                    # Add signal details as child items
                    signal_details = [
                        f"Start bit: {signal['start']}",
                        f"Length: {signal['length']} bits",
                        f"Byte order: {signal['byte_order']}",
                        f"Signed: {'Yes' if signal['is_signed'] else 'No'}",
                        f"Scale: {signal['scale']}",
                        f"Offset: {signal['offset']}"
                    ]
                    
                    # Add optional signal details if they exist
                    if signal['minimum'] is not None:
                        signal_details.append(f"Minimum: {signal['minimum']}")
                    if signal['maximum'] is not None:
                        signal_details.append(f"Maximum: {signal['maximum']}")
                    if signal['unit']:
                        signal_details.append(f"Unit: {signal['unit']}")
                    if signal['comment']:
                        signal_details.append(f"Comment: {signal['comment']}")
                    if signal['receivers']:
                        signal_details.append(f"Receivers: {', '.join(signal['receivers'])}")
                    
                    # Add all details as child items
                    for detail in signal_details:
                        detail_item = QTreeWidgetItem()
                        detail_item.setText(0, detail)
                        signal_item.addChild(detail_item)
        
        # Add signals to Signals root
        signals = handler.get_signals()
        for signal in signals:
            signal_item = QTreeWidgetItem()
            signal_item.setText(0, f"{signal['name']} ({signal['message_name']} - ID: 0x{signal['message_id']:X})")
            signal_item.setIcon(0, self.get_signal_icon())
            signals_root.addChild(signal_item)
            
            # Add signal details as child items
            signal_details = [
                f"Start bit: {signal['start']}",
                f"Length: {signal['length']} bits",
                f"Byte order: {signal['byte_order']}",
                f"Signed: {'Yes' if signal['is_signed'] else 'No'}",
                f"Scale: {signal['scale']}",
                f"Offset: {signal['offset']}"
            ]
            
            # Add optional signal details if they exist
            if signal['minimum'] is not None:
                signal_details.append(f"Minimum: {signal['minimum']}")
            if signal['maximum'] is not None:
                signal_details.append(f"Maximum: {signal['maximum']}")
            if signal['unit']:
                signal_details.append(f"Unit: {signal['unit']}")
            if signal['comment']:
                signal_details.append(f"Comment: {signal['comment']}")
            if signal['receivers']:
                signal_details.append(f"Receivers: {', '.join(signal['receivers'])}")
            
            # Add all details as child items
            for detail in signal_details:
                detail_item = QTreeWidgetItem()
                detail_item.setText(0, detail)
                signal_item.addChild(detail_item)
            
    def get_node_icon(self):
        """Returns a default icon for nodes"""
        return QIcon()
        
    def get_message_icon(self):
        """Returns a default icon for messages"""
        return QIcon()
        
    def get_signal_icon(self):
        """Returns a default icon for signals"""
        return QIcon()
            
    def clear_display(self):
        """Clear all displayed information"""
        self.file_name_label.hide()  # Hide the label instead of setting text
        self.tree_widget.clear()
        self.signals_table.setVisible(False)
        self.messages_table.setVisible(False)
        self.nodes_table.setVisible(False)
        self.main_splitter.hide()
        self.current_handler = None
        
        # Remove bus load calculator button if it exists
        if self.bus_load_button:
            self.bus_load_button.setParent(None)  # Remove from layout
            self.bus_load_button = None

    def is_message_item(self, item):
        """Check if the tree item represents a message"""
        # Check if item text contains "(ID:" which is our message format
        if "(ID:" in item.text(0):
            # Make sure it's not under a Signals parent (which also shows message ID)
            parent = item.parent()
            if parent and parent.text(0) == "Messages":
                return True
            # Check if it's under Tx/Rx Messages in a node
            if parent and parent.text(0) in ["Tx Messages", "Rx Messages"]:
                return True
        return False
        
    def get_message_data_from_item(self, item):
        """Get message data from a tree item"""
        # Extract message name from the item text (format: "name (ID: 0xXX)")
        message_name = item.text(0).split(" (ID:")[0]
        
        # If it's under a node's Tx/Rx messages
        parent = item.parent()
        if parent and parent.text(0) in ["Tx Messages", "Rx Messages"]:
            node_item = parent.parent()
            if node_item:
                node_name = node_item.text(0)
                node_messages = self.current_handler.get_node_messages(node_name)
                # Search in tx_messages or rx_messages based on parent text
                messages_list = node_messages['tx_messages'] if parent.text(0) == "Tx Messages" else node_messages['rx_messages']
                for msg in messages_list:
                    if msg['name'] == message_name:
                        return msg
        
        # If it's under the main Messages root or anywhere else
        messages = self.current_handler.get_messages()
        for msg in messages:
            if msg['name'] == message_name:
                return msg
                
        return None

    def show_bus_load_calculator(self):
        """Show the bus load calculator dialog."""
        if not self.current_handler or not self.current_handler.is_valid():
            return
            
        # Get messages from the handler
        messages = self.current_handler.get_messages()
        
        # Create and show the dialog
        dialog = BusLoadDialog(messages, self)
        dialog.exec_() 