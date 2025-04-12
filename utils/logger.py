import logging
import os
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(config=None):
    """
    Configure logging for the application.
    
    Args:
        config (dict, optional): Logging configuration dictionary
            If None, uses default configuration
    
    Returns:
        logger: Root logger instance
    """
    # Get the root logger
    logger = logging.getLogger()
    
    # Clear any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Default configuration if not provided
    if config is None:
        config = {
            "level": "INFO",
            "file_logging": True,
            "log_file": "app.log"
        }
    
    # Set the log level
    level_name = config.get("level", "INFO")
    level = getattr(logging, level_name.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Add file handler if enabled
    if config.get("file_logging", True):
        # Get log directory
        log_dir = _get_log_dir()
        
        # Get log filename, adding date if not already in the name
        log_file = config.get("log_file", "app.log")
        if not any(x in log_file for x in ['%d', '%m', '%Y', '%y']):
            # Add date to filename
            base, ext = os.path.splitext(log_file)
            date_str = datetime.now().strftime('%Y%m%d')
            log_file = f"{base}_{date_str}{ext}"
        
        # Create full log path
        log_path = os.path.join(log_dir, log_file)
        
        try:
            # Create file handler
            file_handler = logging.FileHandler(log_path, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            
            # Add file handler to logger
            logger.addHandler(file_handler)
            
            logger.info(f"Logging to file: {log_path}")
        except Exception as e:
            logger.error(f"Failed to set up file logging: {str(e)}")
    
    return logger

def _get_log_dir():
    """
    Get the log directory path.
    Creates it if it doesn't exist.
    
    Returns:
        str: Path to the log directory
    """
    # Get the user's home directory
    home_dir = Path.home()
    
    # Create app logs directory
    log_dir = os.path.join(home_dir, ".dbc_viewer", "logs")
    
    # Create the directory if it doesn't exist
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir, exist_ok=True)
        except Exception:
            # Fallback to current directory if home directory is not accessible
            log_dir = os.path.join(os.path.abspath('.'), "logs")
            os.makedirs(log_dir, exist_ok=True)
    
    return log_dir 