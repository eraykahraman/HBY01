from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QPushButton, QHBoxLayout, QMessageBox, QTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView, QDialog
from PyQt5.QtCore import Qt

class DBCCompatibilityView(QMainWindow):
    def __init__(self, imported_dbc_files=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DBC Files Compatibility Analysis")
        self.setMinimumSize(1000, 700)
        self.imported_dbc_files = imported_dbc_files or []
        self.parent_window = parent
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title
        self.title_label = QLabel("DBC Files Compatibility Analysis")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 18px; margin: 10px;")
        layout.addWidget(self.title_label)

        # File selection section
        file_section = QWidget()
        file_layout = QVBoxLayout(file_section)
        
        file_label = QLabel("Select DBC Files for Compatibility Analysis:")
        file_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        file_layout.addWidget(file_label)

        self.dbc_list_widget = QListWidget()
        self.dbc_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dbc_list_widget.setMinimumHeight(150)
        for dbc_file in self.imported_dbc_files:
            item = QListWidgetItem(dbc_file)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.dbc_list_widget.addItem(item)
        file_layout.addWidget(self.dbc_list_widget)
        
        layout.addWidget(file_section)

        # Analysis buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Add Select ECU button (to the left of Analyze Compatibility)
        self.select_ecu_button = QPushButton("Select ECU")
        self.select_ecu_button.setToolTip("Select a common ECU (node) present in all selected DBC files")
        self.select_ecu_button.clicked.connect(self.select_ecu)
        button_layout.addWidget(self.select_ecu_button)

        self.export_button = QPushButton("Export Results")
        self.export_button.setToolTip("Export compatibility analysis results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)

        # Add Detailed ECU Comparison button
        self.detailed_compare_button = QPushButton("Detailed ECU Comparison")
        self.detailed_compare_button.setToolTip("Show detailed field-by-field comparison for selected ECU across DBC files")
        self.detailed_compare_button.clicked.connect(self.show_detailed_ecu_comparison)
        button_layout.insertWidget(2, self.detailed_compare_button)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        # Results section
        results_section = QWidget()
        results_layout = QVBoxLayout(results_section)
        
        results_label = QLabel("Compatibility Analysis Results:")
        results_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        results_layout.addWidget(results_label)

        # Create tab widget for different analysis views
        self.tab_widget = QTabWidget()
        
        # Summary tab
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.tab_widget.addTab(self.summary_text, "Summary")
        
        # Conflicts tab
        self.conflicts_text = QTextEdit()
        self.conflicts_text.setReadOnly(True)
        self.tab_widget.addTab(self.conflicts_text, "Conflicts")
        
        # Details tab
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.tab_widget.addTab(self.details_text, "Detailed Analysis")
        
        # Rx/Tx Presence tab
        self.presence_table_widget = None  # Will be created on demand
        self.tab_widget.addTab(QWidget(), "ECU Message Presence")
        
        results_layout.addWidget(self.tab_widget)
        layout.addWidget(results_section)

        # Initially hide results section
        results_section.setVisible(False)
        self.results_section = results_section

    def export_results(self):
        # TODO: Implement export functionality
        QMessageBox.information(self, "Export Results", "Export functionality will be implemented here.")

    def select_ecu(self):
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files to select a common ECU.")
            return
        # Traverse up to main window to access dbc_controller
        main_window = self.parent_window.parent_window if hasattr(self.parent_window, 'parent_window') else None
        if main_window is None or not hasattr(main_window, 'dbc_controller'):
            QMessageBox.warning(self, "Error", "Cannot access DBC controller from main window.")
            return
        handlers = main_window.dbc_controller.get_all_handlers()
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
            QMessageBox.warning(self, "No Common ECUs", "No common ECUs (nodes) found in all selected DBC files.")
            return
        node_list = sorted(common_nodes)
        from PyQt5.QtWidgets import QInputDialog
        ecu, ok = QInputDialog.getItem(self, "Select ECU (Node)", "ECU (Node):", node_list, 0, False)
        if ok and ecu:
            self.selected_ecu = ecu
            QMessageBox.information(self, "ECU Selected", f"Selected ECU: {ecu}")
        else:
            self.selected_ecu = None

    def show_ecu_message_presence_dialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QPushButton
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files.")
            return
        # Traverse up to main window to access dbc_controller
        main_window = self.parent_window.parent_window if hasattr(self.parent_window, 'parent_window') else None
        if main_window is None or not hasattr(main_window, 'dbc_controller'):
            QMessageBox.warning(self, "Error", "Cannot access DBC controller from main window.")
            return
        handlers = main_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        # Build Rx/Tx sets for the selected ECU
        rx_entries = set()
        tx_entries = set()
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                messages = handler.get_messages() if hasattr(handler, 'get_messages') else []
                for msg in messages:
                    if self.selected_ecu in msg.get('receivers', []):
                        rx_entries.add((msg['frame_id'], msg['name']))
                    if self.selected_ecu in msg.get('senders', []):
                        tx_entries.add((msg['frame_id'], msg['name']))
        all_entries = sorted(rx_entries.union(tx_entries))
        # Build presence table: { (frame_id, name): {file: present/—} }
        presence = {}
        for entry in all_entries:
            presence[entry] = {}
            for file_name in selected_files:
                handler = handler_map.get(file_name)
                found = False
                if handler:
                    messages = handler.get_messages() if hasattr(handler, 'get_messages') else []
                    for msg in messages:
                        if msg['frame_id'] == entry[0] and msg['name'] == entry[1]:
                            if self.selected_ecu in msg.get('receivers', []) or self.selected_ecu in msg.get('senders', []):
                                found = True
                                break
                presence[entry][file_name] = "present" if found else "—"
        # Create dialog and table
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window)
        dialog.setWindowTitle(f"ECU Message Presence Report: {self.selected_ecu}")
        dialog.setMinimumSize(700, 400)
        dialog.resize(1200, 700)  # Reasonable default size, user can resize/maximize
        layout = QVBoxLayout(dialog)
        table = QTableWidget()
        table.setColumnCount(2 + len(selected_files))
        table.setHorizontalHeaderLabels(["Frame ID", "Message Name"] + selected_files)
        if all_entries:
            table.setRowCount(len(all_entries))
            for row, (frame_id, msg_name) in enumerate(all_entries):
                table.setItem(row, 0, QTableWidgetItem(f"0x{frame_id:X}"))
                table.setItem(row, 1, QTableWidgetItem(msg_name))
                for col, file_name in enumerate(selected_files):
                    val = presence[(frame_id, msg_name)][file_name]
                    item = QTableWidgetItem(val)
                    item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                    table.setItem(row, 2 + col, item)
        else:
            table.setRowCount(1)
            item = QTableWidgetItem("No Rx/Tx messages found for selected ECU.")
            item.setFlags(item.flags() ^ Qt.ItemIsEditable)
            table.setItem(0, 0, item)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setSortingEnabled(True)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout.addWidget(table)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        dialog.show()

    def show_detailed_ecu_comparison(self):
        if not hasattr(self, 'selected_ecu') or not self.selected_ecu:
            QMessageBox.warning(self, "No ECU Selected", "Please select an ECU first.")
            return
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files.")
            return
        # Traverse up to main window to access dbc_controller
        main_window = self.parent_window.parent_window if hasattr(self.parent_window, 'parent_window') else None
        if main_window is None or not hasattr(main_window, 'dbc_controller'):
            QMessageBox.warning(self, "Error", "Cannot access DBC controller from main window.")
            return
        handlers = main_window.dbc_controller.get_all_handlers()
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
                    # Rx: selected ECU is a receiver
                    if self.selected_ecu in msg.get('receivers', []):
                        frame_id = msg['frame_id']
                        if frame_id not in rx_map[file_name]:
                            rx_map[file_name][frame_id] = []
                        rx_map[file_name][frame_id].append(msg)
                    # Tx: selected ECU is a sender
                    if self.selected_ecu in msg.get('senders', []):
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
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QPushButton, QFileDialog
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.Window)
        dialog.setWindowTitle(f"Detailed ECU Comparison: {self.selected_ecu}")
        dialog.setMinimumSize(1000, 600)
        layout = QVBoxLayout(dialog)
        tree = QTreeWidget()
        tree.setColumnCount(2 + len(selected_files))
        tree.setHeaderLabels(["Frame ID", "Property"] + selected_files)
        tree.setAlternatingRowColors(True)
        tree.setRootIsDecorated(True)
        # For each frame_id, compare messages
        for frame_id in sorted(all_frame_ids):
            msg_names = []
            file_msgs = {}
            for file in selected_files:
                msg = None
                rx_msgs = rx_map[file].get(frame_id, [])
                tx_msgs = tx_map[file].get(frame_id, [])
                if rx_msgs:
                    msg = rx_msgs[0]
                elif tx_msgs:
                    msg = tx_msgs[0]
                file_msgs[file] = msg
                msg_names.append(msg['name'] if msg else "")
            msg_item = QTreeWidgetItem([f"0x{frame_id:X}", ""] + msg_names)
            tree.addTopLevelItem(msg_item)
            # Role row
            gateway_roles = []
            rx_count = 0
            tx_count = 0
            for file in selected_files:
                msg = file_msgs[file]
                if msg:
                    is_rx = self.selected_ecu in msg.get('receivers', [])
                    is_tx = self.selected_ecu in msg.get('senders', [])
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
            gateway_role_item = QTreeWidgetItem(['', 'role', *gateway_roles])
            # Highlight if roles are different between DBC files
            if len(set(gateway_roles)) > 1:
                for col in range(2, 2 + len(selected_files)):
                    gateway_role_item.setBackground(col, Qt.yellow)
            msg_item.addChild(gateway_role_item)
            # Rx nodes row
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
            for idx, file in enumerate(selected_files):
                msg = file_msgs[file]
                gateway_role = gateway_roles[idx]
                rx_nodes_str = rx_nodes_values[idx]
                if gateway_role in ('Tx', 'Rx/Tx') and rx_nodes_str == '--':
                    rx_nodes_item.setBackground(idx + 2, Qt.yellow)
            msg_item.addChild(rx_nodes_item)
            # Tx nodes row
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
            # Properties to compare
            properties_to_compare = [
                'name', 'length', 'is_extended_frame', 'is_fd', 'frame_format', 'cycle_time', 'send_type'
            ]
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
                    if gateway_role != '--':
                        compare_values.append(str(val))
                prop_item = QTreeWidgetItem(['', prop, *values])
                if prop != 'name' and len(set(compare_values)) > 1:
                    for idx, gateway_role in enumerate(gateway_roles):
                        col = idx + 2
                        if gateway_role != '--':
                            prop_item.setBackground(col, Qt.yellow)
                msg_item.addChild(prop_item)
            # Signal comparison by (start, length)
            all_signal_positions = set()
            signal_map_per_file = [{} for _ in selected_files]
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
                sig_names = []
                gateway_roles_for_signal = []
                for idx, file in enumerate(selected_files):
                    sig = signal_map_per_file[idx].get(start_length)
                    sig_names.append(sig['name'] if sig else '--')
                    gateway_roles_for_signal.append(gateway_roles[idx])
                sig_item = QTreeWidgetItem(['', f"Signal: {start_length[0]}:{start_length[1]}", *sig_names])
                msg_item.addChild(sig_item)
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
                    if prop != 'name' and len(set(compare_values)) > 1:
                        for idx, gateway_role in enumerate(gateway_roles_for_signal):
                            col = idx + 2
                            if gateway_role != '--':
                                prop_row.setBackground(col, Qt.yellow)
                    sig_item.addChild(prop_row)
                # Value Table Comparison
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
                            pass
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
            # Highlight top-level if any descendant is highlighted
            def any_descendant_highlighted(item):
                for col in range(2, 2 + len(selected_files)):
                    brush = item.background(col)
                    if hasattr(brush, 'color') and brush.color().name().lower() in ['#ffff00', '#ff0']:
                        return True
                for i in range(item.childCount()):
                    if any_descendant_highlighted(item.child(i)):
                        return True
                return False
            if any_descendant_highlighted(msg_item):
                for col in range(0, 2 + len(selected_files)):
                    msg_item.setBackground(col, Qt.yellow)
        layout.addWidget(tree)
        # Export and close buttons
        button_layout = QHBoxLayout()
        export_btn = QPushButton("Export to CSV")
        def export_tree_to_csv():
            path, _ = QFileDialog.getSaveFileName(dialog, "Export Comparison to CSV", "", "CSV Files (*.csv)")
            if not path:
                return
            import csv
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                header = ["Frame ID / Property"] + selected_files
                writer.writerow(header)
                def write_item(item, indent_level=0):
                    row_data = []
                    prop_name = "  " * indent_level + item.text(1)
                    if indent_level == 0:
                        row_data.append(item.text(0))
                    else:
                        row_data.append("")
                    row_data.append(prop_name)
                    for col in range(2, tree.columnCount()):
                        row_data.append(item.text(col))
                    writer.writerow(row_data)
                    for i in range(item.childCount()):
                        write_item(item.child(i), indent_level + 1)
                for i in range(tree.topLevelItemCount()):
                    write_item(tree.topLevelItem(i))
            QMessageBox.information(dialog, "Success", f"Comparison data successfully exported to:\n{path}")
        export_btn.clicked.connect(export_tree_to_csv)
        button_layout.addWidget(export_btn)
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        dialog.resize(1200, 700)
        dialog.show()

    def _find_tab_index_by_name(self, name):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == name:
                return i
        return -1 