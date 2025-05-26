from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QDialog, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QFont

class DBCRoutingView(QMainWindow):
    def __init__(self, imported_dbc_files=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select DBC Files for Routing")
        self.setMinimumSize(600, 400)
        self.imported_dbc_files = imported_dbc_files or []
        self.parent_window = parent
        self.gateway_node = None  # Store selected gateway node
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        self.title_label = QLabel("Select DBC Files for Routing")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(self.title_label)

        self.dbc_list_widget = QListWidget()
        self.dbc_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        for dbc_file in self.imported_dbc_files:
            item = QListWidgetItem(dbc_file)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.dbc_list_widget.addItem(item)
        layout.addWidget(self.dbc_list_widget)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.select_gateway_button = QPushButton("Select Gateway")
        self.select_gateway_button.setToolTip("Select a gateway node from selected DBC files")
        self.select_gateway_button.clicked.connect(self.select_gateway)
        button_layout.addWidget(self.select_gateway_button)

        # Add Check Messages button
        self.check_messages_button = QPushButton("Check Messages")
        self.check_messages_button.setToolTip("Check messages for routing (feature to be implemented)")
        self.check_messages_button.clicked.connect(self.check_messages)
        button_layout.addWidget(self.check_messages_button)

        # Add Show Topology button
        self.show_topology_button = QPushButton("Show Topology")
        self.show_topology_button.setToolTip("Show network topology (feature to be implemented)")
        self.show_topology_button.clicked.connect(self.show_topology)
        button_layout.addWidget(self.show_topology_button)

        # Add Compare button
        self.compare_button = QPushButton("Compare")
        self.compare_button.setToolTip("Compare selected DBC files")
        self.compare_button.clicked.connect(self.compare_dbc_files)
        button_layout.addWidget(self.compare_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

    def select_gateway(self):
        # Get selected DBC files
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if not selected_files:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least one DBC file to choose a gateway node.")
            return
        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        node_sets = []
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                nodes = handler.get_nodes() if hasattr(handler, 'get_nodes') else []
                node_names = set(node['name'] for node in nodes)
                node_sets.append(node_names)
        if not node_sets:
            QMessageBox.warning(self, "No Nodes Found", "No nodes found in the selected DBC files.")
            return
        # Find intersection (common nodes)
        common_nodes = set.intersection(*node_sets) if node_sets else set()
        if not common_nodes:
            QMessageBox.warning(self, "No Common Nodes", "No common nodes found in all selected DBC files.")
            return
        node_list = sorted(common_nodes)
        gateway, ok = QInputDialog.getItem(self, "Select Gateway Node", "Gateway Node:", node_list, 0, False)
        if ok and gateway:
            self.gateway_node = gateway
            QMessageBox.information(self, "Gateway Selected", f"Gateway node selected: {gateway}")

    def check_messages(self):
        # Ensure a gateway node is selected
        if not self.gateway_node:
            QMessageBox.warning(self, "Select Gateway Node", "Please select a gateway node first.")
            return
        # Get selected DBC files
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files for routing check.")
            return
        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        # Build Rx and Tx maps: {dbc_file: {frame_id: [message_names]}}
        rx_map = {}
        tx_map = {}
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            rx_map[file_name] = {}
            tx_map[file_name] = {}
            if handler:
                messages = handler.get_messages() if hasattr(handler, 'get_messages') else []
                for msg in messages:
                    # Rx: gateway is a receiver
                    if self.gateway_node in msg.get('receivers', []):
                        frame_id = msg['frame_id']
                        if frame_id not in rx_map[file_name]:
                            rx_map[file_name][frame_id] = []
                        rx_map[file_name][frame_id].append(msg['name'])
                    # Tx: gateway is a sender
                    if self.gateway_node in msg.get('senders', []):
                        frame_id = msg['frame_id']
                        if frame_id not in tx_map[file_name]:
                            tx_map[file_name][frame_id] = []
                        tx_map[file_name][frame_id].append(msg['name'])
        # Build sets for all Rx and Tx (frame_id, msg_name, dbc_file)
        rx_entries = set()
        tx_entries = set()
        for rx_file, rx_frames in rx_map.items():
            for frame_id, rx_msgs in rx_frames.items():
                for rx_msg in rx_msgs:
                    rx_entries.add((frame_id, rx_msg, rx_file))
        for tx_file, tx_frames in tx_map.items():
            for frame_id, tx_msgs in tx_frames.items():
                for tx_msg in tx_msgs:
                    tx_entries.add((frame_id, tx_msg, tx_file))
        # Prepare table data
        table_data = []
        # Show every possible Rx/Tx route
        for frame_id, rx_msg, rx_file in sorted(rx_entries):
            found_tx = False
            for tx_file, tx_frames in tx_map.items():
                if tx_file == rx_file:
                    continue
                if frame_id in tx_frames:
                    for tx_msg in tx_frames[frame_id]:
                        # Only show if message name matches as well
                        if tx_msg == rx_msg:
                            table_data.append([f"0x{frame_id:X}", rx_msg, rx_file, tx_file])
                            found_tx = True
            if not found_tx:
                table_data.append([f"0x{frame_id:X}", rx_msg, rx_file, "—"])
        # Also show Tx messages that are not received anywhere else
        for frame_id, tx_msg, tx_file in sorted(tx_entries):
            found_rx = False
            for rx_file, rx_frames in rx_map.items():
                if rx_file == tx_file:
                    continue
                if frame_id in rx_frames and tx_msg in rx_frames[frame_id]:
                    found_rx = True
            if not found_rx:
                table_data.append([f"0x{frame_id:X}", tx_msg, "—", tx_file])
        # Show results in a dialog with QTableWidget
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window)
        dialog.setWindowTitle("Gateway Routing Messages")
        dialog.setMinimumSize(700, 400)
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Frame ID", "Message Name", "Rx DBC", "Tx DBC"])
        table.setRowCount(len(table_data))
        for row, row_data in enumerate(table_data):
            for col, value in enumerate(row_data):
                item = QTableWidgetItem(value)
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)  # Make cells read-only
                table.setItem(row, col, item)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)
        layout.addWidget(table)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.show()

    def show_topology(self):
        # Get selected DBC files
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if not selected_files:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least one DBC file to show topology.")
            return
        if not self.gateway_node:
            QMessageBox.warning(self, "Select Gateway Node", "Please select a gateway node first.")
            return
        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        # Gather nodes for each bus (excluding gateway)
        bus_nodes = {}
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                nodes = handler.get_nodes() if hasattr(handler, 'get_nodes') else []
                node_names = [node['name'] for node in nodes if node['name'] != self.gateway_node]
                bus_nodes[file_name] = node_names
        # Show topology dialog
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window)
        dialog.setWindowTitle("Network Topology")
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)
        topology_widget = TopologyWidget(self.gateway_node, bus_nodes)
        layout.addWidget(topology_widget)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.show()

    def compare_dbc_files(self):
        """
        Compare selected DBC files focusing on messages that are routed through the gateway node.
        Compares message properties for messages with the same message ID.
        """
        # Get selected DBC files
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files to compare.")
            return

        if not self.gateway_node:
            QMessageBox.warning(self, "Select Gateway Node", "Please select a gateway node first.")
            return

        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}

        # Build Rx and Tx maps: {dbc_file: {frame_id: [message_names]}}
        rx_map = {}
        tx_map = {}
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            rx_map[file_name] = {}
            tx_map[file_name] = {}
            if handler:
                messages = handler.get_messages() if hasattr(handler, 'get_messages') else []
                for msg in messages:
                    # Rx: gateway is a receiver
                    if self.gateway_node in msg.get('receivers', []):
                        frame_id = msg['frame_id']
                        if frame_id not in rx_map[file_name]:
                            rx_map[file_name][frame_id] = []
                        rx_map[file_name][frame_id].append(msg)
                    # Tx: gateway is a sender
                    if self.gateway_node in msg.get('senders', []):
                        frame_id = msg['frame_id']
                        if frame_id not in tx_map[file_name]:
                            tx_map[file_name][frame_id] = []
                        tx_map[file_name][frame_id].append(msg)

        # Find messages to compare (messages that are routed through gateway)
        messages_to_compare = []
        for rx_file, rx_frames in rx_map.items():
            for frame_id, rx_msgs in rx_frames.items():
                for rx_msg in rx_msgs:
                    for tx_file, tx_frames in tx_map.items():
                        if tx_file == rx_file:
                            continue
                        if frame_id in tx_frames:
                            for tx_msg in tx_frames[frame_id]:
                                messages_to_compare.append({
                                    'frame_id': frame_id,
                                    'rx_file': rx_file,
                                    'tx_file': tx_file,
                                    'rx_msg': rx_msg,
                                    'tx_msg': tx_msg
                                })

        if not messages_to_compare:
            QMessageBox.information(self, "No Messages to Compare", 
                                  "No routed messages found to compare between the selected DBC files.")
            return

        # Create comparison dialog
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window)
        dialog.setWindowTitle("Message Comparison Results")
        dialog.setMinimumSize(1000, 600)
        layout = QVBoxLayout(dialog)

        # Create table for comparison results
        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels([
            "Frame ID", 
            "Message Name", 
            "Property", 
            "Rx Value", 
            "Tx Value"
        ])

        # Properties to compare
        properties_to_compare = [
            'length',
            'is_extended_frame',
            'is_fd',
            'cycle_time',
            'send_type'
        ]

        # Populate table with comparison results
        row = 0
        for msg_pair in messages_to_compare:
            frame_id = msg_pair['frame_id']
            rx_msg = msg_pair['rx_msg']
            tx_msg = msg_pair['tx_msg']
            
            # Compare each property
            for prop in properties_to_compare:
                rx_value = rx_msg.get(prop, 'N/A')
                tx_value = tx_msg.get(prop, 'N/A')
                
                # Add row to table
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(f"0x{frame_id:X}"))
                table.setItem(row, 1, QTableWidgetItem(rx_msg['name']))
                table.setItem(row, 2, QTableWidgetItem(prop))
                table.setItem(row, 3, QTableWidgetItem(str(rx_value)))
                table.setItem(row, 4, QTableWidgetItem(str(tx_value)))
                
                # Highlight differences
                if rx_value != tx_value:
                    for col in range(5):
                        item = table.item(row, col)
                        item.setBackground(Qt.yellow)
                
                row += 1

            # Compare signals
            rx_signals = {sig['name']: sig for sig in rx_msg.get('signals', [])}
            tx_signals = {sig['name']: sig for sig in tx_msg.get('signals', [])}
            
            # Find common signals
            common_signals = set(rx_signals.keys()) & set(tx_signals.keys())
            
            # Compare signal properties
            signal_properties = [
                'start', 'length', 'byte_order', 'is_signed',
                'scale', 'offset', 'minimum', 'maximum', 'unit'
            ]
            
            for signal_name in common_signals:
                rx_signal = rx_signals[signal_name]
                tx_signal = tx_signals[signal_name]
                
                for prop in signal_properties:
                    rx_value = rx_signal.get(prop, 'N/A')
                    tx_value = tx_signal.get(prop, 'N/A')
                    
                    # Add row to table
                    table.insertRow(row)
                    table.setItem(row, 0, QTableWidgetItem(f"0x{frame_id:X}"))
                    table.setItem(row, 1, QTableWidgetItem(f"{rx_msg['name']}.{signal_name}"))
                    table.setItem(row, 2, QTableWidgetItem(f"signal.{prop}"))
                    table.setItem(row, 3, QTableWidgetItem(str(rx_value)))
                    table.setItem(row, 4, QTableWidgetItem(str(tx_value)))
                    
                    # Highlight differences
                    if rx_value != tx_value:
                        for col in range(5):
                            item = table.item(row, col)
                            item.setBackground(Qt.yellow)
                    
                    row += 1

        # Set table properties
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        layout.addWidget(table)

        # Add close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.show()

class TopologyWidget(QWidget):
    def __init__(self, gateway_node, bus_nodes, parent=None):
        super().__init__(parent)
        self.gateway_node = gateway_node
        self.bus_nodes = bus_nodes  # dict: {bus_name: [node1, node2, ...]}
        self.setMinimumSize(700, 500)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        width = self.width()
        height = self.height()
        margin_top = 60
        margin_bottom = 40
        node_offset = 60  # Horizontal offset for node rectangles from bus line
        node_width = 100
        node_height = 30
        bus_count = len(self.bus_nodes)
        bus_spacing = width // (bus_count + 1)
        # Calculate bus x positions
        bus_xs = [bus_spacing * (i + 1) for i in range(bus_count)]
        # Gateway rectangle spans from first to last bus (with margin)
        gateway_left = bus_xs[0] - 60 if bus_count > 0 else width//2 - 100
        gateway_right = bus_xs[-1] + 60 if bus_count > 0 else width//2 + 100
        gateway_width = gateway_right - gateway_left
        gateway_rect = QRect(gateway_left, 10, gateway_width, 40)
        # Draw gateway node
        painter.setPen(QPen(Qt.black, 2))
        painter.setFont(QFont('Arial', 12, QFont.Bold))
        painter.drawRect(gateway_rect)
        # Draw gateway label centered in the gateway rectangle
        painter.drawText(gateway_rect, Qt.AlignCenter, self.gateway_node)
        # Draw each bus and its nodes
        painter.setFont(QFont('Arial', 10))
        gateway_bottom = gateway_rect.bottom()
        for idx, (bus_name, nodes) in enumerate(self.bus_nodes.items()):
            x = bus_xs[idx]
            # Draw vertical bus line from bottom of gateway to bottom margin (do not cross into gateway)
            painter.drawLine(x, gateway_bottom, x, height - margin_bottom)
            # Draw bus label at the bottom of the line
            painter.drawText(x-50, height - margin_bottom + 10, 100, 20, Qt.AlignCenter, bus_name)
            # Draw nodes offset from bus line
            node_spacing = (height - margin_top - margin_bottom) // (len(nodes)+1) if nodes else 0
            for n_idx, node in enumerate(nodes):
                node_y = margin_top + node_spacing * (n_idx+1)
                node_rect = QRect(x + node_offset, node_y, node_width, node_height)
                painter.drawRect(node_rect)
                painter.drawText(node_rect, Qt.AlignCenter, node)
                # Draw horizontal line from bus to left edge of node rectangle
                painter.drawLine(x, node_y + node_height//2, x + node_offset, node_y + node_height//2) 