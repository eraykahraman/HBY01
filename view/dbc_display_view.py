from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTreeWidget, QTreeWidgetItem, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal

class DBCDisplayView(QMainWindow):
    # Signal emitted when window is closed
    window_closed = pyqtSignal(str)  # Emits file_path of the associated DBC
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DBC Content Viewer")
        self.setGeometry(200, 200, 800, 600)
        
        # Property to store which DBC file this view is for
        self.dbc_file_path = None
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tree widget for hierarchical display
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["DBC Content"])
        self.tree.setColumnCount(1)
        layout.addWidget(self.tree)
        
    def display_dbc_content(self, instance_id):
        """Display the content of a DBC file in the tree view"""
        self.tree.clear()
        self.dbc_file_path = instance_id
        
        # Get the DBC content from the controller
        db = self.parent().dbc_controller.get_dbc(instance_id)
        if not db:
            return
            
        # Create root item with instance ID
        root = QTreeWidgetItem(self.tree)
        root.setText(0, f"DBC Instance: {instance_id}")
        root.setExpanded(True)
        
        # Add messages
        messages_item = QTreeWidgetItem(root)
        messages_item.setText(0, "Messages")
        messages_item.setExpanded(True)
        
        for msg in db.messages:
            msg_item = QTreeWidgetItem(messages_item)
            msg_item.setText(0, msg.name)
            
            # Add signals for this message
            signals_item = QTreeWidgetItem(msg_item)
            signals_item.setText(0, "Signals")
            for signal in msg.signals:
                signal_item = QTreeWidgetItem(signals_item)
                signal_item.setText(0, signal.name)

    def closeEvent(self, event):
        """Handle window close event"""
        # Emit signal that this window is closing
        if self.dbc_file_path:
            self.window_closed.emit(self.dbc_file_path)
        super().closeEvent(event) 