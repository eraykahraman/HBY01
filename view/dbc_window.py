from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from view.dbc_display_view import DBCDisplayView
from controller.dbc_io_handler import DBC_IO_Handler

class DBCWindow(QMainWindow):
    def __init__(self, handler: DBC_IO_Handler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the window UI"""
        # Set window title with file name
        file_info = self.handler.get_file_info()
        self.setWindowTitle(f"DBC Viewer - {file_info['file_name']}")
        
        # Set window size and position
        self.setGeometry(200, 200, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create and add the DBC display view
        self.display_view = DBCDisplayView()
        layout.addWidget(self.display_view)
        
        # Update display with handler data
        self.display_view.update_display(self.handler) 