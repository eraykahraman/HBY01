from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSpacerItem, QSizePolicy, QFrame,
                            QSplitter)
from PyQt5.QtCore import Qt
from controller.DBC_IO_Controller import DBC_IO_Controller
from view.dbc_listview import DBCListView
from view.dbc_display_view import DBCDisplayView
from view.dbc_window import DBCWindow

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
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(1)  # Set the width of the splitter handle
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #d0d0d0;
            }
            QSplitter::handle:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Create left panel for DBC list
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(1)
        
        # Create and add the import button
        self.import_button = QPushButton("Import DBC")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_dbc)
        left_layout.addWidget(self.import_button)
        
        # Create and add the DBC list view
        self.dbc_list = DBCListView()
        left_layout.addWidget(self.dbc_list)
        
        # Add left panel to splitter
        splitter.addWidget(left_panel)
        
        # Create and add the DBC display view to splitter
        self.dbc_display = DBCDisplayView()
        splitter.addWidget(self.dbc_display)
        
        # Set initial sizes for the splitter
        splitter.setSizes([200, 1000])  # Left panel 200px, rest to right panel
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Connect to controller signals
        self.dbc_controller.handlers_changed.connect(self.on_handlers_changed)
        self.dbc_controller.handler_removed.connect(self.on_handler_removed)
        
        # Connect to list view signals
        self.dbc_list.handler_selected.connect(self.on_handler_selected)
        self.dbc_list.handler_removed.connect(self.dbc_controller.remove_dbc)
        self.dbc_list.handler_open_in_new_window.connect(self.open_dbc_in_new_window)
        
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
        elif handler:
            # Successfully imported, select the handler to display it
            # This will go through on_handler_selected which will handle
            # displaying in main view or new window appropriately
            self.dbc_list.select_handler(handler)
        
    def on_handlers_changed(self, handlers):
        """Handle updates to the handlers list"""
        self.dbc_list.update_handlers(handlers)
        
    def on_handler_removed(self, file_path):
        """Handle handler removal"""
        self.statusBar.showMessage(f"Removed DBC file: {file_path}")
        self.dbc_display.clear_display()  # Clear display when handler is removed
        # After clearing the display, current_handler will be set to None in the clear_display method
        
    def on_handler_selected(self, handler):
        """Handle handler selection"""
        file_info = handler.get_file_info()
        
        # Check if a DBC file is already displayed in the main window
        if self.dbc_display.current_handler is not None:
            # If a file is already open, open the new file in a new window
            self.open_dbc_in_new_window(handler)
            self.statusBar.showMessage(f"Opened DBC file in new window: {file_info['file_name']} ({file_info['messages_count']} messages, {file_info['nodes_count']} nodes)")
        else:
            # If no file is open, display the new file in the main window
            self.statusBar.showMessage(f"Selected DBC file: {file_info['file_name']} ({file_info['messages_count']} messages, {file_info['nodes_count']} nodes)")
            self.dbc_display.update_display(handler)  # Update display with selected handler
        
    def open_dbc_in_new_window(self, handler):
        """Open a DBC file in a new window"""
        window = DBCWindow(handler, self)
        window.show() 