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

        self.analyze_button = QPushButton("Analyze Compatibility")
        self.analyze_button.setToolTip("Perform comprehensive compatibility analysis")
        self.analyze_button.clicked.connect(self.analyze_compatibility)
        button_layout.addWidget(self.analyze_button)

        self.export_button = QPushButton("Export Results")
        self.export_button.setToolTip("Export compatibility analysis results")
        self.export_button.clicked.connect(self.export_results)
        self.export_button.setEnabled(False)
        button_layout.addWidget(self.export_button)

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

    def analyze_compatibility(self):
        self.results_section.setVisible(True)
        # Show ECU message presence in a dialog if an ECU is selected
        if hasattr(self, 'selected_ecu') and self.selected_ecu:
            self.show_ecu_message_presence_dialog()
        # (Other compatibility analysis logic can go here)

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

    def _find_tab_index_by_name(self, name):
        for i in range(self.tab_widget.count()):
            if self.tab_widget.tabText(i) == name:
                return i
        return -1 