import os
import json
import logging
from pathlib import Path

class Config:
    """
    Configuration manager for the application.
    Handles loading and saving configuration settings.
    """
    
    # Default configuration values
    DEFAULT_CONFIG = {
        "database": {
            "enabled": False,
            "host": "localhost",
            "port": 5432,
            "database": "dbc_viewer",
            "username": "erayswe599",
            "password": "s7s5dbaE",
            "ssl_mode": "prefer"
        },
        "application": {
            "theme": "system",
            "language": "en",
            "auto_save": True,
            "save_interval": 300,  # seconds
            "recent_files_limit": 10
        },
        "logging": {
            "level": "INFO",
            "file_logging": True,
            "log_file": "app.log"
        }
    }
    
    def __init__(self):
        """Initialize the configuration manager."""
        self.logger = logging.getLogger(__name__)
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def _get_config_dir(self):
        """
        Get the configuration directory path.
        Creates it if it doesn't exist.
        
        Returns:
            Path: Path to the configuration directory
        """
        # Get the user's home directory
        home_dir = Path.home()
        
        # Create app config directory
        config_dir = home_dir / ".dbc_viewer"
        
        # Create the directory if it doesn't exist
        if not config_dir.exists():
            try:
                config_dir.mkdir(exist_ok=True)
                self.logger.info(f"Created configuration directory: {config_dir}")
            except Exception as e:
                self.logger.error(f"Failed to create configuration directory: {str(e)}")
                # Fallback to current directory if home directory is not accessible
                config_dir = Path(".") / ".dbc_viewer"
                config_dir.mkdir(exist_ok=True)
        
        return config_dir
    
    def load_config(self):
        """
        Load configuration from file.
        If file doesn't exist, creates it with default values.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if not self.config_file.exists():
            self.logger.info("Configuration file not found, creating with defaults")
            return self.save_config()
        
        try:
            with open(self.config_file, 'r') as f:
                loaded_config = json.load(f)
            
            # Update config with loaded values, preserving defaults for missing keys
            self._update_dict_recursive(self.config, loaded_config)
            self.logger.info("Configuration loaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return False
    
    def save_config(self):
        """
        Save current configuration to file.
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def _update_dict_recursive(self, base_dict, new_dict):
        """
        Recursively update a dictionary with values from another dictionary.
        Only updates keys that already exist in the base dictionary.
        
        Args:
            base_dict (dict): Base dictionary to update
            new_dict (dict): Dictionary with new values
        """
        for key, value in new_dict.items():
            if key in base_dict:
                if isinstance(value, dict) and isinstance(base_dict[key], dict):
                    self._update_dict_recursive(base_dict[key], value)
                else:
                    base_dict[key] = value
    
    def get_db_connection_string(self):
        """
        Get SQLAlchemy connection string for the database.
        
        Returns:
            str: Connection string or None if database is disabled
        """
        db_config = self.config["database"]
        
        if not db_config["enabled"]:
            return None
        
        # Use a simpler connection string format that explicitly includes all parameters
        conn_string = (
            f"postgresql://{db_config['username']}:{db_config['password']}@"
            f"{db_config['host']}:{db_config['port']}/{db_config['database']}"
        )
        
        # Log the connection string (without password)
        masked_conn_string = conn_string.replace(db_config['password'], '***')
        self.logger.info(f"Using connection string: {masked_conn_string}")
        
        return conn_string
    
    def get(self, section, key=None):
        """
        Get a configuration value.
        
        Args:
            section (str): Configuration section
            key (str, optional): Configuration key within section
                                If None, returns the entire section
        
        Returns:
            The configuration value or None if not found
        """
        if section not in self.config:
            return None
        
        if key is None:
            return self.config[section]
        
        return self.config[section].get(key)
    
    def set(self, section, key, value):
        """
        Set a configuration value.
        
        Args:
            section (str): Configuration section
            key (str): Configuration key within section
            value: Value to set
        
        Returns:
            bool: True if set successfully, False otherwise
        """
        if section not in self.config:
            self.logger.error(f"Configuration section '{section}' not found")
            return False
        
        try:
            self.config[section][key] = value
            return True
        except Exception as e:
            self.logger.error(f"Failed to set configuration value: {str(e)}")
            return False 