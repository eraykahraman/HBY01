from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTreeWidget, QTreeWidgetItem, QLabel,
                            QSplitter, QTableWidget, QTableWidgetItem,
                            QHeaderView, QHBoxLayout, QLineEdit,
                            QComboBox, QPushButton, QFrame, QStyledItemDelegate)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from view.message_detail_view import MessageDetailView

class FilterHeaderView(QHeaderView):
    """Custom header view with built-in filters"""
    
    def __init__(self, parent=None):
        super().__init__(Qt.Horizontal, parent)
        self.setSectionsClickable(True)
        self.setHighlightSections(True)
        self.setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setStretchLastSection(True)
        
        # Store filter widgets
        self.filter_widgets = {}
        
    def setFilterWidget(self, section, widget):
        """Set the filter widget for a section"""
        self.filter_widgets[section] = widget
        
    def filterWidget(self, section):
        """Get the filter widget for a section"""
        return self.filter_widgets.get(section)

class DBCDisplayView(QMainWindow):
    # Signal emitted when window is closed
    window_closed = pyqtSignal(str)  # Emits file_path of the associated DBC
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("DBC Content Viewer")
        self.setGeometry(200, 200, 1000, 700)
        
        # Property to store which DBC file this view is for
        self.dbc_file_path = None
        
        # Keep track of open message detail views
        self.open_detail_views = []
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create splitter for tree and details view
        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # Create tree widget for hierarchical display (LEFT SIDE)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["DBC Content"])
        self.tree.setColumnCount(1)
        self.tree.itemClicked.connect(self.on_tree_item_clicked)
        self.splitter.addWidget(self.tree)
        
        # Create right side container with layout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.splitter.addWidget(right_widget)
        
        # Column names for reference
        self.column_names = [
            "ID (HEX)", "Name", "Length (Bytes)", "Signals", 
            "Extended Frame", "Cycle Time (ms)", "Senders", 
            "Bus Name", "Comment"
        ]
        
        # Create table widget for detailed view
        self.setup_table()
        right_layout.addWidget(self.table)
        
        # Add clear filters button
        clear_btn = QPushButton("Clear Filters")
        clear_btn.clicked.connect(self.clear_filters)
        right_layout.addWidget(clear_btn)
        
        # Store original messages for filtering
        self.all_messages = []
        
        # Set initial sizes for splitter
        self.splitter.setSizes([300, 700])  # 30% left, 70% right
    
    def setup_table(self):
        """Setup the table with embedded filters in header"""
        self.table = QTableWidget()
        self.table.setColumnCount(len(self.column_names))
        
        # We'll manage sorting ourselves without Qt's built-in mechanism
        self.table.setSortingEnabled(False)
        
        # Variables to track current sort
        self.current_sort_column = -1
        self.current_sort_order = Qt.AscendingOrder
        
        # Connect to item double-click for message details
        self.table.cellDoubleClicked.connect(self.on_table_cell_double_clicked)
        
        # Make sort indicators more visible
        self.table.setStyleSheet("""
            QHeaderView::down-arrow { 
                width: 12px; 
                height: 12px; 
                background: #007bff;
                padding: 2px;
                border-radius: 6px;
            }
            QHeaderView::up-arrow { 
                width: 12px; 
                height: 12px; 
                background: #007bff;
                padding: 2px;
                border-radius: 6px;
            }
        """)
        
        # Set up header with filter widgets
        self.filters = {}
        
        # Create filter row (1 row below the header)
        self.table.setRowCount(0)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setVisible(True)
        self.table.setHorizontalHeaderLabels(self.column_names)
        
        # Connect header click to manage sorting and filters
        self.table.horizontalHeader().sectionClicked.connect(self.on_header_clicked)
        
        # Make the table have two header rows - increase height to avoid overlap
        base_height = self.table.horizontalHeader().height()
        # We'll make the header taller to accommodate both the text and filters without overlap
        self.table.horizontalHeader().setFixedHeight(int(base_height * 2.5))
        
        # Add the filter widgets below each column header
        for i, col_name in enumerate(self.column_names):
            # Create filter widget based on column type
            if col_name == "Extended Frame":
                filter_widget = QComboBox(self.table)
                filter_widget.addItems(["All", "Yes", "No"])
                filter_widget.setStyleSheet("""
                    QComboBox { 
                        border: 1px solid #ccc; 
                        border-radius: 3px; 
                        background-color: white;
                        padding: 1px 3px;
                    }
                """)
                filter_widget.currentTextChanged.connect(self.apply_filters)
            else:
                filter_widget = QLineEdit(self.table)
                filter_widget.setPlaceholderText(f"Filter {col_name}")
                filter_widget.setStyleSheet("""
                    QLineEdit { 
                        border: 1px solid #ccc; 
                        border-radius: 3px; 
                        background-color: white;
                        padding: 1px 3px;
                    }
                """)
                filter_widget.textChanged.connect(self.apply_filters)
            
            # Set filter widget and add to collection
            filter_widget.setParent(self.table)
            self.filters[i] = filter_widget
        
        # Set up a timer to position the filter widgets
        self.table.horizontalHeader().sectionResized.connect(self.position_filter_widgets)
        self.table.horizontalScrollBar().valueChanged.connect(self.position_filter_widgets)
        
        # Setup horizontal header options
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)  # Stretch the comment column
    
    def resizeEvent(self, event):
        """Handle resize event to reposition filter widgets"""
        super().resizeEvent(event)
        self.position_filter_widgets()
    
    def showEvent(self, event):
        """Handle show event"""
        super().showEvent(event)
        self.position_filter_widgets()
    
    def position_filter_widgets(self):
        """Position filter widgets below the headers"""
        header = self.table.horizontalHeader()
        # Calculate positions to avoid overlap - filters start well below header text
        header_height = header.height()
        filter_top = int(header_height * 0.6)  # Position filters in the lower portion of the header
        
        for i, widget in self.filters.items():
            left = header.sectionPosition(i) - self.table.horizontalScrollBar().value()
            width = header.sectionSize(i)
            
            # Calculate height for filter based on widget type
            height = int(min(24, header_height * 0.35))  # Limit height to avoid overflow
            
            # Position widget below the header text with proper spacing
            widget.setGeometry(left + 3, filter_top, width - 6, height)
            widget.setVisible(True)
        
    def display_dbc_content(self, instance_id):
        """Display the content of a DBC file in the tree view"""
        self.tree.clear()
        self.table.clearContents()
        self.table.setRowCount(0)
        self.dbc_file_path = instance_id
        
        # Get the DBC content from the controller
        self.db = self.parent().dbc_controller.get_dbc(instance_id)
        if not self.db:
            return
            
        # Create root item with instance ID
        root = QTreeWidgetItem(self.tree)
        root.setText(0, f"DBC Instance: {instance_id}")
        root.setExpanded(True)
        
        # Add messages
        self.messages_item = QTreeWidgetItem(root)
        self.messages_item.setText(0, "Messages")
        self.messages_item.setExpanded(True)
        
        for msg in self.db.messages:
            msg_item = QTreeWidgetItem(self.messages_item)
            msg_item.setText(0, msg.name)
            
            # Add signals for this message
            signals_item = QTreeWidgetItem(msg_item)
            signals_item.setText(0, "Signals")
            for signal in msg.signals:
                signal_item = QTreeWidgetItem(signals_item)
                signal_item.setText(0, signal.name)
    
    def on_tree_item_clicked(self, item, column):
        """Handle clicks on tree items to update the table view"""
        # Check if this is a message node (parent is the Messages node)
        if item.parent() == self.messages_item:
            # Get the message name and find the corresponding message object
            msg_name = item.text(0)
            for msg in self.db.messages:
                if msg.name == msg_name:
                    self.show_message_details(msg)
                    return
        
        # Handle the existing Messages node click
        if item == self.messages_item:
            self.populate_messages_table()
    
    def on_table_cell_double_clicked(self, row, column):
        """Handle double clicks on table cells to show message details"""
        # Get the ID from the first column of the clicked row
        id_item = self.table.item(row, 0)
        if id_item:
            hex_id = id_item.text()
            # Find the matching message from all_messages
            for msg in self.all_messages:
                if f"0x{msg.frame_id:X}" == hex_id:
                    self.show_message_details(msg)
                    break
    
    def show_message_details(self, message):
        """Show detailed message information in a popup"""
        # Create a non-modal dialog with DBC file information
        detail_view = MessageDetailView(self, message, self.dbc_file_path)
        
        # Keep a reference to prevent garbage collection
        self.open_detail_views.append(detail_view)
        
        # Connect the dialog's finished signal to remove it from our list
        detail_view.finished.connect(lambda: self.remove_detail_view(detail_view))
        
        # Show the dialog as non-modal
        detail_view.show()
    
    def remove_detail_view(self, view):
        """Remove a detail view from our tracking list when it's closed"""
        if view in self.open_detail_views:
            self.open_detail_views.remove(view)
    
    def populate_messages_table(self):
        """Populate the table with message details when Messages node is clicked"""
        self.table.clearContents()
        self.all_messages = self.db.messages
        self.apply_filters()
        
    def clear_filters(self):
        """Clear all filter inputs"""
        for filter_widget in self.filters.values():
            if isinstance(filter_widget, QLineEdit):
                filter_widget.clear()
            elif isinstance(filter_widget, QComboBox):
                filter_widget.setCurrentIndex(0)
        
        # Reapply filters (which will show all messages)
        self.apply_filters()
        
    def on_header_clicked(self, logical_index):
        """Handle sorting when a header is clicked"""
        # Toggle sort order if clicking the same column
        if self.current_sort_column == logical_index:
            # Toggle sort order
            if self.current_sort_order == Qt.AscendingOrder:
                self.current_sort_order = Qt.DescendingOrder
            else:
                self.current_sort_order = Qt.AscendingOrder
        else:
            # New column, default to ascending
            self.current_sort_column = logical_index
            self.current_sort_order = Qt.AscendingOrder
        
        # Apply the sort indicator to the header
        self.table.horizontalHeader().setSortIndicator(logical_index, self.current_sort_order)
        
        # Sort the filtered messages
        self.sort_table(self.current_sort_column, self.current_sort_order)
        
        # Make sure our filters are visible after sorting
        self.position_filter_widgets()
    
    def sort_table(self, column, order):
        """Sort the table content by a specific column"""
        if not hasattr(self, 'all_messages') or not self.all_messages:
            return
            
        # Get current filtered messages
        if self.table.rowCount() == 0:
            return
            
        # Collect the currently visible messages
        current_messages = []
        for row in range(self.table.rowCount()):
            # Get ID from first column to find the message object
            id_item = self.table.item(row, 0)
            if id_item:
                hex_id = id_item.text()
                # Find the matching message from all_messages
                for msg in self.all_messages:
                    if f"0x{msg.frame_id:X}" == hex_id:
                        current_messages.append(msg)
                        break
        
        # Sort the messages based on the column clicked
        def get_sort_key(msg):
            value = self.get_message_column_value(msg, column)
            # Special handling for hex IDs
            if column == 0:  # ID column
                # Convert hex to int for proper numerical sorting
                try:
                    return int(value, 16)
                except ValueError:
                    return 0
            # For other columns, use string comparison
            return str(value).lower()
        
        current_messages.sort(key=get_sort_key, reverse=(order == Qt.DescendingOrder))
        
        # Redisplay the sorted messages
        self.table.clearContents()
        self.table.setRowCount(len(current_messages))
        for row, msg in enumerate(current_messages):
            self.populate_message_row(row, msg)
    
    def apply_filters(self):
        """Apply all filters to the messages table"""
        if not hasattr(self, 'all_messages') or not self.all_messages:
            return
            
        # Clear previous table content
        self.table.clearContents()
        self.table.setRowCount(0)
        
        filtered_messages = []
        
        # Apply each filter
        for msg in self.all_messages:
            match = True
            
            # Check each column's filter
            for col, filter_widget in self.filters.items():
                filter_text = ""
                if isinstance(filter_widget, QLineEdit):
                    filter_text = filter_widget.text().lower()
                elif isinstance(filter_widget, QComboBox) and filter_widget.currentText() != "All":
                    filter_text = filter_widget.currentText().lower()
                
                if not filter_text:  # Skip empty filters
                    continue
                    
                # Get column value based on column index
                value = self.get_message_column_value(msg, col)
                
                # Apply filter (case insensitive)
                if filter_text and str(value).lower().find(filter_text) == -1:
                    match = False
                    break
            
            if match:
                filtered_messages.append(msg)
        
        # Display filtered messages
        self.table.setRowCount(len(filtered_messages))
        for row, msg in enumerate(filtered_messages):
            self.populate_message_row(row, msg)
        
        # Apply current sort if any
        if self.current_sort_column >= 0:
            self.sort_table(self.current_sort_column, self.current_sort_order)
    
    def get_message_column_value(self, msg, col):
        """Get the value for a specific column from a message object"""
        if col == 0:  # ID (HEX)
            return f"0x{msg.frame_id:X}"
        elif col == 1:  # Name
            return msg.name
        elif col == 2:  # Length
            return str(msg.length)
        elif col == 3:  # Signal count
            return str(len(msg.signals))
        elif col == 4:  # Extended Frame
            return "Yes" if getattr(msg, 'is_extended_frame', False) else "No"
        elif col == 5:  # Cycle Time
            cycle_time = getattr(msg, 'cycle_time', None)
            return str(cycle_time) if cycle_time is not None else "N/A"
        elif col == 6:  # Senders
            senders = getattr(msg, 'senders', [])
            return ", ".join(senders) if senders else "N/A"
        elif col == 7:  # Bus Name
            bus_name = getattr(msg, 'bus_name', None)
            return bus_name if bus_name else "N/A"
        elif col == 8:  # Comment
            comment = getattr(msg, 'comment', None)
            return comment if comment else ""
        
        return ""
    
    def populate_message_row(self, row, msg):
        """Populate a single table row with message data"""
        # ID (in hex)
        id_item = QTableWidgetItem(f"0x{msg.frame_id:X}")
        self.table.setItem(row, 0, id_item)
        
        # Name
        name_item = QTableWidgetItem(msg.name)
        self.table.setItem(row, 1, name_item)
        
        # Length
        length_item = QTableWidgetItem(str(msg.length))
        self.table.setItem(row, 2, length_item)
        
        # Signal count
        signal_count_item = QTableWidgetItem(str(len(msg.signals)))
        self.table.setItem(row, 3, signal_count_item)
        
        # Extended Frame
        is_extended = getattr(msg, 'is_extended_frame', False)
        extended_item = QTableWidgetItem("Yes" if is_extended else "No")
        self.table.setItem(row, 4, extended_item)
        
        # Cycle Time
        cycle_time = getattr(msg, 'cycle_time', None)
        cycle_time_item = QTableWidgetItem(str(cycle_time) if cycle_time is not None else "N/A")
        self.table.setItem(row, 5, cycle_time_item)
        
        # Senders
        senders = getattr(msg, 'senders', [])
        senders_text = ", ".join(senders) if senders else "N/A"
        senders_item = QTableWidgetItem(senders_text)
        self.table.setItem(row, 6, senders_item)
        
        # Bus Name
        bus_name = getattr(msg, 'bus_name', None)
        bus_name_item = QTableWidgetItem(bus_name if bus_name else "N/A")
        self.table.setItem(row, 7, bus_name_item)
        
        # Comment
        comment = getattr(msg, 'comment', None)
        comment_item = QTableWidgetItem(comment if comment else "")
        self.table.setItem(row, 8, comment_item)

    def closeEvent(self, event):
        """Handle window close event"""
        # Close all open detail views
        for view in self.open_detail_views[:]:
            view.close()
            
        # Emit signal that this window is closing
        if self.dbc_file_path:
            self.window_closed.emit(self.dbc_file_path)
        super().closeEvent(event) 