from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QStatusBar,
                            QMessageBox, QSpacerItem, QSizePolicy, QFrame,
                            QSplitter, QMenuBar, QMenu, QAction, QDialog, QTabWidget,
                            QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt
from controller.DBC_IO_Controller import DBC_IO_Controller
from view.dbc_listview import DBCListView
from view.dbc_display_view import DBCDisplayView
from view.dbc_window import DBCWindow
from view.db_config_dialog import DatabaseConfigDialog
from view.login_dialog import LoginDialog
from utils.auth_service import AuthService
from view.vehicle_view import VehicleView
from view.dbc_vehicle_assign_dialog import DBC_Vehicle_AssignDialog
import logging
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DBC Master")
        self.setGeometry(100, 100, 1200, 800)
        self.logger = logging.getLogger(__name__)
        
        # Initialize the auth service
        self.auth_service = AuthService()
        self.current_user = None
        
        # Initialize the DBC controller with auth service
        self.dbc_controller = DBC_IO_Controller(self.auth_service)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create menu bar
        self.createMenuBar()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Create DBC files tab
        dbc_tab = QWidget()
        dbc_layout = QVBoxLayout(dbc_tab)
        dbc_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for DBC files view
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
        
        # Create left panel for DBC list or Vehicle list depending on login state
        self.left_panel = QWidget()
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(5, 5, 5, 5)
        self.left_layout.setSpacing(1)
        
        # Create top button layout
        self.button_layout = QHBoxLayout()
        
        # Create and add the import button
        self.import_button = QPushButton("Import DBC")
        self.import_button.setEnabled(True)  # Enable by default for offline use
        self.import_button.setFixedWidth(120)
        self.import_button.clicked.connect(self.import_dbc)
        self.button_layout.addWidget(self.import_button)
        
        # Add spacer
        self.button_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Create and add the login button
        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(80)
        self.login_button.clicked.connect(self.show_login_dialog)
        self.button_layout.addWidget(self.login_button)
        
        # Add button layout to left layout
        self.left_layout.addLayout(self.button_layout)
        
        # Create and add the DBC list view
        self.dbc_list = DBCListView()
        self.left_layout.addWidget(self.dbc_list)
        
        # Create vehicle view (initially hidden)
        self.vehicle_list_view = VehicleView(self.dbc_controller, self.auth_service)
        self.vehicle_list_view.setVisible(False)
        self.vehicle_list_view.vehicle_selected.connect(self.on_vehicle_selected)
        self.left_layout.addWidget(self.vehicle_list_view)
        
        # Add left panel to splitter
        splitter.addWidget(self.left_panel)
        
        # Create and add the DBC display view to splitter
        self.dbc_display = DBCDisplayView()
        splitter.addWidget(self.dbc_display)
        
        # Set initial sizes for the splitter
        splitter.setSizes([200, 1000])  # Left panel 200px, rest to right panel
        
        # Add splitter to DBC tab layout
        dbc_layout.addWidget(splitter)
        
        # Create vehicles tab for Netcom Engineer access
        self.vehicles_tab = QWidget()
        vehicles_layout = QVBoxLayout(self.vehicles_tab)
        self.vehicle_view = VehicleView(self.dbc_controller, self.auth_service)
        self.vehicle_view.vehicle_selected.connect(self.on_vehicle_selected_tab)
        vehicles_layout.addWidget(self.vehicle_view)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(dbc_tab, "DBC Viewer")
        self.tab_widget.addTab(self.vehicles_tab, "Vehicle Management")
        
        # Initially hide vehicles tab (show only for Netcom Engineers)
        self.tab_widget.setTabVisible(1, False)
        
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
        
        # Load DBC files from database at startup
        self.load_dbc_files_from_database()
        
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
        # Check if user has permission to store in database
        store_in_db = False
        if self.auth_service.is_authenticated():
            # Specifically check for add_dbc permission for database storage
            store_in_db = self.auth_service.has_permission("add_dbc")
        
        # Continue with import
        handler, file_name, error = self.dbc_controller.import_dbc(self, store_in_db=store_in_db)
        
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
            if store_in_db:
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
        
        # Create view controls for logged-in users
        self.setup_view_controls()
        
        # Show vehicles in left panel instead of DBC files
        self.dbc_list.setVisible(False)
        self.vehicle_list_view.setVisible(True)
        self.vehicle_list_view.load_vehicles()  # Load vehicles from database
        
        # Show vehicles tab for Netcom Engineers
        is_netcom_engineer = self.auth_service.has_permission("manage_users")
        self.tab_widget.setTabVisible(1, is_netcom_engineer)
        
        # Update vehicle view permissions
        self.vehicle_view.update_permissions()
        self.vehicle_list_view.update_permissions()
        
        # Load DBC files from database
        self.load_dbc_files_from_database()
        
        # Show welcome message
        self.statusBar.showMessage(f"Welcome, {user_info.get('username', 'Unknown')}!", 5000)
        
    def setup_view_controls(self):
        """Set up view control buttons for logged-in users"""
        # Remove any existing view controls
        self.cleanup_view_controls()
        
        # Create view controls layout
        self.view_controls_layout = QHBoxLayout()
        
        # Create "Vehicles" button
        self.vehicles_button = QPushButton("Vehicles")
        self.vehicles_button.clicked.connect(self.show_vehicles_view)
        self.vehicles_button.setFixedWidth(80)
        
        # Create "DBC Files" button 
        self.dbc_files_button = QPushButton("DBC Files")
        self.dbc_files_button.clicked.connect(self.show_all_dbc_files)
        self.dbc_files_button.setFixedWidth(80)
        
        # Add buttons to layout
        self.view_controls_layout.addWidget(self.vehicles_button)
        self.view_controls_layout.addWidget(self.dbc_files_button)
        
        # Add spacer to push buttons to the left
        self.view_controls_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # Add view controls layout below the button layout
        self.left_layout.insertLayout(1, self.view_controls_layout)
    
    def cleanup_view_controls(self):
        """Clean up view control buttons"""
        # Check if view controls exist
        if hasattr(self, 'view_controls_layout'):
            # Clear and remove the layout instead of individual widgets
            # This is safer as it prevents accessing potentially deleted widgets
            if self.view_controls_layout is not None:
                # Remove all items from the layout
                while self.view_controls_layout.count():
                    item = self.view_controls_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                
                # Remove the layout itself
                self.left_layout.removeItem(self.view_controls_layout)
                self.view_controls_layout = None
                
                # Reset button references
                if hasattr(self, 'vehicles_button'):
                    self.vehicles_button = None
                if hasattr(self, 'dbc_files_button'):
                    self.dbc_files_button = None
    
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
        
        # Clean up view controls
        self.cleanup_view_controls()
        
        # Keep import button enabled for offline use
        self.import_button.setEnabled(True)
        
        # Switch back to DBC files in left panel
        self.vehicle_list_view.setVisible(False)
        self.dbc_list.setVisible(True)
        
        # Hide vehicles tab
        self.tab_widget.setTabVisible(1, False)
        
        self.statusBar.showMessage("Logged out")
    
    def show_vehicles_view(self):
        """Show vehicles in the left panel"""
        # Highlight the vehicles button
        self.vehicles_button.setStyleSheet("background-color: #e0e0e0;")
        self.dbc_files_button.setStyleSheet("")
        
        # Hide DBC list and show vehicle list
        self.dbc_list.setVisible(False)
        self.vehicle_list_view.setVisible(True)
        
        # Reload vehicles list
        self.vehicle_list_view.load_vehicles()
    
    def show_all_dbc_files(self):
        """Show all DBC files in the database"""
        # Highlight the DBC files button
        self.vehicles_button.setStyleSheet("")
        self.dbc_files_button.setStyleSheet("background-color: #e0e0e0;")
        
        # Create a list of all DBC files in the database
        if self.dbc_controller.db_service.is_database_enabled():
            self.statusBar.showMessage("Loading all DBC files from database...")
            
            # Get all DBC files from database
            all_dbc_files = self.dbc_controller.db_service.get_dbc_files()
            
            # Load each file that's not already loaded
            for file_info in all_dbc_files:
                file_path = file_info.get('filepath')
                
                # Skip if already loaded
                if file_path in self.dbc_controller.handlers:
                    continue
                    
                # Skip if file doesn't exist on disk
                if not os.path.exists(file_path):
                    self.logger.warning(f"DBC file in database not found on disk: {file_path}")
                    continue
                
                # Create a new handler for this DBC file
                handler = self.dbc_controller.get_handler(file_path)
                if not handler:
                    # If handler doesn't exist, try to load it
                    self.dbc_controller.import_dbc(None, store_in_db=False, vehicle_id=file_info.get('vehicle_id'))
            
            # Update the handlers list
            self.dbc_list.update_handlers(self.dbc_controller.get_all_handlers())
            
            # Show DBC list and hide vehicle list
            self.vehicle_list_view.setVisible(False)
            self.dbc_list.setVisible(True)
            
            # Update status
            self.statusBar.showMessage(f"Showing all {len(all_dbc_files)} DBC files in database", 5000)
        else:
            self.statusBar.showMessage("Database not enabled, cannot show DBC files", 5000)
        
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

    def load_dbc_files_from_database(self):
        """Load DBC files from the database"""
        if self.dbc_controller.db_service.is_database_enabled():
            self.statusBar.showMessage("Loading DBC files from database...")
            files_loaded = self.dbc_controller.load_dbc_files_from_database()
            
            if files_loaded > 0:
                self.statusBar.showMessage(f"Loaded {files_loaded} DBC files from database", 5000)
        else:
            self.logger.info("Database not enabled, skipping DBC file loading")

    def on_vehicle_selected(self, vehicle):
        """Handle vehicle selection in the main view's left panel"""
        if not vehicle:
            return
            
        # Get the DBC files for this vehicle
        vehicle_files = self.dbc_controller.get_vehicle_dbc_files(vehicle.get('id'))
        
        # Clear current DBC display
        self.dbc_display.clear_display()
        
        # Show vehicle info in status bar
        vehicle_name = vehicle.get('name', 'Unknown')
        make = vehicle.get('make', '')
        model = vehicle.get('model', '')
        
        if make or model:
            vehicle_info = f"{vehicle_name} ({make} {model})".strip()
        else:
            vehicle_info = vehicle_name
            
        dbc_count = len(vehicle_files)
        self.statusBar.showMessage(f"Selected vehicle: {vehicle_info} with {dbc_count} DBC files")
        
        # Create and display vehicle DBC files view
        self.show_vehicle_dbc_files(vehicle, vehicle_files)
        
        # If there's only one DBC file, select it automatically
        if dbc_count == 1:
            file_path = vehicle_files[0].get('filepath')
            handler = self.dbc_controller.get_handler(file_path)
            if handler:
                self.on_handler_selected(handler)
                
    def show_vehicle_dbc_files(self, vehicle, vehicle_files):
        """Display DBC files belonging to the selected vehicle"""
        # Create a temporary widget to display vehicle's DBC files
        if hasattr(self, 'vehicle_dbc_files_widget') and self.vehicle_dbc_files_widget is not None:
            # Remove the existing widget if it exists
            self.left_layout.removeWidget(self.vehicle_dbc_files_widget)
            self.vehicle_dbc_files_widget.deleteLater()
        
        # Create new widget
        self.vehicle_dbc_files_widget = QWidget()
        vdbc_layout = QVBoxLayout(self.vehicle_dbc_files_widget)
        
        # Add header with vehicle name
        vehicle_name = vehicle.get('name', 'Unknown Vehicle')
        header_label = QLabel(f"DBC Files for {vehicle_name}")
        header_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        vdbc_layout.addWidget(header_label)
        
        # Add list of DBC files
        files_list = QListWidget()
        files_list.setMaximumHeight(150)  # Limit height to avoid taking too much space
        
        if not vehicle_files:
            # No DBC files for this vehicle
            item = QListWidgetItem("No DBC files found for this vehicle")
            item.setFlags(item.flags() & ~Qt.ItemIsEnabled)  # Make item non-selectable
            files_list.addItem(item)
        else:
            # Add each DBC file to the list
            for file_info in vehicle_files:
                filename = file_info.get('filename', 'Unknown file')
                item = QListWidgetItem(filename)
                item.setData(Qt.UserRole, file_info)
                files_list.addItem(item)
                
            # Connect to selection
            files_list.itemClicked.connect(self.on_vehicle_dbc_file_clicked)
        
        vdbc_layout.addWidget(files_list)
        
        # Add button to add more DBC files if the user has permission
        if self.auth_service.has_permission("add_dbc"):
            add_dbc_btn = QPushButton("Add DBC to this vehicle")
            add_dbc_btn.clicked.connect(lambda: self.add_dbc_to_vehicle(vehicle))
            vdbc_layout.addWidget(add_dbc_btn)
        
        # Show the widget in the left panel below the vehicle list
        self.left_layout.addWidget(self.vehicle_dbc_files_widget)
        self.vehicle_dbc_files_widget.setVisible(True)
    
    def on_vehicle_dbc_file_clicked(self, item):
        """Handle click on a vehicle's DBC file"""
        file_info = item.data(Qt.UserRole)
        if not file_info:
            return
            
        file_path = file_info.get('filepath')
        if not file_path:
            return
            
        handler = self.dbc_controller.get_handler(file_path)
        
        # If handler doesn't exist, try to load it
        if not handler:
            try:
                # Check if file exists
                import os
                if not os.path.exists(file_path):
                    QMessageBox.warning(
                        self, 
                        "File Not Found",
                        f"The DBC file was not found on the filesystem: {file_path}"
                    )
                    return
                    
                # Load the file
                handler = self.dbc_controller.import_dbc_from_path(file_path, store_in_db=False)
                if not handler:
                    QMessageBox.critical(
                        self,
                        "Load Error",
                        f"Could not load DBC file: {file_path}"
                    )
                    return
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Error loading DBC file: {str(e)}"
                )
                return
        
        # Display the DBC file
        self.on_handler_selected(handler)
    
    def add_dbc_to_vehicle(self, vehicle):
        """Add a DBC file to the selected vehicle"""
        if not self.auth_service.has_permission("add_dbc"):
            QMessageBox.warning(
                self,
                "Permission Denied",
                "You need Netcom Engineer permissions to add DBC files to vehicles."
            )
            return
            
        dialog = DBC_Vehicle_AssignDialog(
            self.dbc_controller,
            self,
            vehicle.get("id")
        )
        dialog.exec_()
        
        # Refresh the vehicle DBC files view
        vehicle_files = self.dbc_controller.get_vehicle_dbc_files(vehicle.get('id'))
        self.show_vehicle_dbc_files(vehicle, vehicle_files)
    
    def on_vehicle_selected_tab(self, vehicle):
        """Handle vehicle selection in the dedicated vehicles tab"""
        # Same as on_vehicle_selected but for tab view
        self.on_vehicle_selected(vehicle) 