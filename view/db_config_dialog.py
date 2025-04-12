from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QComboBox, QCheckBox, 
    QPushButton, QSpinBox, QGroupBox, 
    QMessageBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from utils import config, db_manager
from utils.db_service import DBCDatabaseService
import logging

class DatabaseConfigDialog(QDialog):
    """
    Dialog for configuring PostgreSQL database connection settings.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger(__name__)
        self.db_service = DBCDatabaseService()
        
        self.setWindowTitle("Database Configuration")
        self.setMinimumWidth(450)
        
        self.initUI()
        self.loadCurrentConfig()
        
    def initUI(self):
        """Initialize the dialog UI components"""
        main_layout = QVBoxLayout(self)
        
        # Database enable checkbox
        self.enable_db = QCheckBox("Enable PostgreSQL Database")
        self.enable_db.stateChanged.connect(self.onEnableStateChanged)
        main_layout.addWidget(self.enable_db)
        
        # Database connection group
        self.conn_group = QGroupBox("Connection Settings")
        conn_layout = QFormLayout(self.conn_group)
        
        # Host settings
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("localhost")
        conn_layout.addRow("Host:", self.host_input)
        
        # Port settings
        self.port_input = QSpinBox()
        self.port_input.setRange(1, 65535)
        self.port_input.setValue(5432)
        conn_layout.addRow("Port:", self.port_input)
        
        # Database name
        self.db_name_input = QLineEdit()
        self.db_name_input.setPlaceholderText("dbc_viewer")
        conn_layout.addRow("Database:", self.db_name_input)
        
        # Username
        self.username_input = QLineEdit()
        conn_layout.addRow("Username:", self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        conn_layout.addRow("Password:", self.password_input)
        
        # SSL Mode
        self.ssl_mode_combo = QComboBox()
        self.ssl_mode_combo.addItems(["prefer", "require", "disable", "verify-ca", "verify-full"])
        conn_layout.addRow("SSL Mode:", self.ssl_mode_combo)
        
        main_layout.addWidget(self.conn_group)
        
        # Test connection button
        test_btn = QPushButton("Test Connection")
        test_btn.clicked.connect(self.testConnection)
        main_layout.addWidget(test_btn)
        
        # Buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.saveConfig)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
    
    def loadCurrentConfig(self):
        """Load current configuration values into the form"""
        db_config = config.get("database")
        
        if not db_config:
            return
            
        self.enable_db.setChecked(db_config.get("enabled", False))
        self.host_input.setText(db_config.get("host", "localhost"))
        self.port_input.setValue(db_config.get("port", 5432))
        self.db_name_input.setText(db_config.get("database", "dbc_viewer"))
        self.username_input.setText(db_config.get("username", ""))
        self.password_input.setText(db_config.get("password", ""))
        
        # Set SSL mode
        ssl_mode = db_config.get("ssl_mode", "prefer")
        index = self.ssl_mode_combo.findText(ssl_mode)
        if index >= 0:
            self.ssl_mode_combo.setCurrentIndex(index)
            
        # Update UI based on enabled state
        self.onEnableStateChanged(self.enable_db.isChecked())
    
    def onEnableStateChanged(self, state):
        """Enable or disable form fields based on checkbox state"""
        enabled = bool(state)
        self.conn_group.setEnabled(enabled)
    
    def getFormValues(self):
        """Get the current form values as a dictionary"""
        return {
            "enabled": self.enable_db.isChecked(),
            "host": self.host_input.text().strip(),
            "port": self.port_input.value(),
            "database": self.db_name_input.text().strip(),
            "username": self.username_input.text().strip(),
            "password": self.password_input.text().strip(),
            "ssl_mode": self.ssl_mode_combo.currentText()
        }
    
    def testConnection(self):
        """Test the database connection with the current form values"""
        # Get values from form
        values = self.getFormValues()
        
        if not values["enabled"]:
            QMessageBox.information(
                self, 
                "Database Connection", 
                "Database is not enabled. Enable it to test the connection."
            )
            return
            
        # Check required fields
        if not values["host"] or not values["database"]:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Host and database name are required fields."
            )
            return
            
        # Create a temporary database manager for testing
        test_db = DatabaseConfigDialog.create_test_connection(values)
        
        if test_db:
            QMessageBox.information(
                self,
                "Connection Successful",
                "Successfully connected to the database."
            )
            
            # Clean up test connection
            test_db.dispose()
        else:
            QMessageBox.critical(
                self,
                "Connection Failed",
                "Failed to connect to the database. Please check your settings."
            )
    
    @staticmethod
    def create_test_connection(values):
        """
        Create a test database connection with the given values.
        
        Returns:
            DatabaseManager or None: Database manager if connection successful, None otherwise
        """
        from utils.db_manager import DatabaseManager
        
        # Build connection string
        conn_string = "postgresql://"
        
        # Add username and password if provided
        if values["username"]:
            conn_string += values["username"]
            if values["password"]:
                conn_string += f":{values['password']}"
            conn_string += "@"
        
        # Add host and port
        conn_string += f"{values['host']}:{values['port']}"
        
        # Add database name
        conn_string += f"/{values['database']}"
        
        # Add SSL mode if not default
        if values["ssl_mode"] != "prefer":
            conn_string += f"?sslmode={values['ssl_mode']}"
        
        # Create test database manager
        test_db = DatabaseManager()
        if test_db.initialize(conn_string):
            return test_db
        
        return None
    
    def saveConfig(self):
        """Save the form values to configuration and initialize database"""
        values = self.getFormValues()
        
        # Update configuration
        db_config = config.get("database")
        
        for key, value in values.items():
            config.set("database", key, value)
        
        # Save configuration to file
        if config.save_config():
            self.logger.info("Database configuration saved")
            
            # If database is enabled, try to initialize it
            if values["enabled"]:
                # Reinitialize database
                if self.db_service.init_database():
                    self.logger.info("Database initialized successfully")
                else:
                    self.logger.warning("Failed to initialize database")
                    QMessageBox.warning(
                        self,
                        "Database Initialization",
                        "Database configuration was saved, but initialization failed. "
                        "The application will continue without database functionality."
                    )
            else:
                # Database disabled, dispose of any existing connections
                db_manager.dispose()
            
            # Accept dialog (close with success)
            self.accept()
        else:
            self.logger.error("Failed to save database configuration")
            QMessageBox.critical(
                self,
                "Configuration Error",
                "Failed to save database configuration."
            ) 