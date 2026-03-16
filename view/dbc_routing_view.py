from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox, QDialog, QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView, QTreeWidget, QTreeWidgetItem, QFileDialog
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

    def highlight_empty_routing_nodes(self, row_item, file_msgs, all_dbc_files, node_type, start_col=2):
        for idx, file in enumerate(all_dbc_files):
            msg = file_msgs[file]
            col = start_col + idx
            if msg is not None and not msg.get(node_type, []):
                row_item.setBackground(col, Qt.yellow)

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

        # Get handlers and raw cantools database objects from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        db_map = {handler.get_file_info()['file_name']: handler.get_database() for handler in handlers}

        # Build Rx and Tx maps: {dbc_file: {frame_id: [message_objs]}}
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

        # Collect all unique frame_ids from Rx and Tx
        all_frame_ids = set()
        for rx_frames in rx_map.values():
            all_frame_ids.update(rx_frames.keys())
        for tx_frames in tx_map.values():
            all_frame_ids.update(tx_frames.keys())

        # Prepare dialog
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window)
        dialog.setWindowTitle("Message Comparison Results")
        dialog.setMinimumSize(1000, 600)
        layout = QVBoxLayout(dialog)

        # Set up tree columns: Frame ID, Property, then one column per DBC file for message names
        tree = QTreeWidget()
        tree.setColumnCount(2 + len(selected_files))
        tree.setHeaderLabels(["Frame ID", "Property"] + selected_files)
        tree.setAlternatingRowColors(True)
        tree.setRootIsDecorated(True)

        for frame_id in sorted(all_frame_ids):
            # For each DBC file, get the message name for this frame_id (if any)
            msg_names = []
            file_msgs = {}
            for file in selected_files:
                msg = None
                # Prefer Rx, then Tx
                rx_msgs = rx_map[file].get(frame_id, [])
                tx_msgs = tx_map[file].get(frame_id, [])
                if rx_msgs:
                    msg = rx_msgs[0]
                elif tx_msgs:
                    msg = tx_msgs[0]
                file_msgs[file] = msg
                msg_names.append(msg['name'] if msg else "")
            # Top-level: frame id row with message names
            msg_item = QTreeWidgetItem([f"0x{frame_id:X}", ""] + msg_names)
            tree.addTopLevelItem(msg_item)

            # Gateway role row
            gateway_roles = []
            rx_count = 0
            tx_count = 0
            for file in selected_files:
                msg = file_msgs[file]
                if msg:
                    is_rx = self.gateway_node in msg.get('receivers', [])
                    is_tx = self.gateway_node in msg.get('senders', [])
                    if is_rx and is_tx:
                        role = "Rx/Tx"
                    elif is_rx:
                        role = "Rx"
                    elif is_tx:
                        role = "Tx"
                    else:
                        role = "--"
                else:
                    role = "--"
                if role in ("Rx", "Rx/Tx"):
                    rx_count += 1
                if role in ("Tx", "Rx/Tx"):
                    tx_count += 1
                gateway_roles.append(role)
            gateway_role_item = QTreeWidgetItem(['', 'gateway_role', *gateway_roles])
            # Highlight only for error conditions:
            highlight_error = False
            if rx_count > 1:
                highlight_error = True
            elif rx_count > 0 and tx_count == 0:
                highlight_error = True
            elif tx_count > 0 and rx_count == 0:
                highlight_error = True
            if highlight_error:
                for col in range(2, 2 + len(selected_files)):
                    gateway_role_item.setBackground(col, Qt.yellow)
            msg_item.addChild(gateway_role_item)

            # Add Rx nodes row
            rx_nodes_values = []
            for file in selected_files:
                msg = file_msgs[file]
                if msg and 'receivers' in msg:
                    rx_nodes = msg['receivers']
                    rx_nodes_str = ', '.join(rx_nodes) if rx_nodes else '--'
                else:
                    rx_nodes_str = '--'
                rx_nodes_values.append(rx_nodes_str)
            rx_nodes_item = QTreeWidgetItem(['', 'rx_nodes', *rx_nodes_values])
            # Highlight if gateway transmits but no receivers (routing issue)
            for idx, file in enumerate(selected_files):
                msg = file_msgs[file]
                gateway_role = gateway_roles[idx]
                rx_nodes_str = rx_nodes_values[idx]
                # Highlight if gateway is Tx/Rx/Tx but no receivers
                if gateway_role in ('Tx', 'Rx/Tx') and rx_nodes_str == '--':
                    rx_nodes_item.setBackground(idx + 2, Qt.yellow)
            msg_item.addChild(rx_nodes_item)

            # Add Tx nodes row
            tx_nodes_values = []
            for file in selected_files:
                msg = file_msgs[file]
                if msg and 'senders' in msg:
                    tx_nodes = msg['senders']
                    tx_nodes_str = ', '.join(tx_nodes) if tx_nodes else '--'
                else:
                    tx_nodes_str = '--'
                tx_nodes_values.append(tx_nodes_str)
            tx_nodes_item = QTreeWidgetItem(['', 'tx_nodes', *tx_nodes_values])
            msg_item.addChild(tx_nodes_item)

            # List of properties to compare
            properties_to_compare = [
                'name',  # Show message name as the first property
                'length',
                'is_extended_frame',
                'is_fd',
                'frame_format',
                'cycle_time',
                'send_type'
            ]

            # For each property, collect values from each DBC file
            for prop in properties_to_compare:
                values = []
                compare_values = []
                for idx, file in enumerate(selected_files):
                    msg = file_msgs[file]
                    gateway_role = gateway_roles[idx]
                    if prop == 'name':
                        val = msg['name'] if msg else '--'
                    else:
                        val = msg.get(prop, '--') if msg else '--'
                    values.append(str(val))
                    # Only include in comparison if gateway role is not '--'
                    if gateway_role != '--':
                        compare_values.append(str(val))
                prop_item = QTreeWidgetItem(['', prop, *values])
                # Highlight only if there are differences among non-empty gateway roles
                if prop != 'name' and len(set(compare_values)) > 1:
                    for idx, gateway_role in enumerate(gateway_roles):
                        col = idx + 2
                        if gateway_role != '--':
                            prop_item.setBackground(col, Qt.yellow)
                msg_item.addChild(prop_item)

            # --- Signal comparison by (start, length) ---
            # 1. Collect all unique (start, length) pairs for signals in this message
            all_signal_positions = set();
            signal_map_per_file = [{} for _ in selected_files]  # List of dicts: { (start, length): signal_obj }
            for idx, file in enumerate(selected_files):
                msg = file_msgs[file]
                if msg and 'signals' in msg:
                    for sig in msg['signals']:
                        key = (sig.get('start'), sig.get('length'))
                        all_signal_positions.add(key)
                        signal_map_per_file[idx][key] = sig

            signal_properties = [
                'name', 'byte_order', 'is_signed', 'scale', 'offset', 'minimum', 'maximum', 'unit'
            ]

            for start_length in sorted(all_signal_positions):
                # Gather signal names for each file at this position
                sig_names = []
                gateway_roles_for_signal = []
                for idx, file in enumerate(selected_files):
                    sig = signal_map_per_file[idx].get(start_length)
                    sig_names.append(sig['name'] if sig else '--')
                    gateway_roles_for_signal.append(gateway_roles[idx])
                # Top-level: signal row
                sig_item = QTreeWidgetItem(['', f"Signal: {start_length[0]}:{start_length[1]}", *sig_names])
                msg_item.addChild(sig_item)
                
                # Track if any signal property differs for this signal
                signal_has_differences = False
                cols_with_differences = set()
                
                # For each property, compare values for DBC files where gateway role is not '--'
                for prop in signal_properties:
                    values = []
                    compare_values = []
                    for idx in range(len(selected_files)):
                        sig = signal_map_per_file[idx].get(start_length)
                        val = sig.get(prop, '--') if sig else '--'
                        values.append(str(val))
                        if gateway_roles_for_signal[idx] != '--':
                            compare_values.append(str(val))
                    prop_row = QTreeWidgetItem(['', prop, *values])
                    # Highlight only if there are differences among non-empty gateway roles
                    if prop != 'name' and len(set(compare_values)) > 1:
                        signal_has_differences = True
                        for idx, gateway_role in enumerate(gateway_roles_for_signal):
                            col = idx + 2
                            if gateway_role != '--':
                                prop_row.setBackground(col, Qt.yellow)
                                cols_with_differences.add(col)
                    sig_item.addChild(prop_row)
                
                # Highlight the signal row itself if any property differs
                if signal_has_differences:
                    for col in cols_with_differences:
                        sig_item.setBackground(col, Qt.yellow)

                # --- Value Table Comparison ---
                all_value_keys = set()
                value_tables_per_file = {}
                for idx, file in enumerate(selected_files):
                    sig_dict = signal_map_per_file[idx].get(start_length)
                    if not sig_dict:
                        continue
                    sig_name = sig_dict['name']
                    db = db_map.get(file)
                    if db:
                        try:
                            message = db.get_message_by_frame_id(frame_id)
                            raw_signal = message.get_signal_by_name(sig_name)
                            if raw_signal and raw_signal.choices:
                                value_tables_per_file[file] = raw_signal.choices
                                all_value_keys.update(raw_signal.choices.keys())
                        except KeyError:
                            pass # Message or signal not in this DB
                
                if all_value_keys:
                    value_table_header = QTreeWidgetItem(['', 'value_table', ''])
                    sig_item.addChild(value_table_header)
                    for value_key in sorted(all_value_keys):
                        descriptions = []
                        compare_values = []
                        for idx, file in enumerate(selected_files):
                            choices = value_tables_per_file.get(file)
                            description = choices.get(value_key, '--') if choices else '--'
                            descriptions.append(str(description))
                            if gateway_roles_for_signal[idx] != '--':
                                compare_values.append(str(description))

                        prop_row = QTreeWidgetItem(['', f"  {value_key}", *descriptions])
                        if len(set(compare_values)) > 1:
                            for idx, gateway_role in enumerate(gateway_roles_for_signal):
                                col = idx + 2
                                if gateway_role != '--':
                                    prop_row.setBackground(col, Qt.yellow)
                        value_table_header.addChild(prop_row)

            # After all child rows are added to msg_item
            has_yellow = False
            for i in range(msg_item.childCount()):
                child = msg_item.child(i)
                for col in range(2, 2 + len(selected_files)):
                    brush = child.background(col)
                    if hasattr(brush, 'color') and brush.color().name().lower() in ['#ffff00', '#ff0']:
                        has_yellow = True
                        break
                if has_yellow:
                    break
            if has_yellow:
                msg_item.setBackground(0, Qt.yellow)

        layout.addWidget(tree)

        # Add export and close buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton("Export to CSV")

        def export_tree_to_csv():
            path, _ = QFileDialog.getSaveFileName(dialog, "Export Comparison to CSV", "", "CSV Files (*.csv)")
            if not path:
                return

            try:
                import csv
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Write header
                    header = ["Frame ID / Property"] + selected_files
                    writer.writerow(header)

                    # Recursive function to write items
                    def write_item(item, indent_level=0):
                        row_data = []
                        # Indent the property name
                        prop_name = "  " * indent_level + item.text(1)
                        # For top-level items, Frame ID is in the first column, property is empty
                        if indent_level == 0:
                            row_data.append(item.text(0))
                        else:
                            # For child items, the first column is empty
                            row_data.append("")
                        
                        row_data.append(prop_name)
                        
                        # Add the rest of the columns
                        for col in range(2, tree.columnCount()):
                            row_data.append(item.text(col))
                        writer.writerow(row_data)

                        # Recursively write children
                        for i in range(item.childCount()):
                            write_item(item.child(i), indent_level + 1)

                    # Start writing from top-level items
                    for i in range(tree.topLevelItemCount()):
                        write_item(tree.topLevelItem(i))

                QMessageBox.information(dialog, "Success", f"Comparison data successfully exported to:\n{path}")
            except Exception as e:
                QMessageBox.critical(dialog, "Error", f"Failed to export CSV file: {e}")

        export_btn.clicked.connect(export_tree_to_csv)
        button_layout.addWidget(export_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)

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