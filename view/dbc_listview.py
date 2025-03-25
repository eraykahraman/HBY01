from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                            QListWidgetItem, QLabel, QHBoxLayout,
                            QPushButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon

class DBCListView(QWidget):
    # Signals emitted when a DBC file is selected or removed
    dbc_selected = pyqtSignal(str)  # Emits the file path of the selected DBC
    dbc_removed = pyqtSignal(str)   # Emits the file path of the removed DBC
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add title label
        title = QLabel("Loaded DBC Files")
        title.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Create list widget
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.SingleSelection)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        layout.addWidget(self.list_widget)
        
    def add_dbc_file(self, file_path):
        """Add a new DBC file to the list"""
        # Create a widget to hold the filename and remove button
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 2, 5, 2)
        item_layout.setSpacing(5)
        
        # Add filename label
        file_name = file_path.split('/')[-1]
        name_label = QLabel(file_name)
        name_label.setStyleSheet("padding: 2px;")
        item_layout.addWidget(name_label)
        
        # Add remove button
        remove_button = QPushButton("×")
        remove_button.setFixedSize(20, 20)
        remove_button.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: white;
                border: none;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #ff6666;
            }
        """)
        remove_button.clicked.connect(lambda: self.on_remove_clicked(file_path))
        item_layout.addWidget(remove_button)
        
        # Add stretch to push the remove button to the right
        item_layout.addStretch()
        
        # Create list item and set the widget
        item = QListWidgetItem()
        item.setData(Qt.UserRole, file_path)  # Store full path as item data
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)
        
    def on_remove_clicked(self, file_path):
        """Handle remove button click by emitting the remove signal"""
        self.dbc_removed.emit(file_path)
                
    def on_item_clicked(self, item):
        """Handle click on an item in the list"""
        file_path = item.data(Qt.UserRole)
        self.dbc_selected.emit(file_path)
            
    def get_selected_dbc(self):
        """Get the currently selected DBC file path"""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None 