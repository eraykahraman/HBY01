from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt
from controller.DBC_IO_Controller import DBC_IO_Controller
from view.dbc_listview import DBCListView

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Master")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize the DBC controller
        self.dbc_controller = DBC_IO_Controller()
        
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
        self.dbc_controller.handlers_changed.connect(self.on_handlers_changed)
        self.dbc_controller.handler_removed.connect(self.on_handler_removed)
        
        # Connect to list view signals
        self.dbc_list.handler_selected.connect(self.on_handler_selected)
        self.dbc_list.handler_removed.connect(self.dbc_controller.remove_dbc)
        
    def import_dbc(self):
        handler, file_name, error = self.dbc_controller.import_dbc(self)
        if error:
            # Show detailed error message in dialog
            QMessageBox.critical(
                self,
                "DBC Load Error",
                error,  # Use the full error message
                QMessageBox.Ok
            )
            # Show shorter version in status bar
            self.statusBar.showMessage("Failed to load DBC file - See error dialog for details")
        
    def on_handlers_changed(self, handlers):
        """Handle updates to the handlers list"""
        self.dbc_list.update_handlers(handlers)
        
    def on_handler_removed(self, file_path):
        """Handle handler removal"""
        self.statusBar.showMessage(f"Removed DBC file: {file_path}")
        
    def on_handler_selected(self, handler):
        """Handle handler selection"""
        file_info = handler.get_file_info()
        self.statusBar.showMessage(f"Selected DBC file: {file_info['file_name']} ({file_info['messages_count']} messages, {file_info['nodes_count']} nodes)")
        # TODO: Update the main view with the selected handler's contents 