from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QTreeWidget, QTreeWidgetItem, QLabel,
                            QSplitter, QTableWidget, QTableWidgetItem,
                            QHeaderView, QHBoxLayout, QLineEdit,
                            QComboBox, QPushButton, QFrame, QStyledItemDelegate,
                            QToolButton, QStyle)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor
from view.message_detail_view import MessageDetailView
import sip

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
        
        # Set up a timer to position the filter widgets
        self.table.horizontalHeader().sectionResized.connect(self.position_filter_widgets)
        self.table.horizontalScrollBar().valueChanged.connect(self.position_filter_widgets)
        
        # Setup horizontal header options - Make columns resizable by user
        header = self.table.horizontalHeader()
        
        # Configure column resize behavior - Interactive allows user to resize
        for i in range(len(self.column_names)):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set initial default column widths
        header.resizeSection(0, 100)  # ID column
        header.resizeSection(1, 150)  # Name column
        header.resizeSection(2, 80)   # Length column
        header.resizeSection(3, 80)   # Signals column
        header.resizeSection(4, 100)  # Extended Frame
        header.resizeSection(5, 100)  # Cycle Time
        header.resizeSection(6, 120)  # Senders
        header.resizeSection(7, 100)  # Bus Name
        
        # Last column (Comment) stretches to fill remaining space
        header.setStretchLastSection(True)
        
        # Create message filters initially
        self.create_message_filters()
    
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
        # Check if filters attribute exists
        if not hasattr(self, 'filters') or not self.filters:
            return
            
        header = self.table.horizontalHeader()
        if not header:
            return
            
        # Calculate positions to avoid overlap - filters start well below header text
        header_height = header.height()
        filter_top = int(header_height * 0.6)  # Position filters in the lower portion of the header
        
        for i, widget in list(self.filters.items()):
            # Skip if widget has been deleted
            if widget is None or not widget.isVisible():
                continue
                
            try:
                # Safety check to handle deleted widgets
                if not widget.parent():
                    # Widget is orphaned, remove it from filters
                    self.filters[i] = None
                    continue
                    
                left = header.sectionPosition(i) - self.table.horizontalScrollBar().value()
                width = header.sectionSize(i)
                
                # Calculate height for filter based on widget type
                height = int(min(24, header_height * 0.35))  # Limit height to avoid overflow
                
                # Position widget below the header text with proper spacing
                widget.setGeometry(left + 3, filter_top, width - 6, height)
                widget.setVisible(True)
                widget.raise_()  # Ensure filter is on top of other widgets
            except RuntimeError:
                # Widget has been deleted, remove it from filters
                self.filters[i] = None
    
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
        
        # Add nodes section if available
        if hasattr(self.db, 'nodes') and self.db.nodes:
            self.nodes_item = QTreeWidgetItem(root)
            self.nodes_item.setText(0, "Nodes")
            self.nodes_item.setExpanded(True)
            
            # Add all nodes to the tree
            for node in self.db.nodes:
                node_item = QTreeWidgetItem(self.nodes_item)
                node_item.setText(0, node.name)
                
                # Add node comment if available
                if hasattr(node, 'comment') and node.comment:
                    comment_item = QTreeWidgetItem(node_item)
                    comment_item.setText(0, f"Comment: {node.comment}")
        
        # Add messages section
        self.messages_item = QTreeWidgetItem(root)
        self.messages_item.setText(0, "Messages")
        self.messages_item.setExpanded(True)
        
        # Add all messages directly under the Messages node without grouping by sender
        for msg in self.db.messages:
            msg_item = QTreeWidgetItem(self.messages_item)
            msg_item.setText(0, f"{msg.name} (0x{msg.frame_id:X})")
            
            # Add signals group
            if msg.signals:
                signals_item = QTreeWidgetItem(msg_item)
                signals_item.setText(0, f"Signals ({len(msg.signals)})")
                
                # Add signals with details
                for signal in msg.signals:
                    signal_item = QTreeWidgetItem(signals_item)
                    signal_item.setText(0, signal.name)
                    
                    # Add signal details as children
                    bit_info = QTreeWidgetItem(signal_item)
                    bit_info.setText(0, f"Bits: {signal.start}|{signal.length}")
                    
                    byte_order = getattr(signal, 'byte_order', "Unknown")
                    order_item = QTreeWidgetItem(signal_item)
                    order_item.setText(0, f"Byte Order: {byte_order}")
                    
                    is_signed = getattr(signal, 'is_signed', False)
                    signed_item = QTreeWidgetItem(signal_item)
                    signed_item.setText(0, f"Signed: {'Yes' if is_signed else 'No'}")
                    
                    if hasattr(signal, 'comment') and signal.comment:
                        sig_comment_item = QTreeWidgetItem(signal_item)
                        sig_comment_item.setText(0, f"Comment: {signal.comment}")
        
        # Add separate signals section at root level
        self.signals_item = QTreeWidgetItem(root)
        signal_count = sum(len(msg.signals) for msg in self.db.messages)
        self.signals_item.setText(0, f"All Signals ({signal_count})")
        
        # Create alphabetically sorted list of all signals
        all_signals = []
        for msg in self.db.messages:
            for signal in msg.signals:
                all_signals.append((signal, msg))
        
        # Sort by signal name
        all_signals.sort(key=lambda x: x[0].name)
        
        # Add all signals to the signals section
        for signal, parent_msg in all_signals:
            signal_item = QTreeWidgetItem(self.signals_item)
            signal_item.setText(0, f"{signal.name} - {parent_msg.name} (0x{parent_msg.frame_id:X})")
    
    def on_tree_item_clicked(self, item, column):
        """Handle clicks on tree items to update the table view"""
        # Check if this is the Messages node
        if item == self.messages_item:
            self.populate_messages_table()
            return
            
        # Check if this is the Signals node
        if hasattr(self, 'signals_item') and item == self.signals_item:
            self.populate_signals_table()
            return
        
        # Check if this is a message node (direct child of Messages node)
        if item.parent() == self.messages_item:
            # This is a message node
            msg_text = item.text(0)
            if " (0x" in msg_text:
                msg_name = msg_text.split(" (0x")[0]  # Extract message name
                for msg in self.db.messages:
                    if msg.name == msg_name:
                        self.show_message_details(msg)
                        return
        
        # Check if this is an individual signal in the "All Signals" section
        if hasattr(self, 'signals_item') and item.parent() == self.signals_item:
            # Extract signal name and message name from the text
            signal_text = item.text(0)
            if " - " in signal_text and " (0x" in signal_text:
                signal_name = signal_text.split(" - ")[0]
                msg_name = signal_text.split(" - ")[1].split(" (0x")[0]
                
                # Find the message and signal
                for msg in self.db.messages:
                    if msg.name == msg_name:
                        for signal in msg.signals:
                            if signal.name == signal_name:
                                self.show_signal_details(signal, msg)
                                return
    
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
        
        # Update table headers if needed
        if self.table.columnCount() != len(self.column_names):
            self.table.setColumnCount(len(self.column_names))
            self.table.setHorizontalHeaderLabels(self.column_names)
            
            # Configure column resize behavior
            header = self.table.horizontalHeader()
            for i in range(len(self.column_names)):
                header.setSectionResizeMode(i, QHeaderView.Interactive)
                
            # Reset column widths
            header.resizeSection(0, 100)  # ID column
            header.resizeSection(1, 150)  # Name column
            header.resizeSection(2, 80)   # Length column
            header.resizeSection(3, 80)   # Signals column
            header.resizeSection(4, 100)  # Extended Frame
            header.resizeSection(5, 100)  # Cycle Time
            header.resizeSection(6, 120)  # Senders
            header.resizeSection(7, 100)  # Bus Name
        
        # Create message filters (will handle cleanup of existing ones)
        self.create_message_filters()
        
        # Clean up any message_filters reference
        if hasattr(self, 'message_filters'):
            delattr(self, 'message_filters')
            
        # Populate data
        self.all_messages = self.db.messages
        self.apply_filters()
        
    def create_message_filters(self):
        """Create filter widgets for message columns"""
        # Safely clean up existing filters first
        if hasattr(self, 'filters'):
            for key, widget in list(self.filters.items()):
                try:
                    if widget is not None:
                        widget.setParent(None)
                        widget.deleteLater()
                except (RuntimeError, Exception):
                    pass  # Widget already deleted
        
        # Create new filter dictionary
        self.filters = {}
        
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
            filter_widget.show()  # Ensure widget is visible
            
        # Position the filter widgets
        QTimer.singleShot(50, self.position_filter_widgets)
    
    def clear_filters(self):
        """Clear all filter inputs"""
        for filter_widget in self.filters.values():
            if isinstance(filter_widget, QLineEdit):
                filter_widget.clear()
            elif isinstance(filter_widget, QComboBox):
                filter_widget.setCurrentIndex(0)
        
        # Determine which apply method to use based on current view
        if self.table.columnCount() == len(self.column_names):
            # Messages table
            self.apply_filters()
            # Close any expanded signal rows by resetting the table
            self.populate_messages_table()
        else:
            # Signals table
            self.apply_signal_filters()
    
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
        
        # Determine if we're in messages or signals view by checking column count
        if self.table.columnCount() == len(self.column_names):
            # Messages table
            self.sort_table(self.current_sort_column, self.current_sort_order)
        else:
            # Signals table
            self.sort_signals_table(self.current_sort_column, self.current_sort_order)
        
        # Make sure our filters are visible after sortingsn
        self.position_filter_widgets()
    
    def sort_table(self, column, order):
        """Sort the table content by a specific column"""
        if not hasattr(self, 'all_messages') or not self.all_messages:
            return
            
        # Close any expanded signal rows first to avoid sorting issues
        self.collapse_all_signals()
            
        # Get current filtered messages
        if self.table.rowCount() == 0:
            return
            
        # Collect the currently visible messages
        current_messages = []
        for row in range(self.table.rowCount()):
            # Get ID from first column to find the message object
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                # Find the button in the cell widget to get the message
                for child in cell_widget.children():
                    if isinstance(child, QToolButton) and hasattr(child, 'msg'):
                        current_messages.append(child.msg)
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
    
    def collapse_all_signals(self):
        """Collapse all expanded signal rows"""
        # First check if we need to do anything
        row = 0
        while row < self.table.rowCount():
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                # Find the button in the cell widget
                for child in cell_widget.children():
                    if isinstance(child, QToolButton) and hasattr(child, 'is_expanded') and child.is_expanded:
                        # Collapse this row
                        self.toggle_signal_rows(child)
                        break
            row += 1
    
    def apply_filters(self):
        """Apply all filters to the messages table"""
        if not hasattr(self, 'all_messages') or not self.all_messages:
            return
            
        # Collapse all expanded signals first to avoid filtering issues
        self.collapse_all_signals()
            
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
        # Create expand/collapse button in first column
        expand_button = QToolButton()
        expand_button.setArrowType(Qt.RightArrow)
        expand_button.setCheckable(True)
        expand_button.setStyleSheet("QToolButton { border: none; }")
        
        # Store the message and whether row is expanded
        expand_button.msg = msg
        expand_button.is_expanded = False
        expand_button.row = row
        
        # Connect button click to expand/collapse
        expand_button.clicked.connect(lambda checked, b=expand_button: 
                                     self.toggle_signal_rows(b))
        
        # Add the expand button to a cell widget
        id_cell = QWidget()
        id_layout = QHBoxLayout(id_cell)
        id_layout.setContentsMargins(0, 0, 0, 0)
        id_layout.addWidget(expand_button)
        id_layout.addWidget(QLabel(f"0x{msg.frame_id:X}"))
        id_layout.setAlignment(Qt.AlignLeft)
        
        self.table.setCellWidget(row, 0, id_cell)
        
        # Name
        name_item = QTableWidgetItem(msg.name)
        self.table.setItem(row, 1, name_item)
        
        # Length
        length_item = QTableWidgetItem(str(msg.length))
        self.table.setItem(row, 2, length_item)
        
        # Signal count
        signal_count = len(msg.signals)
        signal_text = f"{signal_count} signal{'s' if signal_count != 1 else ''}"
        signal_count_item = QTableWidgetItem(signal_text)
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
    
    def toggle_signal_rows(self, button):
        """Expand or collapse signal rows for a message"""
        if button.is_expanded:
            # Collapse - remove signal rows
            button.setArrowType(Qt.RightArrow)
            
            # Find how many rows to remove (number of signals)
            signal_count = len(button.msg.signals)
            
            # Remove rows starting from the next row after the message
            self.table.removeRow(button.row + 1)
            # We need to adjust row numbers for all buttons below this one
            self.adjust_button_rows(button.row, -signal_count)
            
            button.is_expanded = False
        else:
            # Expand - insert signal rows
            button.setArrowType(Qt.DownArrow)
            
            # Insert a row for each signal
            for i, signal in enumerate(button.msg.signals):
                signal_row = button.row + i + 1
                self.table.insertRow(signal_row)
                
                # Create indented signal name with type indicator
                signal_cell = QWidget()
                signal_layout = QHBoxLayout(signal_cell)
                signal_layout.setContentsMargins(0, 0, 0, 0)
                signal_layout.addSpacing(30)  # Indentation
                
                # Add a different icon for signals
                icon_label = QLabel("↳")
                signal_layout.addWidget(icon_label)
                
                # Add signal name and details
                signal_name = QLabel(f"<b>{signal.name}</b>")
                signal_layout.addWidget(signal_name)
                
                # Add type info after the name
                bit_info = QLabel(f" ({signal.start}|{signal.length})")
                bit_info.setStyleSheet("color: gray;")
                signal_layout.addWidget(bit_info)
                
                signal_layout.addStretch()
                self.table.setCellWidget(signal_row, 1, signal_cell)
                
                # Add empty or N/A items for the other columns
                for col in range(2, self.table.columnCount()):
                    self.table.setItem(signal_row, col, QTableWidgetItem(""))
                
                # Set row background color to differentiate from message rows
                for col in range(self.table.columnCount()):
                    if self.table.item(signal_row, col):
                        self.table.item(signal_row, col).setBackground(QColor("#f8f8f8"))
            
            # We need to adjust row numbers for all buttons below this one
            self.adjust_button_rows(button.row, len(button.msg.signals))
            
            button.is_expanded = True
    
    def adjust_button_rows(self, changed_row, offset):
        """Adjust the row property of buttons below the changed row"""
        # Get the number of rows in the table
        row_count = self.table.rowCount()
        
        # Update row numbers for buttons below the changed row
        for row in range(changed_row + 1 + max(offset, 0), row_count):
            cell_widget = self.table.cellWidget(row, 0)
            if cell_widget:
                # Find the button in the cell widget
                button = None
                for child in cell_widget.children():
                    if isinstance(child, QToolButton):
                        button = child
                        break
                
                if button and hasattr(button, 'row'):
                    button.row = row  # Update the row number
    
    def show_signal_details(self, signal, parent_msg):
        """Show detailed information about a signal"""
        # Create a non-modal dialog with signal and DBC file information
        detail_view = MessageDetailView(self, parent_msg, self.dbc_file_path, selected_signal=signal)
        
        # Keep a reference to prevent garbage collection
        self.open_detail_views.append(detail_view)
        
        # Connect the dialog's finished signal to remove it from our list
        detail_view.finished.connect(lambda: self.remove_detail_view(detail_view))
        
        # Show the dialog as non-modal
        detail_view.show()
        
    def populate_signals_table(self):
        """Populate the table with all signals when the Signals node is clicked"""
        if not hasattr(self, 'db') or not self.db.messages:
            return
            
        # Clear the table
        self.table.clearContents()
        self.table.setRowCount(0)
        
        # Collect all signals from all messages
        all_signals = []
        for msg in self.db.messages:
            for signal in msg.signals:
                all_signals.append((signal, msg))
        
        # Sort by signal name
        all_signals.sort(key=lambda x: x[0].name)
        
        # Set up column names for signals view - include all available signal attributes
        signal_columns = [
            "Signal Name", "Message", "Start Bit", "Length", 
            "Byte Order", "Signed", "Initial", "Scale", "Offset", 
            "Min Value", "Max Value", "Unit", "Multiplexer",
            "Choices", "Comment", "Receivers"
        ]
        
        # Update table headers
        if self.table.columnCount() != len(signal_columns):
            self.table.setColumnCount(len(signal_columns))
            self.table.setHorizontalHeaderLabels(signal_columns)
            
            # Configure column resize behavior
            header = self.table.horizontalHeader()
            for i in range(len(signal_columns)):
                header.setSectionResizeMode(i, QHeaderView.Interactive)
                
            # Set default widths for signal table columns
            header.resizeSection(0, 150)  # Signal Name
            header.resizeSection(1, 200)  # Message
            header.resizeSection(2, 70)   # Start Bit
            header.resizeSection(3, 70)   # Length
            header.resizeSection(4, 100)  # Byte Order
            header.resizeSection(5, 70)   # Signed
            header.resizeSection(6, 70)   # Initial
            header.resizeSection(7, 70)   # Scale
            header.resizeSection(8, 70)   # Offset
            header.resizeSection(9, 80)   # Min Value
            header.resizeSection(10, 80)  # Max Value
            header.resizeSection(11, 70)  # Unit
            header.resizeSection(12, 120) # Multiplexer
            header.resizeSection(13, 150) # Choices
            
            # Comment and Receivers columns can stretch
            header.setStretchLastSection(True)
            
        # Create signal filters (will handle cleanup of existing ones)
        self.setup_signal_filters(signal_columns)
        
        # Populate the table
        self.table.setRowCount(len(all_signals))
        for row, (signal, msg) in enumerate(all_signals):
            # Signal Name
            self.table.setItem(row, 0, QTableWidgetItem(signal.name))
            
            # Message
            self.table.setItem(row, 1, QTableWidgetItem(f"{msg.name} (0x{msg.frame_id:X})"))
            
            # Start Bit
            self.table.setItem(row, 2, QTableWidgetItem(str(signal.start)))
            
            # Length
            self.table.setItem(row, 3, QTableWidgetItem(str(signal.length)))
            
            # Byte Order
            byte_order = getattr(signal, 'byte_order', "Unknown")
            self.table.setItem(row, 4, QTableWidgetItem(byte_order))
            
            # Signed
            is_signed = getattr(signal, 'is_signed', False)
            self.table.setItem(row, 5, QTableWidgetItem("Yes" if is_signed else "No"))
            
            # Initial Value
            initial = getattr(signal, 'initial', None)
            self.table.setItem(row, 6, QTableWidgetItem(str(initial) if initial is not None else ""))
            
            # Scale
            scale = getattr(signal, 'scale', 1.0)
            self.table.setItem(row, 7, QTableWidgetItem(str(scale)))
            
            # Offset
            offset = getattr(signal, 'offset', 0.0)
            self.table.setItem(row, 8, QTableWidgetItem(str(offset)))
            
            # Min Value
            minimum = getattr(signal, 'minimum', None)
            self.table.setItem(row, 9, QTableWidgetItem(str(minimum) if minimum is not None else ""))
            
            # Max Value
            maximum = getattr(signal, 'maximum', None)
            self.table.setItem(row, 10, QTableWidgetItem(str(maximum) if maximum is not None else ""))
            
            # Unit
            unit = getattr(signal, 'unit', "")
            self.table.setItem(row, 11, QTableWidgetItem(unit if unit else ""))
            
            # Multiplexer
            multiplexer_signal = getattr(signal, 'multiplexer_signal', None)
            multiplexer_ids = getattr(signal, 'multiplexer_ids', [])
            multiplexer_info = ""
            
            if multiplexer_signal:
                multiplexer_info = f"Dependent on: {multiplexer_signal}"
            elif multiplexer_ids:
                multiplexer_info = f"Is multiplexer, IDs: {multiplexer_ids}"
                
            self.table.setItem(row, 12, QTableWidgetItem(multiplexer_info))
            
            # Choices (enum values)
            choices = getattr(signal, 'choices', None)
            choices_text = ""
            if choices:
                choices_items = []
                for value, name in choices.items():
                    choices_items.append(f"{value}={name}")
                choices_text = ", ".join(choices_items)
            self.table.setItem(row, 13, QTableWidgetItem(choices_text))
            
            # Comment
            comment = getattr(signal, 'comment', "")
            self.table.setItem(row, 14, QTableWidgetItem(comment if comment else ""))
            
            # Receivers
            receivers = getattr(signal, 'receivers', [])
            receivers_text = ", ".join(receivers) if receivers else ""
            self.table.setItem(row, 15, QTableWidgetItem(receivers_text))
        
        # Position filter widgets
        self.position_filter_widgets()
        
    def setup_signal_filters(self, signal_columns):
        """Set up filter widgets for signal columns"""
        # Safely clean up existing filters
        if hasattr(self, 'filters'):
            for key, widget in list(self.filters.items()):
                try:
                    if widget is not None:
                        widget.setParent(None)
                        widget.deleteLater()
                except (RuntimeError, Exception):
                    pass  # Widget already deleted
        
        # Create new filter dictionary
        self.filters = {}
        
        # Create filter widgets for each signal column
        for i, col_name in enumerate(signal_columns):
            # Choose filter type based on column
            if col_name == "Byte Order":
                filter_widget = QComboBox(self.table)
                filter_widget.addItems(["All", "little_endian", "big_endian"])
                filter_widget.setStyleSheet("""
                    QComboBox { 
                        border: 1px solid #ccc; 
                        border-radius: 3px; 
                        background-color: white;
                        padding: 1px 3px;
                    }
                """)
                filter_widget.currentTextChanged.connect(self.apply_signal_filters)
            elif col_name == "Signed":
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
                filter_widget.currentTextChanged.connect(self.apply_signal_filters)
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
                filter_widget.textChanged.connect(self.apply_signal_filters)
            
            # Set filter widget and add to collection
            filter_widget.setParent(self.table)
            self.filters[i] = filter_widget
            filter_widget.show()  # Ensure widget is visible
            
        # Position the filter widgets now
        self.position_filter_widgets()
        
    def apply_signal_filters(self):
        """Apply all filters to the signals table"""
        if self.table.rowCount() == 0:
            return
            
        # Store all rows data for filtering
        all_rows = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                row_data.append(item.text() if item else "")
            all_rows.append(row_data)
            
        # Apply filters
        filtered_rows = []
        for row_data in all_rows:
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
                    
                # Get cell value
                value = row_data[col].lower()
                
                # Apply filter (case insensitive)
                if filter_text and value.find(filter_text) == -1:
                    match = False
                    break
            
            if match:
                filtered_rows.append(row_data)
                
        # Update the table with filtered rows
        self.table.clearContents()
        self.table.setRowCount(len(filtered_rows))
        
        for row, row_data in enumerate(filtered_rows):
            for col, cell_data in enumerate(row_data):
                self.table.setItem(row, col, QTableWidgetItem(cell_data))
                
        # Apply current sort if any
        if self.current_sort_column >= 0:
            self.sort_signals_table(self.current_sort_column, self.current_sort_order)
            
    def on_table_cell_double_clicked(self, row, column):
        """Handle double clicks on table cells to show message details"""
        # Get the message object from the row
        cell_widget = self.table.cellWidget(row, 0)
        if cell_widget:
            # Find the button in the cell widget to get the message
            for child in cell_widget.children():
                if isinstance(child, QToolButton) and hasattr(child, 'msg'):
                    self.show_message_details(child.msg)
                    return
                    
        # For signal rows, find the parent message
        # This works because signal rows don't have a cell widget in column 0
        parent_row = row
        while parent_row >= 0:
            parent_cell = self.table.cellWidget(parent_row, 0)
            if parent_cell:
                # Find the button in the cell widget
                for child in parent_cell.children():
                    if isinstance(child, QToolButton) and hasattr(child, 'msg'):
                        self.show_message_details(child.msg)
                        return
            parent_row -= 1
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Close all open detail views
        for view in self.open_detail_views[:]:
            view.close()
            
        # Emit signal that this window is closing
        if self.dbc_file_path:
            self.window_closed.emit(self.dbc_file_path)
        super().closeEvent(event) 

    def sort_signals_table(self, column, order):
        """Sort the signals table by a specific column"""
        if self.table.rowCount() == 0:
            return
            
        # Store current table data
        rows_data = []
        for row in range(self.table.rowCount()):
            row_data = []
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            rows_data.append(row_data)
        
        # Sort the data
        def get_sort_key(row_data):
            value = row_data[column]
            # Special handling for numeric columns
            if column in [2, 3, 7, 8, 9, 10]:  # Start bit, length, scale, offset, min, max
                try:
                    return float(value) if value else 0
                except ValueError:
                    return 0
            # For other columns, use string comparison
            return str(value).lower()
        
        rows_data.sort(key=get_sort_key, reverse=(order == Qt.DescendingOrder))
        
        # Update the table
        self.table.clearContents()
        for row, row_data in enumerate(rows_data):
            for col, cell_data in enumerate(row_data):
                item = QTableWidgetItem(cell_data)
                self.table.setItem(row, col, item) 