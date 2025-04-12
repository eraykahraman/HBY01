from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSpacerItem, QSizePolicy, QFrame,
                            QSplitter, QMenuBar, QMenu, QAction, QDialog)
from PyQt5.QtCore import Qt
from controller.DBC_IO_Controller import DBC_IO_Controller
from view.dbc_listview import DBCListView
from view.dbc_display_view import DBCDisplayView
from view.dbc_window import DBCWindow
from view.db_config_dialog import DatabaseConfigDialog
from view.login_dialog import LoginDialog
from utils.auth_service import AuthService
import logging

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Master")
        self.setGeometry(100, 100, 1200, 800)
        self.logger = logging.getLogger(__name__)
        
        # Initialize the auth service
        self.auth_service = AuthService()
        self.current_user = None
        
        # Initialize the DBC controller
        self.dbc_controller = DBC_IO_Controller()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.createMenuBar()
        
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
        
        # Create top button layout
        button_layout = QHBoxLayout()
        
        # Create and add the import button
        self.import_button = QPushButton("Import DBC")
        self.import_button.setEnabled(True)  # Enable by default for offline use
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_dbc)
        button_layout.addWidget(self.import_button)
        
        # Add spacer
        button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Create and add the login button
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(80)
        self.login_button.clicked.connect(self.show_login_dialog)
        button_layout.addWidget(self.login_button)
        
        # Add button layout to left layout
        left_layout.addLayout(button_layout)
        
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
        
        # Create user label in status bar
        self.user_label = QLabel("Not logged in")
        self.statusBar.addPermanentWidget(self.user_label)
        
        # Connect to controller signals
        self.dbc_controller.handlers_changed.connect(self.on_handlers_changed)
        self.dbc_controller.handler_removed.connect(self.on_handler_removed)
        self.dbc_controller.db_error.connect(self.on_db_error)
        
        # Connect to list view signals
        self.dbc_list.handler_selected.connect(self.on_handler_selected)
        self.dbc_list.handler_removed.connect(self.dbc_controller.remove_dbc)
        self.dbc_list.handler_open_in_new_window.connect(self.open_dbc_in_new_window)
        
    def createMenuBar(self):
        """Create the main menu bar with all menus"""
        menubar = self.menuBar()
        
        # File menu
        fileMenu = menubar.addMenu('&File')
        
        # Import DBC action
        importAction = QAction('&Import DBC...', self)
        importAction.setShortcut('Ctrl+I')
        importAction.setStatusTip('Import a DBC file')
        importAction.triggered.connect(self.import_dbc)
        fileMenu.addAction(importAction)
        
        # Recent files submenu
        self.recentFilesMenu = QMenu('&Recent Files', self)
        fileMenu.addMenu(self.recentFilesMenu)
        
        # Update recent files menu when shown
        self.recentFilesMenu.aboutToShow.connect(self.updateRecentFilesMenu)
        
        # Exit action
        exitAction = QAction('E&xit', self)
        exitAction.setShortcut('Alt+F4')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)
        
        # Database menu
        dbMenu = menubar.addMenu('&Database')
        
        # Database configuration action
        dbConfigAction = QAction('&Configure...', self)
        dbConfigAction.setStatusTip('Configure database connection')
        dbConfigAction.triggered.connect(self.showDatabaseConfig)
        dbMenu.addAction(dbConfigAction)
        
        # Database search action
        dbSearchAction = QAction('&Search...', self)
        dbSearchAction.setStatusTip('Search for DBC files in database')
        dbSearchAction.triggered.connect(self.showDatabaseSearch)
        dbMenu.addAction(dbSearchAction)
        
        # User menu
        userMenu = menubar.addMenu('&User')
        
        # Login action
        self.loginAction = QAction('&Login', self)
        self.loginAction.setStatusTip('Login to your account')
        self.loginAction.triggered.connect(self.show_login_dialog)
        userMenu.addAction(self.loginAction)
        
        # Logout action
        self.logoutAction = QAction('&Logout', self)
        self.logoutAction.setStatusTip('Logout from your account')
        self.logoutAction.triggered.connect(self.logout)
        self.logoutAction.setEnabled(False)  # Disabled until user logs in
        userMenu.addAction(self.logoutAction)
        
        # Help menu
        helpMenu = menubar.addMenu('&Help')
        
        # About action
        aboutAction = QAction('&About', self)
        aboutAction.setStatusTip('About this application')
        aboutAction.triggered.connect(self.showAbout)
        helpMenu.addAction(aboutAction)
        
    def updateRecentFilesMenu(self):
        """Update the recent files menu with files from database"""
        self.recentFilesMenu.clear()
        
        recent_files = self.dbc_controller.get_recent_dbc_files()
        if not recent_files:
            noRecentAction = QAction('No recent files', self)
            noRecentAction.setEnabled(False)
            self.recentFilesMenu.addAction(noRecentAction)
            return
            
        # Add each recent file to the menu
        for file in recent_files:
            filename = file.get('filename', 'Unknown')
            filepath = file.get('filepath', '')
            
            if filepath:
                action = QAction(filename, self)
                action.setStatusTip(f"Open {filepath}")
                # Use lambda to create a closure that captures the filepath
                action.triggered.connect(lambda checked, path=filepath: self.openRecentFile(path))
                self.recentFilesMenu.addAction(action)
        
    def openRecentFile(self, filepath):
        """Open a file from the recent files list"""
        self.statusBar.showMessage(f"Opening {filepath}...")
        handler, file_name, error = self.dbc_controller.import_dbc(self)
        
        if error:
            QMessageBox.critical(
                self,
                "DBC Load Error",
                error,
                QMessageBox.Ok
            )
            self.statusBar.showMessage("Failed to load DBC file - See error dialog for details")
        
    def showDatabaseConfig(self):
        """Show the database configuration dialog"""
        dialog = DatabaseConfigDialog(self)
        result = dialog.exec_()
        
        if result == QDialog.Accepted:
            self.statusBar.showMessage("Database configuration updated")
        
    def showDatabaseSearch(self):
        """Show a dialog to search for DBC files in the database"""
        # This would be implemented in a future update
        self.statusBar.showMessage("Database search not yet implemented")
        
    def showAbout(self):
        """Show the about dialog"""
        QMessageBox.about(
            self,
            "About DBC Master",
            "DBC Master v1.0\n\n"
            "A tool for viewing and editing DBC files.\n\n"
            "© 2025 Your Company"
        )
        
    def import_dbc(self):
        """Import a DBC file"""
        # Continue with import without requiring authentication
        handler, file_name, error = self.dbc_controller.import_dbc(self, store_in_db=self.auth_service.is_authenticated())
        
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
        elif file_name:
            if self.auth_service.is_authenticated():
                self.statusBar.showMessage(f"Imported DBC file: {file_name} and stored in database")
            else:
                self.statusBar.showMessage(f"Imported DBC file: {file_name} (offline mode - not stored in database)")
        
    def show_login_dialog(self):
        """Show the login dialog"""
        dialog = LoginDialog(self.auth_service, self)
        dialog.login_successful.connect(self.handle_login_success)
        dialog.exec_()
        
    def handle_login_success(self, user_info):
        """Handle successful login"""
        self.current_user = user_info
        self.user_label.setText(f"Logged in as: {user_info.get('username', 'Unknown')}")
        
        # Update UI state
        self.login_button.setText("Logout")
        self.login_button.clicked.disconnect()
        self.login_button.clicked.connect(self.logout)
        
        self.loginAction.setEnabled(False)
        self.logoutAction.setEnabled(True)
        
        # Enable import button if user has permission
        has_import_permission = self.auth_service.has_permission("add_dbc")
        self.import_button.setEnabled(has_import_permission)
        
        # Load DBC files from database
        self.statusBar.showMessage("Loading DBC files from database...")
        files_loaded = self.dbc_controller.load_dbc_files_from_database()
        
        if files_loaded > 0:
            self.statusBar.showMessage(f"Welcome, {user_info.get('username', 'Unknown')}! Loaded {files_loaded} DBC files from database.", 5000)
        else:
            self.statusBar.showMessage(f"Welcome, {user_info.get('username', 'Unknown')}!", 5000)
        
    def logout(self):
        """Logout the current user"""
        self.auth_service.logout()
        self.current_user = None
        
        # Update UI state
        self.user_label.setText("Not logged in")
        self.login_button.setText("Login")
        self.login_button.clicked.disconnect()
        self.login_button.clicked.connect(self.show_login_dialog)
        
        self.loginAction.setEnabled(True)
        self.logoutAction.setEnabled(False)
        
        # Keep import button enabled for offline use
        self.import_button.setEnabled(True)
        
        self.statusBar.showMessage("Logged out")
        
    def on_handlers_changed(self, handlers):
        """Handle updates to the handlers list"""
        self.dbc_list.update_handlers(handlers)
        
    def on_handler_removed(self, file_path):
        """Handle handler removal"""
        self.statusBar.showMessage(f"Removed DBC file: {file_path}")
        self.dbc_display.clear_display()  # Clear display when handler is removed
        
    def on_handler_selected(self, handler):
        """Handle handler selection"""
        file_info = handler.get_file_info()
        self.statusBar.showMessage(f"Selected DBC file: {file_info['file_name']} ({file_info['messages_count']} messages, {file_info['nodes_count']} nodes)")
        self.dbc_display.update_display(handler)  # Update display with selected handler
        
    def open_dbc_in_new_window(self, handler):
        """Open a DBC file in a new window"""
        window = DBCWindow(handler, self)
        window.show()
        
    def on_db_error(self, error_message):
        """Handle database errors"""
        self.logger.error(f"Database error: {error_message}")
        # Display a non-blocking status message
        self.statusBar.showMessage(f"Database error: {error_message}", 5000)  # Show for 5 seconds 