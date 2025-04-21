from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QListWidget, 
                            QListWidgetItem, QLabel, QHBoxLayout,
                            QPushButton, QMenu)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from controller.dbc_io_handler import DBC_IO_Handler

class DBCListView(QWidget):
    # Signals emitted when a DBC file is selected or removed
    handler_selected = pyqtSignal(DBC_IO_Handler)  # Emits the selected handler
    handler_removed = pyqtSignal(str)   # Emits the file path of the removed handler
    handler_open_in_new_window = pyqtSignal(DBC_IO_Handler)  # New signal for opening in new window
    
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
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        self.list_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.list_widget)
        
    def show_context_menu(self, position):
        """Show context menu for the list widget"""
        item = self.list_widget.itemAt(position)
        if item:
            handler = item.data(Qt.UserRole)
            if handler:
                menu = QMenu()
                open_in_new_window_action = menu.addAction("Open in New Window")
                action = menu.exec_(self.list_widget.mapToGlobal(position))
                
                if action == open_in_new_window_action:
                    self.handler_open_in_new_window.emit(handler)
        
    def update_handlers(self, handlers):
        """Update the list with the current set of handlers"""
        # Clear the current list
        self.list_widget.clear()
        
        # Add all handlers
        for handler in handlers:
            self.add_handler(handler)
            
    def add_handler(self, handler: DBC_IO_Handler):
        """Add a new DBC handler to the list"""
        # Create a widget to hold the filename and remove button
        item_widget = QWidget()
        item_layout = QHBoxLayout(item_widget)
        item_layout.setContentsMargins(5, 2, 5, 2)
        item_layout.setSpacing(5)
        
        # Add filename label
        file_info = handler.get_file_info()
        name_label = QLabel(file_info["file_name"])
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
        remove_button.clicked.connect(lambda: self.on_remove_clicked(handler.get_file_path()))
        item_layout.addWidget(remove_button)
        
        # Add stretch to push the remove button to the right
        item_layout.addStretch()
        
        # Create list item and set the widget
        item = QListWidgetItem()
        item.setData(Qt.UserRole, handler)  # Store handler as item data
        item.setSizeHint(item_widget.sizeHint())
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, item_widget)
        
    def on_remove_clicked(self, file_path):
        """Handle remove button click by emitting the remove signal"""
        self.handler_removed.emit(file_path)
                
    def on_selection_changed(self):
        """Handle selection changes in the list"""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            handler = selected_items[0].data(Qt.UserRole)
            self.handler_selected.emit(handler)
            
    def get_selected_handler(self):
        """Get the currently selected handler"""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None
        
    def remove_item_by_file_path(self, file_path):
        """Remove an item from the list widget by its file path"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            handler = item.data(Qt.UserRole)
            if handler.get_file_path() == file_path:
                self.list_widget.takeItem(i)
                break 

    def select_handler(self, handler):
        """Programmatically select a handler in the list"""
        # Find the item with the matching handler
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.UserRole) == handler:
                # Select the item, which will trigger on_selection_changed
                self.list_widget.setCurrentItem(item)
                break 