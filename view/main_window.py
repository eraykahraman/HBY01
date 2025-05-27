from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSpacerItem, QSizePolicy, QFrame,
                            QSplitter, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from controller.DBC_IO_Controller import DBC_IO_Controller
from controller.db_load_controller import DBLoadController
from view.dbc_listview import DBCListView
from view.dbc_display_view import DBCDisplayView
from view.dbc_window import DBCWindow
from view.dbc_comparison_results_view import DBCComparisonResultsView
from view.dbc_routing_view import DBCRoutingView
from database import db_session
from view.user_auth_dialog import UserAuthDialog
from PyQt5.QtWidgets import QDialog
from database.models import UserRole, DBCFile
from database.repository import DBCRepository

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Master")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize controllers
        self.dbc_controller = DBC_IO_Controller()
        self.db_load_controller = DBLoadController()
        
        # Connect DB load controller signals
        self.db_load_controller.dbc_loaded.connect(self.on_dbc_loaded)
        self.db_load_controller.dbc_load_failed.connect(self.on_dbc_load_failed)
        
        # Track open DBC windows by file path
        self.open_dbc_windows = {}  # {file_path: DBCWindow}
        
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
        
        # Create buttons layout for import/export
        buttons_layout = QHBoxLayout()
        
        # Create and add the database connect button
        self.db_connect_button = QPushButton("Connect DB")
        self.db_connect_button.setFixedWidth(120)
        self.db_connect_button.clicked.connect(self.connect_database)
        buttons_layout.addWidget(self.db_connect_button)
        
        # Create and add the import button
        self.import_button = QPushButton("Import DBC")
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_dbc)
        buttons_layout.addWidget(self.import_button)
        
        # Create and add the load to DB button (hidden by default)
        self.load_to_db_button = QPushButton("Load to DB")
        self.load_to_db_button.setFixedWidth(120)
        self.load_to_db_button.setToolTip("Load DBC file to database (Netcom Engineers only)")
        self.load_to_db_button.clicked.connect(self.load_dbc_to_database)
        self.load_to_db_button.setVisible(False)  # Hidden initially
        buttons_layout.addWidget(self.load_to_db_button)
        
        # Create and add the compare button
        self.compare_button = QPushButton("Compare")
        self.compare_button.setFixedWidth(120)
        self.compare_button.setToolTip("Compare loaded DBC files for conflicting signal names")
        self.compare_button.clicked.connect(self.open_comparison_results_view)
        buttons_layout.addWidget(self.compare_button)

        # Add Route button next to Compare
        self.route_button = QPushButton("Route")
        self.route_button.setFixedWidth(120)
        self.route_button.setToolTip("Route feature (to be implemented)")
        self.route_button.clicked.connect(self.open_routing_view)
        buttons_layout.addWidget(self.route_button)
        
        # Create and add the logout button (hidden by default)
        self.logout_button = QPushButton("Logout")
        self.logout_button.setFixedWidth(120)
        self.logout_button.clicked.connect(self.logout_user)
        self.logout_button.setVisible(False)  # Hidden initially
        buttons_layout.addWidget(self.logout_button)
        
        # Add buttons layout to left panel
        left_layout.addLayout(buttons_layout)
        
        # Create and add the DBC list view
        self.dbc_list = DBCListView()
        left_layout.addWidget(self.dbc_list)
        
        # Create database DBC files list
        self.db_dbc_list = QListWidget()
        self.db_dbc_list.setVisible(False)  # Hidden initially
        self.db_dbc_list.itemDoubleClicked.connect(self.on_db_dbc_selected)
        left_layout.addWidget(QLabel("DBC Files in Database:"))
        left_layout.addWidget(self.db_dbc_list)
        
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
        self.dbc_controller.dbc_exported.connect(self.on_dbc_exported)
        
        # Connect to list view signals
        self.dbc_list.handler_selected.connect(self.on_handler_selected)
        self.dbc_list.handler_removed.connect(self.dbc_controller.remove_dbc)
        self.dbc_list.handler_open_in_new_window.connect(self.open_dbc_in_new_window)
        self.dbc_list.handler_export.connect(self.on_handler_export)
        
        # Connect to display view signals
        self.dbc_display.export_requested.connect(self.on_handler_export)
        
        self.current_user_role = None
        
        self.setup_db_dbc_list_context_menu()
        
    def load_dbc_to_database(self):
        """Load the currently selected DBC file to the database"""
        # Get the selected handler
        handler = self.dbc_list.get_selected_handler()
        if not handler:
            QMessageBox.warning(
                self,
                "Load to DB Error",
                "Please first import a DBC file using the 'Import DBC' button and select it in the list.",
                QMessageBox.Ok
            )
            return

        try:
            # Get file info
            file_info = handler.get_file_info()
            file_path = handler.get_file_path()
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Use the DB load controller to save to database
            success, dbc_file, error = self.db_load_controller.load_dbc_to_database(
                file_name=file_info['file_name'],
                file_path=file_path,
                content=content
            )

            if not success:
                QMessageBox.critical(
                    self,
                    "Load to DB Error",
                    error,
                    QMessageBox.Ok
                )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Load to DB Error",
                f"Failed to load DBC file to database: {str(e)}",
                QMessageBox.Ok
            )

    def on_dbc_loaded(self, dbc_file: DBCFile):
        """Handle successful DBC file load to database"""
        try:
            file_name = dbc_file.file_name
            self.statusBar.showMessage(f"Successfully loaded DBC file to database: {file_name}")
            QMessageBox.information(
                self,
                "Success",
                f"DBC file '{file_name}' has been loaded to the database.",
                QMessageBox.Ok
            )
        except Exception as e:
            self.statusBar.showMessage("Successfully loaded DBC file to database")
            QMessageBox.information(
                self,
                "Success",
                "DBC file has been loaded to the database.",
                QMessageBox.Ok
            )

    def on_dbc_load_failed(self, error_msg: str):
        """Handle failed DBC file load to database"""
        self.statusBar.showMessage("Failed to load DBC file to database")
        QMessageBox.critical(
            self,
            "Load to DB Error",
            error_msg,
            QMessageBox.Ok
        )
    
    def connect_database(self):
        """Show user authentication dialog, then connect to the database if successful login/register"""
        auth_dialog = UserAuthDialog(self)
        if auth_dialog.exec_() == QDialog.Accepted and auth_dialog.success:
            try:
                db_session.create_tables()
                self.db_connect_button.setEnabled(False)
                self.db_connect_button.setText("Connected")
                self.statusBar.showMessage(f"Connected as {auth_dialog.username} ({auth_dialog.role})")
                self.import_button.setEnabled(True)
                self.logout_button.setVisible(True)
                self.current_user_role = auth_dialog.role

                # Show Load to DB button only for Netcom Engineers
                if self.current_user_role == UserRole.NETCOM_ENGINEER.value:
                    self.load_to_db_button.setVisible(True)
                else:
                    self.load_to_db_button.setVisible(False)

                # Show and update database DBC files list
                self.db_dbc_list.setVisible(True)
                self.update_db_dbc_list()

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Database Connection Error",
                    f"Failed to connect to database: {str(e)}",
                    QMessageBox.Ok
                )
                self.statusBar.showMessage("Failed to connect to database")
        else:
            self.statusBar.showMessage("Database connection cancelled or authentication failed")
    
    def import_dbc(self):
        """Import a DBC file (available to all users, even if not connected to DB)"""
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
            # Show message about next steps
            if self.current_user_role == UserRole.NETCOM_ENGINEER.value:
                self.statusBar.showMessage("DBC file imported. Select it in the list and click 'Load to DB' to save to database.")
    
    def export_dbc(self):
        """
        Export the currently selected DBC file
        """
        # Get the selected handler
        handler = self.dbc_list.get_selected_handler()
        if not handler:
            QMessageBox.warning(
                self,
                "Export Error",
                "No DBC file selected for export.",
                QMessageBox.Ok
            )
            return
            
        # Get the file path from the handler
        file_path = handler.get_file_path()
        
        # Call the controller to export the file
        success, target_file, error = self.dbc_controller.export_dbc(file_path, self)
        
        if error and error != "Export cancelled":
            # Show error message dialog
            QMessageBox.critical(
                self,
                "DBC Export Error",
                error,
                QMessageBox.Ok
            )
            # Show shorter version in status bar
            self.statusBar.showMessage("Failed to export DBC file - See error dialog for details")
        
    def on_dbc_exported(self, file_path):
        """Handle successful DBC export"""
        self.statusBar.showMessage(f"Successfully exported DBC file to: {file_path}")
        
    def on_handlers_changed(self, handlers):
        """Handle updates to the handlers list"""
        self.dbc_list.update_handlers(handlers)
        # Enable/disable the export button based on whether there are handlers
        # self.export_button.setEnabled(len(handlers) > 0)  # Removed as the button no longer exists
        
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
        file_path = handler.get_file_path()
        # Check if file is displayed in the main window
        if (self.dbc_display.current_handler and
            self.dbc_display.current_handler.get_file_path() == file_path):
            self.raise_()
            self.activateWindow()
        elif file_path in self.open_dbc_windows:
            window = self.open_dbc_windows[file_path]
            window.raise_()
            window.activateWindow()
        else:
            window = DBCWindow(handler, self)
            self.open_dbc_windows[file_path] = window
            window.dbc_window_closed.connect(self.on_dbc_window_closed)
            window.show()

    def on_dbc_window_closed(self, file_path):
        # Remove from open windows dict
        if file_path in self.open_dbc_windows:
            del self.open_dbc_windows[file_path]
        # Remove from controller/handlers if needed
        self.dbc_controller.remove_dbc(file_path)
        # Update the UI list
        self.dbc_list.update_handlers(self.dbc_controller.get_all_handlers())

    def on_handler_export(self, handler):
        """
        Handle export request from the context menu
        
        Args:
            handler (DBC_IO_Handler): The handler to export
        """
        # Get the file path from the handler
        file_path = handler.get_file_path()
        
        # Call the controller to export the file
        success, target_file, error = self.dbc_controller.export_dbc(file_path, self)
        
        if error and error != "Export cancelled":
            # Show error message dialog
            QMessageBox.critical(
                self,
                "DBC Export Error",
                error,
                QMessageBox.Ok
            )
            # Show shorter version in status bar
            self.statusBar.showMessage("Failed to export DBC file - See error dialog for details") 

    def open_comparison_results_view(self):
        # Get all handlers
        handlers = self.dbc_controller.get_all_handlers()
        # Get file names for display
        dbc_files = [h.get_file_info()['file_name'] for h in handlers]
        dialog = DBCComparisonResultsView(dbc_files, self)
        dialog.show()

    def open_routing_view(self):
        # Get all handlers
        handlers = self.dbc_controller.get_all_handlers()
        # Get file names for display
        dbc_files = [h.get_file_info()['file_name'] for h in handlers]
        routing_view = DBCRoutingView(dbc_files, self)
        routing_view.show()

    def logout_user(self):
        """Logout the current user and reset UI state"""
        self.db_connect_button.setEnabled(True)
        self.db_connect_button.setText("Connect DB")
        self.logout_button.setVisible(False)
        self.load_to_db_button.setVisible(False)  # Hide Load to DB button
        self.db_dbc_list.setVisible(False)  # Hide database DBC files list
        self.statusBar.showMessage("Logged out")
        self.current_user_role = None

    def on_db_dbc_selected(self, item):
        """Handle selection of a DBC file from the database list"""
        try:
            # Get the DBC file from the database
            dbc_file = self.db_load_controller.get_dbc_file(item.data(Qt.UserRole))
            if dbc_file:
                # Create a temporary file with the content
                import tempfile
                import os
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.dbc', delete=False) as temp_file:
                    temp_file.write(dbc_file.content)
                    temp_path = temp_file.name
                
                # Import the file using the DBC controller (use the new method)
                handler, file_name, error = self.dbc_controller.import_dbc_from_path(temp_path)
                if handler:
                    # Set only file_name to the original value from the database for display
                    handler.file_name = dbc_file.file_name
                    # Do NOT overwrite handler.file_path, keep it as the temp file path
                    # Clean up the temporary file
                    os.unlink(temp_path)
                    # Update the list view to reflect the new file name
                    self.dbc_list.update_handlers(self.dbc_controller.get_all_handlers())
                    # Select the handler in the list
                    self.dbc_list.select_handler(handler)
                elif error:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to load DBC file from database: {error}",
                        QMessageBox.Ok
                    )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load DBC file from database: {str(e)}",
                QMessageBox.Ok
            )

    def setup_db_dbc_list_context_menu(self):
        self.db_dbc_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.db_dbc_list.customContextMenuRequested.connect(self.on_db_dbc_list_context_menu)

    def on_db_dbc_list_context_menu(self, position):
        if self.current_user_role != UserRole.NETCOM_ENGINEER.value:
            return
        item = self.db_dbc_list.itemAt(position)
        if item:
            from PyQt5.QtWidgets import QMenu
            menu = QMenu()
            delete_action = menu.addAction("Delete from Database")
            action = menu.exec_(self.db_dbc_list.viewport().mapToGlobal(position))
            if action == delete_action:
                dbc_id = item.data(Qt.UserRole)
                dbc_name = item.text()
                reply = QMessageBox.question(
                    self,
                    "Delete DBC File",
                    f"Are you sure you want to delete '{dbc_name}' from the database?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    success = self.db_load_controller.delete_dbc_file(dbc_id)
                    if success:
                        self.statusBar.showMessage(f"Deleted '{dbc_name}' from database.")
                        self.update_db_dbc_list()
                    else:
                        QMessageBox.critical(
                            self,
                            "Delete Error",
                            f"Failed to delete '{dbc_name}' from database.",
                            QMessageBox.Ok
                        )

    def update_db_dbc_list(self):
        """Update the list of DBC files from the database"""
        try:
            self.db_dbc_list.clear()
            dbc_files = self.db_load_controller.get_all_dbc_files()
            for dbc_file in dbc_files:
                item = QListWidgetItem(dbc_file.file_name)
                item.setData(Qt.UserRole, dbc_file.id)
                self.db_dbc_list.addItem(item)
            # Ensure context menu is set up
            self.setup_db_dbc_list_context_menu()
        except Exception as e:
            self.statusBar.showMessage(f"Failed to load DBC files from database: {str(e)}") 