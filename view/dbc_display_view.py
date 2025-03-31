from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTreeWidget, QTreeWidgetItem,
                            QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from controller.dbc_io_handler import DBC_IO_Handler

class DBCDisplayView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(5)
        
        # File info section
        self.file_name_label = QLabel("File: No file selected")
        self.file_name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.file_name_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                padding: 2px;
                background-color: #f0f0f0;
                border-bottom: 1px solid #d0d0d0;
            }
        """)
        layout.addWidget(self.file_name_label)
        
        # Node tree view
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)  # Hide the header since we'll use root item
        self.tree_widget.setStyleSheet("""
            QTreeWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QTreeWidget::item {
                height: 25px;
            }
            QTreeWidget::item:hover {
                background-color: #e8e8e8;
            }
            QTreeWidget::item:selected {
                background-color: #e0e0e0;
                color: black;
            }
        """)
        layout.addWidget(self.tree_widget)
        
    def update_display(self, handler: DBC_IO_Handler):
        """Update the display with information from the handler"""
        if not handler or not handler.is_valid():
            self.clear_display()
            return
            
        # Update file name
        file_info = handler.get_file_info()
        self.file_name_label.setText(f"File: {file_info['file_name']}")
        
        # Update nodes tree
        self.tree_widget.clear()
        nodes = handler.get_nodes()
        
        # Create root item for Network nodes
        root_item = QTreeWidgetItem(self.tree_widget)
        root_item.setText(0, "Network nodes")
        root_item.setExpanded(True)  # Expand by default
        
        # Add nodes as children of the root item
        for node in nodes:
            node_item = QTreeWidgetItem(root_item)
            node_item.setText(0, node['name'])
            node_item.setIcon(0, self.get_node_icon())  # Add icon to node
            
    def get_node_icon(self):
        """Returns a default icon for nodes"""
        # You can replace this with actual icon loading
        return QIcon()
            
    def clear_display(self):
        """Clear all displayed information"""
        self.file_name_label.setText("File: No file selected")
        self.tree_widget.clear() 