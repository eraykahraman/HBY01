from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from controller.DBC_IO_Controller import DBC_IO_Controller
from view.dbc_listview import DBCListView
from view.dbc_display_view import DBCDisplayView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Master")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize the DBC controller
        self.dbc_controller = DBC_IO_Controller()
        
        # Initialize display view
        self.display_view = None
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Add some padding
        
        # Create horizontal layout for the button and content
        h_layout = QHBoxLayout()
        h_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins from horizontal layout
        
        # Create and add the import button
        self.import_button = QPushButton("Import DBC")
        self.import_button.setFixedWidth(120)  # Set a fixed width for the button
        self.import_button.clicked.connect(self.import_dbc)
        h_layout.addWidget(self.import_button)
        
        # Add horizontal stretch to push everything to the left
        h_layout.addStretch()
        
        # Add the horizontal layout to the main layout
        main_layout.addLayout(h_layout)
        
        # Create and add the DBC list view
        self.dbc_list = DBCListView()
        self.dbc_list.setFixedWidth(200)  # Set a fixed width for the list
        main_layout.addWidget(self.dbc_list)
        
        # Add vertical stretch to push everything to the top
        main_layout.addStretch()
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Connect to controller signals
        self.dbc_controller.dbc_loaded.connect(self.on_dbc_loaded)
        self.dbc_controller.dbc_error.connect(self.on_dbc_error)
        self.dbc_controller.dbc_removed.connect(self.on_dbc_removed)
        
        # Connect to list view signals
        self.dbc_list.dbc_selected.connect(self.on_dbc_selected)
        self.dbc_list.dbc_removed.connect(self.on_dbc_removed)
        
    def import_dbc(self):
        """Handle DBC file import"""
        self.dbc_controller.import_dbc(self)
        
    def on_dbc_loaded(self, file_path, db):
        """Handle successful DBC file load"""
        self.statusBar.showMessage(f"Loaded DBC file: {file_path}")
        self.dbc_list.add_dbc_file(file_path)
        
    def on_dbc_error(self, error_message):
        """Handle DBC file load error"""
        # Show error in popup message
        QMessageBox.critical(
            self,
            "DBC Load Error",
            error_message,
            QMessageBox.Ok
        )
        # Also show in status bar for reference
        self.statusBar.showMessage(f"Error: {error_message}")
        
    def on_dbc_selected(self, instance_id):
        """Handle DBC file selection from the list"""
        self.statusBar.showMessage(f"Selected DBC file: {instance_id}")
        
        # Create or show display view
        if not self.display_view:
            self.display_view = DBCDisplayView(self)
            self.display_view.show()
        
        # Update display view with DBC content
        self.display_view.display_dbc_content(instance_id)
        
    def on_dbc_removed(self, file_path):
        """Handle DBC file removal"""
        self.statusBar.showMessage(f"Removed DBC file: {file_path}")
        # Remove from list view
        for i in range(self.dbc_list.list_widget.count()):
            item = self.dbc_list.list_widget.item(i)
            if item.data(Qt.UserRole) == file_path:
                self.dbc_list.list_widget.takeItem(i)
                break 