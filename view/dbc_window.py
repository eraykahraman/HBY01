from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from view.dbc_display_view import DBCDisplayView
from controller.dbc_io_handler import DBC_IO_Handler

class DBCWindow(QMainWindow):
    dbc_window_closed = pyqtSignal(str)  # file_path
    def __init__(self, handler: DBC_IO_Handler, parent=None):
        super().__init__(parent)
        self.handler = handler
        self.file_path = handler.get_file_path() if hasattr(handler, 'get_file_path') else None
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
        
        # Connect signals
        self.display_view.export_requested.connect(self.on_export_requested)
        
        # Update display with handler data
        self.display_view.update_display(self.handler)
        
    def on_export_requested(self, handler):
        """
        Handle export request from the display view
        
        Args:
            handler (DBC_IO_Handler): The handler to export
        """
        # Use the parent window's controller to export the file
        if hasattr(self.parent(), 'dbc_controller'):
            file_path = handler.get_file_path()
            success, target_file, error = self.parent().dbc_controller.export_dbc(file_path, self)
            
            if error and error != "Export cancelled":
                # Show error message dialog
                QMessageBox.critical(
                    self,
                    "DBC Export Error",
                    error,
                    QMessageBox.Ok
                )
                # Show message in status bar if it exists
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage("Failed to export DBC file - See error dialog for details")
            elif success and target_file:
                # Show success message in status bar if it exists
                if hasattr(self, 'statusBar'):
                    self.statusBar().showMessage(f"Successfully exported DBC file to: {target_file}")
                else:
                    # If no status bar, show a success message box
                    QMessageBox.information(
                        self,
                        "DBC Export Success",
                        f"Successfully exported DBC file to: {target_file}",
                        QMessageBox.Ok
                    ) 
    def closeEvent(self, event):
        if self.file_path:
            self.dbc_window_closed.emit(self.file_path)
        super().closeEvent(event) 