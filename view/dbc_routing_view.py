from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QAbstractItemView, QWidget, QPushButton, QHBoxLayout, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt

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
        node_names = set()
        for file_name in selected_files:
            handler = handler_map.get(file_name)
            if handler:
                nodes = handler.get_nodes() if hasattr(handler, 'get_nodes') else []
                for node in nodes:
                    node_names.add(node['name'])
        if not node_names:
            QMessageBox.warning(self, "No Nodes Found", "No nodes found in the selected DBC files.")
            return
        node_list = sorted(node_names)
        gateway, ok = QInputDialog.getItem(self, "Select Gateway Node", "Gateway Node:", node_list, 0, False)
        if ok and gateway:
            self.gateway_node = gateway
            QMessageBox.information(self, "Gateway Selected", f"Gateway node selected: {gateway}") 