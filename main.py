import sys
from PyQt5.QtWidgets import QApplication
from view.main_window import MainWindow
from utils.logger import setup_logging
from utils import config

def main():
    # Set up logging first
    logger = setup_logging(config.get("logging"))
    logger.info("Starting DBC Master application")
    
    # Create the application
    app = QApplication(sys.argv)
    app.setApplicationName("DBC Master")
    app.setOrganizationName("Your Company")
    app.setOrganizationDomain("example.com")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    # Start the event loop
    exit_code = app.exec_()
    
    # Clean up resources
    logger.info("Shutting down DBC Master application")
    
    # Exit with the app's exit code
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
