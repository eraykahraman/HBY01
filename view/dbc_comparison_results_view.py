from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QAbstractItemView, QMessageBox, QTextEdit, QWidget
from PyQt5.QtCore import Qt

class DBCComparisonResultsView(QMainWindow):
    def __init__(self, imported_dbc_files=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select DBC Files to Compare")
        self.setMinimumSize(800, 600)
        self.imported_dbc_files = imported_dbc_files or []
        self.parent_window = parent
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        
        self.setup_ui()

    def setup_ui(self):
        self.title_label = QLabel("Select DBC Files to Compare")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.layout.addWidget(self.title_label)

        # List of imported DBC files with checkboxes
        self.dbc_list_widget = QListWidget()
        self.dbc_list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.dbc_list_widget.setMinimumHeight(200)
        for dbc_file in self.imported_dbc_files:
            item = QListWidgetItem(dbc_file)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.dbc_list_widget.addItem(item)
        self.layout.addWidget(self.dbc_list_widget)

        # Results text edit (hidden initially)
        self.results_text_edit = QTextEdit()
        self.results_text_edit.setReadOnly(True)
        self.results_text_edit.setVisible(False)
        self.results_text_edit.setMinimumWidth(700)
        self.results_text_edit.setMinimumHeight(300)
        self.layout.addWidget(self.results_text_edit)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Add Check Nodes button
        self.check_nodes_button = QPushButton("Check Nodes")
        self.check_nodes_button.setToolTip("Check nodes for selected DBC files")
        self.check_nodes_button.clicked.connect(self.check_nodes)
        button_layout.addWidget(self.check_nodes_button)
        
        self.check_messages_button = QPushButton("Check Messages")
        self.check_messages_button.setToolTip("Check messages for selected DBC files")
        self.check_messages_button.clicked.connect(self.check_messages)
        button_layout.addWidget(self.check_messages_button)
        
        self.compare_button = QPushButton("Compare")
        self.compare_button.setToolTip("Compare selected DBC files")
        self.compare_button.clicked.connect(self.compare_selected_files)
        button_layout.addWidget(self.compare_button)
        
        # Add Export button
        self.export_button = QPushButton("Export")
        self.export_button.setToolTip("Export results to a text file")
        self.export_button.clicked.connect(self.export_results)
        button_layout.addWidget(self.export_button)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        button_layout.addWidget(close_button)
        self.layout.addLayout(button_layout)

    def compare_selected_files(self):
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files to compare.")
            return
        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        file_to_signals = {}
        missing_files = []
        # Build a mapping from file name to handler for quick lookup
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                # Build mapping: signal_name -> set of message_names
                signal_to_messages = {}
                messages = handler.get_messages() if hasattr(handler, 'get_messages') else []
                for msg in messages:
                    for signal in msg.get('signals', []):
                        name = signal['name']
                        if name not in signal_to_messages:
                            signal_to_messages[name] = set()
                        signal_to_messages[name].add(msg['name'])
                file_to_signals[file_name] = signal_to_messages
            else:
                missing_files.append(file_name)
        if missing_files:
            QMessageBox.warning(self, "Missing Handlers", f"No handler found for the following files:\n" + "\n".join(missing_files))
        print("Selected files:", selected_files)
        print("Files with signals:", list(file_to_signals.keys()))
        # Compare each pair
        results = []
        files = list(file_to_signals.keys())
        for i in range(len(files)):
            for j in range(i+1, len(files)):
                f1, f2 = files[i], files[j]
                signals1 = set(file_to_signals[f1].keys())
                signals2 = set(file_to_signals[f2].keys())
                common = signals1.intersection(signals2)
                if common:
                    results.append(f"Duplications in DBC file {f1} and {f2}:")
                    for name in sorted(common):
                        results.append(f"- Signal: {name}")
                        results.append(f"  {f1}: Message(s): {', '.join(sorted(file_to_signals[f1][name]))}")
                        results.append(f"  {f2}: Message(s): {', '.join(sorted(file_to_signals[f2][name]))}")
                    results.append("")
                else:
                    results.append(f"No duplications in DBC file {f1} and {f2}.")
                    results.append("")
        if not results:
            results.append("Selected DBC files:")
            for f in selected_files:
                results.append(f"- {f}")
            results.append("")
            results.append("No duplicates found.")
        print("\n".join(results))
        self.results_text_edit.setPlainText("\n".join(results))
        self.results_text_edit.setVisible(True)

    def check_messages(self):
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files to check messages.")
            return
        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        file_to_frameid_msgs = {}
        missing_files = []
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                frameid_to_msgs = {}
                messages = handler.get_messages() if hasattr(handler, 'get_messages') else []
                for msg in messages:
                    frame_id = msg['frame_id']
                    if frame_id not in frameid_to_msgs:
                        frameid_to_msgs[frame_id] = []
                    frameid_to_msgs[frame_id].append(msg['name'])
                file_to_frameid_msgs[file_name] = frameid_to_msgs
            else:
                missing_files.append(file_name)
        if missing_files:
            QMessageBox.warning(self, "Missing Handlers", f"No handler found for the following files:\n" + "\n".join(missing_files))
        results = []
        files = list(file_to_frameid_msgs.keys())
        for i in range(len(files)):
            for j in range(i+1, len(files)):
                f1, f2 = files[i], files[j]
                frameids1 = set(file_to_frameid_msgs[f1].keys())
                frameids2 = set(file_to_frameid_msgs[f2].keys())
                common = frameids1.intersection(frameids2)
                if common:
                    results.append(f"Duplicate Frame IDs in {f1} and {f2}:")
                    for frame_id in sorted(common):
                        results.append(f"- Frame ID: 0x{frame_id:X}")
                        results.append(f"  {f1}: Message(s): {', '.join(file_to_frameid_msgs[f1][frame_id])}")
                        results.append(f"  {f2}: Message(s): {', '.join(file_to_frameid_msgs[f2][frame_id])}")
                    results.append("")
                else:
                    results.append(f"No duplicate Frame IDs in {f1} and {f2}.")
                    results.append("")
        self.results_text_edit.setPlainText("\n".join(results))
        self.results_text_edit.setVisible(True)

    def check_nodes(self):
        selected_files = []
        for i in range(self.dbc_list_widget.count()):
            item = self.dbc_list_widget.item(i)
            if item.checkState() == Qt.Checked:
                selected_files.append(item.text())
        if len(selected_files) < 2:
            QMessageBox.warning(self, "Select DBC Files", "Please select at least two DBC files to check nodes.")
            return
        # Get handlers from parent window
        handlers = self.parent_window.dbc_controller.get_all_handlers()
        handler_map = {handler.get_file_info()['file_name']: handler for handler in handlers}
        file_to_nodes = {}
        missing_files = []
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                nodes = handler.get_nodes() if hasattr(handler, 'get_nodes') else []
                node_names = set(node['name'] for node in nodes)
                file_to_nodes[file_name] = node_names
            else:
                missing_files.append(file_name)
        if missing_files:
            QMessageBox.warning(self, "Missing Handlers", f"No handler found for the following files:\n" + "\n".join(missing_files))
        results = []
        files = list(file_to_nodes.keys())
        for i in range(len(files)):
            for j in range(i+1, len(files)):
                f1, f2 = files[i], files[j]
                nodes1 = file_to_nodes[f1]
                nodes2 = file_to_nodes[f2]
                common = nodes1.intersection(nodes2)
                if common:
                    results.append(f"Duplicate Nodes in {f1} and {f2}:")
                    for name in sorted(common):
                        results.append(f"- {name}")
                    results.append("")
                else:
                    results.append(f"No duplicate Nodes in {f1} and {f2}.")
                    results.append("")
        self.results_text_edit.setPlainText("\n".join(results))
        self.results_text_edit.setVisible(True)

    def export_results(self):
        from PyQt5.QtWidgets import QFileDialog
        text = self.results_text_edit.toPlainText()
        if not text.strip():
            QMessageBox.warning(self, "Export Error", "There is no result to export.")
            return
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Results", "results.txt", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(self, "Export Successful", f"Results exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export results: {str(e)}") 