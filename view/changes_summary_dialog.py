from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTextEdit, QDialogButtonBox, QSizePolicy)
from PyQt5.QtCore import Qt

class ChangesSummaryDialog(QDialog):
    """Dialog for displaying changes summary with a scrollable text area"""
    
    # Result codes
    EXPORT_CHANGES = 3  # Custom result code for Export Changes button
    
    def __init__(self, changes_summary, parent=None):
        """
        Initialize the changes summary dialog.
        
        Args:
            changes_summary (str): The changes summary text to display
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        self.changes_summary = changes_summary
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle("Changes Summary")
        self.setMinimumSize(600, 400)
        self.setMaximumSize(800, 600)  # Allow a bit of resize flexibility but cap it
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Add title label
        title_label = QLabel("The following changes have been made:")
        title_label.setStyleSheet("font-weight: bold; font-size: 12px;")
        main_layout.addWidget(title_label)
        
        # Create text edit for displaying changes
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(self.changes_summary)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        
        # Set a monospaced font for better formatting
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, Courier New, monospace;
                font-size: 10pt;
                background-color: white;
                border: 1px solid #d0d0d0;
            }
        """)
        
        main_layout.addWidget(self.text_edit)
        
        # Add question label
        question_label = QLabel("Do you want to proceed with the export?")
        main_layout.addWidget(question_label)
        
        # Create button layout
        button_layout = QHBoxLayout()
        
        # Add Export Changes button
        export_button = QPushButton("Export Changes")
        export_button.clicked.connect(self.export_changes)
        button_layout.addWidget(export_button)
        
        button_layout.addStretch()
        
        # Add Yes/No buttons
        yes_button = QPushButton("Yes")
        yes_button.clicked.connect(self.accept)
        no_button = QPushButton("No")
        no_button.clicked.connect(self.reject)
        
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        
        main_layout.addLayout(button_layout)
        
    def export_changes(self):
        """Handle Export Changes button click"""
        self.done(ChangesSummaryDialog.EXPORT_CHANGES) 