from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTreeWidget, QTreeWidgetItem,
                            QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter, QStackedWidget, QPushButton,
                            QMenu, QAction, QDialog, QCheckBox, QScrollArea, QDialogButtonBox,
                            QAbstractItemView)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from controller.dbc_io_handler import DBC_IO_Handler
from view.signal_detail_view import SignalDetailView
from view.message_detail_view import MessageDetailView
from view.node_detail_view import NodeDetailView
from view.bus_load_dialog import BusLoadDialog

class NumericTableWidgetItem(QTableWidgetItem):
    """Custom QTableWidgetItem subclass that sorts numerically"""
    def __init__(self, value=None, display_text=None):
        """Initialize with numeric value for sorting and optional display text"""
        super().__init__()
        if display_text is not None:
            self.setData(Qt.DisplayRole, display_text)
        if value is not None:
            self.setData(Qt.UserRole, value)
            
    def __lt__(self, other):
        """Override less than operator to use UserRole for sorting"""
        if self.data(Qt.UserRole) is None:
            return True  # None values sort first
        if other.data(Qt.UserRole) is None:
            return False
            
        # Use the UserRole data for sorting
        return self.data(Qt.UserRole) < other.data(Qt.UserRole)

class ColumnSelectorDialog(QDialog):
    """Dialog that allows selection of multiple columns to show/hide"""
    def __init__(self, parent, table):
        super().__init__(parent)
        self.table = table
        self.selected_columns = []
        self.checkboxes = []
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Column Visibility")
        self.setMinimumWidth(300)
        
        main_layout = QVBoxLayout(self)
        
        # Add a label with instructions
        label = QLabel("Select columns to display:")
        main_layout.addWidget(label)
        
        # Create scroll area for checkboxes
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)
        
        # Add select all / deselect all buttons
        select_buttons_layout = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self.select_all)
        deselect_all_btn = QPushButton("Deselect All")
        deselect_all_btn.clicked.connect(self.deselect_all)
        select_buttons_layout.addWidget(select_all_btn)
        select_buttons_layout.addWidget(deselect_all_btn)
        main_layout.addLayout(select_buttons_layout)
        
        # Add checkbox for each column
        header = self.table.horizontalHeader()
        for i in range(self.table.columnCount()):
            column_name = self.table.horizontalHeaderItem(i).text()
            checkbox = QCheckBox(column_name)
            checkbox.setChecked(not header.isSectionHidden(i))
            checkbox.setProperty("column_index", i)
            self.checkboxes.append(checkbox)
            scroll_layout.addWidget(checkbox)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def select_all(self):
        """Select all checkboxes"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(True)
    
    def deselect_all(self):
        """Deselect all checkboxes"""
        for checkbox in self.checkboxes:
            checkbox.setChecked(False)
    
    def get_selected_columns(self):
        """Get a dictionary of column indices and their visibility state"""
        visibility = {}
        for checkbox in self.checkboxes:
            col_index = checkbox.property("column_index")
            visibility[col_index] = checkbox.isChecked()
        return visibility

class DBCDisplayView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_handler = None
        self.bus_load_button = None  # Initialize as None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.setSpacing(5)
        
        # File info section
        self.file_name_label = QLabel()
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
        self.file_name_label.hide()  # Hide label initially
        
        # Add buttons row
        self.buttons_layout = QHBoxLayout()  # Make it instance variable
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.buttons_layout.addStretch()
        
        # Add file name label and buttons to layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.file_name_label)
        top_layout.addLayout(self.buttons_layout)
        layout.addLayout(top_layout)
        
        # Create splitter for main content
        self.main_splitter = QSplitter(Qt.Horizontal)
        self.main_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #d0d0d0;
                width: 2px;
            }
            QSplitter::handle:hover {
                background-color: #a0a0a0;
            }
        """)
        
        # Tree view
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setMinimumWidth(200)  # Set minimum width for tree
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
        self.tree_widget.itemClicked.connect(self.on_tree_item_clicked)
        self.main_splitter.addWidget(self.tree_widget)
        
        # Create stacked widget for tables
        self.tables_stack = QStackedWidget()
        
        # Signals table
        self.signals_table = QTableWidget()
        self.signals_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 4px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        self.setup_signals_table()
        self.tables_stack.addWidget(self.signals_table)
        
        # Messages table
        self.messages_table = QTableWidget()
        self.messages_table.setStyleSheet(self.signals_table.styleSheet())
        self.setup_messages_table()
        self.tables_stack.addWidget(self.messages_table)
        
        # Nodes table
        self.nodes_table = QTableWidget()
        self.nodes_table.setStyleSheet(self.signals_table.styleSheet())
        self.setup_nodes_table()
        self.tables_stack.addWidget(self.nodes_table)
        
        # Add tables stack to splitter
        self.main_splitter.addWidget(self.tables_stack)
        
        # Set initial sizes (30:70 ratio)
        self.main_splitter.setSizes([300, 700])
        
        layout.addWidget(self.main_splitter)
        
        # Initially hide both tree and tables
        self.main_splitter.hide()

    def setup_table_header_context_menu(self, table):
        """Setup a context menu for the table header to allow showing/hiding columns"""
        header = table.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(lambda pos, t=table: self.show_header_context_menu(pos, t))
        
    def show_header_context_menu(self, pos, table):
        """Show the context menu for the table header"""
        menu = QMenu(self)
        
        # Add an option to use the multi-column selector
        select_columns_action = QAction("Select Columns...", self)
        select_columns_action.triggered.connect(lambda: self.show_column_selector_dialog(table))
        menu.addAction(select_columns_action)
        
        menu.addSeparator()
        
        # Add an option to show all columns
        show_all_action = QAction("Show All Columns", self)
        show_all_action.triggered.connect(lambda: self.show_all_columns(table))
        menu.addAction(show_all_action)
        
        # Show the menu at the correct position
        header = table.horizontalHeader()
        menu.exec_(header.mapToGlobal(pos))

    def show_column_selector_dialog(self, table):
        """Show dialog for selecting multiple columns"""
        dialog = ColumnSelectorDialog(self, table)
        if dialog.exec_() == QDialog.Accepted:
            # Apply the visibility settings
            visibility = dialog.get_selected_columns()
            for col_index, is_visible in visibility.items():
                table.setColumnHidden(col_index, not is_visible)

    def show_all_columns(self, table):
        """Show all columns in the table"""
        for i in range(table.columnCount()):
            table.setColumnHidden(i, False)

    def setup_signals_table(self):
        """Setup the signals table structure"""
        columns = [
            "Name", "Message", "Message ID", "Start Bit", "Length", "Byte Order",
            "Signed", "Scale", "Offset", "Minimum", "Maximum", "Unit", "Comment", "Receivers",
            "Is Multiplexer", "Multiplexer ID", "Is Float", "Decimal Places", "Choices Count",
            "SPN", "PGN", "SA", "DA", "Priority", "Address", "Is J1939"
        ]
        self.signals_table.setColumnCount(len(columns))
        self.signals_table.setHorizontalHeaderLabels(columns)
        header = self.signals_table.horizontalHeader()
        
        # Make table read-only
        self.signals_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Enable manual column resizing
        self.signals_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Set stretch for the last column to use remaining space
        header.setStretchLastSection(True)
        
        # Set column widths
        column_widths = {
            "Name": 150,
            "Message": 150,
            "Message ID": 100,
            "Start Bit": 80,
            "Length": 80,
            "Byte Order": 100,
            "Signed": 80,
            "Scale": 80,
            "Offset": 80,
            "Minimum": 80,
            "Maximum": 80,
            "Unit": 80,
            "Comment": 200,
            "Receivers": 150,
            "Is Multiplexer": 100,
            "Multiplexer ID": 100,
            "Is Float": 80,
            "Decimal Places": 120,
            "Choices Count": 100,
            "SPN": 80,
            "PGN": 80,
            "SA": 60,
            "DA": 60,
            "Priority": 80,
            "Address": 80,
            "Is J1939": 80
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            self.signals_table.setColumnWidth(i, column_widths.get(col, 100))
        
        # Connect double-click signal to show signal details
        self.signals_table.itemDoubleClicked.connect(self.on_signal_double_clicked)
        
        # Setup header context menu for column visibility
        self.setup_table_header_context_menu(self.signals_table)
        
        self.signals_table.setVisible(False)  # Hide table initially

    def setup_messages_table(self):
        """Setup the messages table structure"""
        columns = [
            "Name", "ID", "Length", "Signals Count", "Senders", "Extended", "CAN FD", 
            "Bus", "Cycle Time", "Send Type", "Comment", "Header ID", "Header Byte Order",
            "Unused Bit Pattern", "Is Multiplexed", "Contained Messages Count",
            "PGN", "Priority", "Source Address", "Destination Address", "Protocol"
        ]
        self.messages_table.setColumnCount(len(columns))
        self.messages_table.setHorizontalHeaderLabels(columns)
        header = self.messages_table.horizontalHeader()
        
        # Make table read-only
        self.messages_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Enable manual column resizing for all columns
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column to use remaining space
        header.setStretchLastSection(True)
        
        # Set initial widths for columns
        column_widths = {
            "Name": 150,     # Wider for message names
            "ID": 100,      # Wider to fit hex values
            "Length": 80,    # Fixed size for byte length
            "Signals Count": 100,  # Increased to fit content
            "Senders": 150,  # Wider for multiple sender names
            "Extended": 80,  # Yes/No field
            "CAN FD": 80,   # Yes/No field
            "Bus": 100,     # Bus name
            "Cycle Time": 100,  # Cycle time in ms
            "Send Type": 100,  # Send type
            "Comment": 200,   # For comments
            "Header ID": 100,  # Header ID
            "Header Byte Order": 120,  # Byte order for the header
            "Unused Bit Pattern": 140,  # Pattern for unused bits
            "Is Multiplexed": 100,  # Whether message is multiplexed
            "Contained Messages Count": 180,  # Count of contained messages
            "PGN": 80,  # Parameter Group Number (J1939)
            "Priority": 80,  # Priority (J1939)
            "Source Address": 120,  # Source Address (J1939)
            "Destination Address": 140,  # Destination Address (J1939)
            "Protocol": 100  # Protocol type
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            self.messages_table.setColumnWidth(i, column_widths.get(col, 150))
        
        # Connect double-click signal to show message details
        self.messages_table.itemDoubleClicked.connect(self.on_message_double_clicked)
        
        # Setup header context menu for column visibility
        self.setup_table_header_context_menu(self.messages_table)
        
        self.messages_table.setVisible(False)  # Hide table initially

    def setup_nodes_table(self):
        """Setup the nodes table structure"""
        columns = [
            "Name", "Tx Messages Count", "Rx Messages Count", "Tx Signals Count", "Rx Signals Count", 
            "Comment", "Address", "Function Name", "Manufacturer Code", "Identity Number",
            "Industry Group", "Vehicle System", "Vehicle System Instance", 
            "Function", "Function Instance", "ECU Instance", "Manufacturer Ext",
            "ECU Ext Reference", "Is J1939"
        ]
        self.nodes_table.setColumnCount(len(columns))
        self.nodes_table.setHorizontalHeaderLabels(columns)
        header = self.nodes_table.horizontalHeader()
        
        # Make table read-only
        self.nodes_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Enable manual column resizing for all columns
        for i in range(len(columns)):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column to use remaining space
        header.setStretchLastSection(True)
        
        # Set initial widths for columns
        column_widths = {
            "Name": 150,
            "Tx Messages Count": 120,
            "Rx Messages Count": 120,
            "Tx Signals Count": 120,
            "Rx Signals Count": 120,
            "Comment": 200,
            "Address": 100,
            "Function Name": 150,
            "Manufacturer Code": 120,
            "Identity Number": 120,
            "Industry Group": 120,
            "Vehicle System": 120,
            "Vehicle System Instance": 150,
            "Function": 100,
            "Function Instance": 120,
            "ECU Instance": 120,
            "Manufacturer Ext": 120,
            "ECU Ext Reference": 150,
            "Is J1939": 80
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            self.nodes_table.setColumnWidth(i, column_widths.get(col, 150))
        
        # Connect double-click signal to show node details
        self.nodes_table.itemDoubleClicked.connect(self.on_node_double_clicked)
        
        # Setup header context menu for column visibility
        self.setup_table_header_context_menu(self.nodes_table)
        
        self.nodes_table.setVisible(False)  # Hide table initially

    def update_signals_table(self, signals):
        """Update the signals table with data"""
        # Temporarily disable sorting while updating
        self.signals_table.setSortingEnabled(False)
        
        # Clear existing items
        self.signals_table.setRowCount(0)
        self.signals_table.setRowCount(len(signals))
        
        # Store signals data for later use
        self.signals_data = signals
        
        # Helper function to create numeric items
        def create_numeric_item(value, display_text=None):
            if value is None:
                return QTableWidgetItem("")
            if display_text is None:
                display_text = str(value)
            item = NumericTableWidgetItem(value)
            item.setData(Qt.DisplayRole, display_text)
            return item
        
        # Helper function to create text items
        def create_text_item(text):
            if text is None:
                return QTableWidgetItem("")
            item = QTableWidgetItem(str(text))
            item.setData(Qt.UserRole, str(text))
            return item
        
        # Helper function for boolean items
        def create_bool_item(value):
            text = 'Yes' if value else 'No'
            item = QTableWidgetItem(text)
            item.setData(Qt.UserRole, 1 if value else 0)
            return item
        
        # Prepare all items first
        table_items = []
        for signal in signals:
            # Create basic text items
            name_item = create_text_item(signal['name'])
            message_name_item = create_text_item(signal['message_name'])
            
            # Create message ID item - hex display with numeric sorting
            message_id_item = create_numeric_item(int(signal['message_id']), f"0x{signal['message_id']:X}")
            
            # Create numeric items with proper sorting
            start_bit_item = create_numeric_item(int(signal['start']))
            length_item = create_numeric_item(int(signal['length']))
            byte_order_item = create_text_item(signal['byte_order'])
            signed_item = create_bool_item(signal['is_signed'])
            scale_item = create_numeric_item(float(signal['scale']))
            offset_item = create_numeric_item(float(signal['offset']))
            
            # Minimum value (may be null)
            min_item = create_numeric_item(signal['minimum'])
            
            # Maximum value (may be null)
            max_item = create_numeric_item(signal['maximum'])
            
            unit_item = create_text_item(signal.get('unit', ''))
            comment_item = create_text_item(signal.get('comment', ''))
            receivers_item = create_text_item(', '.join(signal['receivers']) if signal['receivers'] else '')
            
            # Additional signal properties
            is_multiplexer_item = create_bool_item(signal.get('is_multiplexer', False))
            multiplexer_id_item = create_numeric_item(signal.get('multiplexer_id'))
            is_float_item = create_bool_item(signal.get('is_float', False))
            decimal_item = create_numeric_item(signal.get('decimal'))
            
            # Count choices if available
            choices_count = 0
            if signal.get('choices') and isinstance(signal.get('choices'), dict):
                choices_count = len(signal.get('choices'))
            choices_count_item = create_numeric_item(choices_count)
            
            # J1939 specific fields
            spn_item = create_numeric_item(signal.get('spn'))
            pgn_item = create_numeric_item(signal.get('pgn'))
            sa_item = create_numeric_item(signal.get('sa'))
            da_item = create_numeric_item(signal.get('da'))
            priority_item = create_numeric_item(signal.get('priority'))
            address_item = create_numeric_item(signal.get('address'))
            is_j1939_item = create_bool_item(signal.get('is_j1939', False))
            
            row_items = [
                name_item,
                message_name_item,
                message_id_item,
                start_bit_item,
                length_item,
                byte_order_item,
                signed_item,
                scale_item,
                offset_item,
                min_item,
                max_item,
                unit_item,
                comment_item,
                receivers_item,
                is_multiplexer_item,
                multiplexer_id_item,
                is_float_item,
                decimal_item,
                choices_count_item,
                spn_item,
                pgn_item,
                sa_item,
                da_item,
                priority_item,
                address_item,
                is_j1939_item
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.signals_table.setItem(row, col, item)
        
        # Re-enable sorting
        self.signals_table.setSortingEnabled(True)
        self.signals_table.setVisible(True)
        self.tables_stack.setCurrentWidget(self.signals_table)

    def update_messages_table(self, messages):
        """Update the messages table with data"""
        # Temporarily disable sorting while updating
        self.messages_table.setSortingEnabled(False)
        
        # Clear existing items
        self.messages_table.setRowCount(0)
        self.messages_table.setRowCount(len(messages))
        
        # Store messages data for later use
        self.messages_data = messages
        
        # Helper function to create numeric items
        def create_numeric_item(value, display_text=None):
            if value is None:
                return QTableWidgetItem("")
            if display_text is None:
                display_text = str(value)
            item = NumericTableWidgetItem(value)
            item.setData(Qt.DisplayRole, display_text)
            return item
        
        # Helper function to create text items
        def create_text_item(text):
            if text is None:
                return QTableWidgetItem("")
            item = QTableWidgetItem(str(text))
            item.setData(Qt.UserRole, str(text))
            return item
        
        # Helper function for boolean items
        def create_bool_item(value):
            text = 'Yes' if value else 'No'
            item = QTableWidgetItem(text)
            item.setData(Qt.UserRole, 1 if value else 0)
            return item
        
        # Prepare all items first
        table_items = []
        for msg in messages:
            # Extract J1939 specifics if available
            j1939_specifics = msg.get('j1939_specifics', {}) or {}
            if not isinstance(j1939_specifics, dict):
                j1939_specifics = {}
            
            # Create name item
            name_item = create_text_item(msg['name'])
            
            # Create frame ID item - hex value but store numeric value for sorting
            frame_id_item = create_numeric_item(int(msg['frame_id']), f"0x{msg['frame_id']:X}")
            
            # Numeric items with proper sorting
            length_item = create_numeric_item(int(msg['length']))
            signals_count_item = create_numeric_item(len(msg['signals']))
            
            # Create other items
            senders_item = create_text_item(', '.join(msg['senders']) if msg['senders'] else '')
            
            # Boolean items
            extended_item = create_bool_item(msg.get('is_extended_frame', False))
            fd_item = create_bool_item(msg.get('is_fd', False))
            
            # Text and numeric items
            bus_item = create_text_item(msg.get('bus_name', ''))
            cycle_time = msg.get('cycle_time')
            cycle_time_item = create_numeric_item(int(cycle_time) if cycle_time is not None else None, 
                                                  f"{cycle_time} ms" if cycle_time is not None else "")
            send_type_item = create_text_item(msg.get('send_type', ''))
            comment_item = create_text_item(msg.get('comment', ''))
            
            # Additional message properties
            header_id = msg.get('header_id')
            header_id_item = create_numeric_item(header_id, f"0x{header_id:X}" if header_id is not None else "")
            header_byte_order_item = create_text_item(msg.get('header_byte_order', ''))
            unused_bit_pattern_item = create_numeric_item(msg.get('unused_bit_pattern', 0))
            
            # Determine if message is multiplexed
            is_multiplexed = False
            for signal in msg['signals']:
                if signal.get('is_multiplexer', False):
                    is_multiplexed = True
                    break
            is_multiplexed_item = create_bool_item(is_multiplexed)
            
            # Count contained messages
            contained_count = len(msg.get('contained_messages', []))
            contained_count_item = create_numeric_item(contained_count)
            
            # J1939 specific fields
            pgn_item = create_numeric_item(j1939_specifics.get('pgn'))
            priority_item = create_numeric_item(j1939_specifics.get('priority'))
            source_address_item = create_numeric_item(j1939_specifics.get('source_address'))
            destination_address_item = create_numeric_item(j1939_specifics.get('destination_address'))
            
            # Determine protocol type
            protocol = "Standard CAN"
            if msg.get('is_fd', False):
                protocol = "CAN FD"
            elif j1939_specifics:
                protocol = "J1939"
            protocol_item = create_text_item(protocol)
            
            row_items = [
                name_item,
                frame_id_item,
                length_item,
                signals_count_item,
                senders_item,
                extended_item,
                fd_item,
                bus_item,
                cycle_time_item,
                send_type_item,
                comment_item,
                header_id_item,
                header_byte_order_item,
                unused_bit_pattern_item,
                is_multiplexed_item,
                contained_count_item,
                pgn_item,
                priority_item,
                source_address_item,
                destination_address_item,
                protocol_item
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.messages_table.setItem(row, col, item)
        
        # Re-enable sorting
        self.messages_table.setSortingEnabled(True)
        self.messages_table.setVisible(True)
        self.tables_stack.setCurrentWidget(self.messages_table)

    def update_nodes_table(self, nodes):
        """Update the nodes table with data"""
        # Temporarily disable sorting while updating
        self.nodes_table.setSortingEnabled(False)
        
        # Clear existing items
        self.nodes_table.setRowCount(0)
        self.nodes_table.setRowCount(len(nodes))
        
        # Prepare all items first
        table_items = []
        for node in nodes:
            # Get node messages and signals
            node_messages = self.current_handler.get_node_messages(node['name'])
            node_signals = self.current_handler.get_node_signals(node['name'])
            
            # Count values
            tx_messages_count = len(node_messages['tx_messages'])
            rx_messages_count = len(node_messages['rx_messages'])
            tx_signals_count = len(node_signals['tx_signals'])
            rx_signals_count = len(node_signals['rx_signals'])
            
            # Helper function to create numeric items
            def create_numeric_item(value, display_text=None):
                if value is None:
                    return QTableWidgetItem("")
                if display_text is None:
                    display_text = str(value)
                item = NumericTableWidgetItem(value)
                item.setData(Qt.DisplayRole, display_text)
                return item
            
            # Helper function to create text items
            def create_text_item(text):
                if text is None:
                    return QTableWidgetItem("")
                item = QTableWidgetItem(str(text))
                item.setData(Qt.UserRole, str(text))
                return item
            
            # Helper function for boolean items
            def create_bool_item(value):
                text = 'Yes' if value else 'No'
                item = QTableWidgetItem(text)
                item.setData(Qt.UserRole, 1 if value else 0)
                return item
            
            # Create items
            name_item = QTableWidgetItem(node['name'])
            name_item.setData(Qt.UserRole, node['name'])
            
            # Create numeric items for counts
            tx_messages_item = create_numeric_item(tx_messages_count)
            rx_messages_item = create_numeric_item(rx_messages_count)
            tx_signals_item = create_numeric_item(tx_signals_count)
            rx_signals_item = create_numeric_item(rx_signals_count)
            
            # Get comment
            comment_item = create_text_item(node.get('comment', ''))
            
            # Get additional node properties
            address_item = create_numeric_item(node.get('address', None))
            function_name_item = create_text_item(node.get('function_name', ''))
            manufacturer_code_item = create_numeric_item(node.get('manufacturer_code', None))
            identity_number_item = create_numeric_item(node.get('identity_number', None))
            industry_group_item = create_numeric_item(node.get('industry_group', None))
            vehicle_system_item = create_numeric_item(node.get('vehicle_system', None))
            vehicle_system_instance_item = create_numeric_item(node.get('vehicle_system_instance', None))
            function_item = create_numeric_item(node.get('function', None))
            function_instance_item = create_numeric_item(node.get('function_instance', None))
            ecu_instance_item = create_numeric_item(node.get('ecu_instance', None))
            manufacturer_ext_item = create_numeric_item(node.get('manufacturer_ext', None))
            ecu_ext_ref_item = create_text_item(node.get('ecu_ext_ref', ''))
            is_j1939_item = create_bool_item(node.get('is_j1939', False))
            
            row_items = [
                name_item,
                tx_messages_item,
                rx_messages_item,
                tx_signals_item,
                rx_signals_item,
                comment_item,
                address_item,
                function_name_item,
                manufacturer_code_item,
                identity_number_item,
                industry_group_item,
                vehicle_system_item,
                vehicle_system_instance_item,
                function_item,
                function_instance_item,
                ecu_instance_item,
                manufacturer_ext_item,
                ecu_ext_ref_item,
                is_j1939_item
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.nodes_table.setItem(row, col, item)
        
        # Re-enable sorting
        self.nodes_table.setSortingEnabled(True)
        self.nodes_table.setVisible(True)
        self.tables_stack.setCurrentWidget(self.nodes_table)

    def on_tree_item_clicked(self, item):
        """Handle tree item clicks"""
        if not self.current_handler:
            return
            
        # Check if the clicked item is the Signals, Messages, or Network Nodes root
        if item.text(0) == "Signals":
            signals = self.current_handler.get_signals()
            self.update_signals_table(signals)
        elif item.text(0) == "Messages":
            messages = self.current_handler.get_messages()
            self.update_messages_table(messages)
        elif item.text(0) == "Network Nodes":
            nodes = self.current_handler.get_nodes()
            self.update_nodes_table(nodes)
        # Check if the clicked item is "Tx Messages" or "Rx Messages" under a node
        elif item.text(0) in ["Tx Messages", "Rx Messages"]:
            parent_node = item.parent()
            if parent_node and parent_node.parent() and parent_node.parent().text(0) == "Network Nodes":
                node_name = parent_node.text(0)
                node_messages = self.current_handler.get_node_messages(node_name)
                
                # Display only Tx or Rx messages based on selection
                if item.text(0) == "Tx Messages":
                    self.update_messages_table(node_messages['tx_messages'])
                else:  # Rx Messages
                    self.update_messages_table(node_messages['rx_messages'])
        else:
            # Check if this is a node item directly under Network Nodes
            parent = item.parent()
            if parent and parent.text(0) == "Network Nodes":
                node_name = item.text(0)
                self.show_node_details(node_name)
            # Check if this is a signal item by looking at its parent
            elif parent and parent.text(0) in ["Signals", "Tx Signals", "Rx Signals"]:
                # Find the signal data
                signal_name = item.text(0)
                signal_data = None
                
                # If it's under a node's Tx/Rx signals
                if parent.text(0) in ["Tx Signals", "Rx Signals"]:
                    node_item = parent.parent()
                    if node_item:
                        node_name = node_item.text(0)
                        node_signals = self.current_handler.get_node_signals(node_name)
                        # Search in tx_signals or rx_signals based on parent text
                        signals_list = node_signals['tx_signals'] if parent.text(0) == "Tx Signals" else node_signals['rx_signals']
                        for signal in signals_list:
                            if signal['name'] == signal_name:
                                signal_data = signal
                                break
                # If it's under the main Signals root
                elif parent.text(0) == "Signals":
                    # Extract signal name from the text (format: "name (message_name - ID: 0xXX)")
                    signal_name = signal_name.split(" (")[0]
                    signals = self.current_handler.get_signals()
                    for signal in signals:
                        if signal['name'] == signal_name:
                            signal_data = signal
                            break
                # If it's under a message's signals
                elif parent.text(0) == "Signals" and parent.parent():
                    message_item = parent.parent()
                    message_name = message_item.text(0).split(" (ID:")[0]
                    messages = self.current_handler.get_messages()
                    for msg in messages:
                        if msg['name'] == message_name:
                            for signal in msg['signals']:
                                if signal['name'] == signal_name:
                                    # Add message info to signal data
                                    signal_data = signal.copy()
                                    signal_data['message_name'] = msg['name']
                                    signal_data['message_id'] = msg['frame_id']
                                    break
                            break
                
                # Show signal detail view if signal data was found
                if signal_data:
                    signal_detail = SignalDetailView(signal_data, self)
                    signal_detail.show()
            
            # Check if this is a message item
            elif self.is_message_item(item):
                message_data = self.get_message_data_from_item(item)
                if message_data:
                    message_detail = MessageDetailView(message_data, self)
                    message_detail.show()
            else:
                self.signals_table.setVisible(False)
                self.messages_table.setVisible(False)
                self.nodes_table.setVisible(False)
        
    def on_signal_double_clicked(self, item):
        """Handle double-click on a signal in the signals table"""
        if not self.current_handler or not hasattr(self, 'signals_data'):
            return
            
        # Get the row of the clicked item
        row = item.row()
        
        # Get the signal data for this row
        signal_data = self.signals_data[row]
        
        # Show the signal detail view
        signal_detail = SignalDetailView(signal_data, self)
        signal_detail.show()  # Use show() instead of exec_() to allow multiple windows
        
    def on_message_double_clicked(self, item):
        """Handle double-click on a message in the messages table"""
        if not self.current_handler or not hasattr(self, 'messages_data'):
            return
            
        # Get the row of the clicked item
        row = item.row()
        
        # Get the message data for this row
        message_data = self.messages_data[row]
        
        # Show the message detail view
        message_detail = MessageDetailView(message_data, self)
        message_detail.show()  # Use show() to allow multiple windows

    def show_node_details(self, node_name):
        """Show details for a node"""
        if not self.current_handler:
            return
            
        # Find the node data
        nodes = self.current_handler.get_nodes()
        node_data = None
        for node in nodes:
            if node['name'] == node_name:
                node_data = node
                break
            
        if not node_data:
            return
        
        # Get node messages and signals
        node_messages = self.current_handler.get_node_messages(node_name)
        node_signals = self.current_handler.get_node_signals(node_name)
        
        # Show node detail view
        node_detail = NodeDetailView(node_data, node_messages, node_signals, self)
        node_detail.show()
        
    def on_node_double_clicked(self, item):
        """Handle double-click on a node in the nodes table"""
        if not self.current_handler:
            return
        
        # Get the row of the clicked item
        row = item.row()
        
        # Get the node name from the first column
        node_name = self.nodes_table.item(row, 0).text()
        
        # Show node details
        self.show_node_details(node_name)

    def organize_node_messages(self, node_name: str, messages: list) -> tuple[list, list]:
        """
        Organize messages into Tx and Rx lists for a given node
        
        Args:
            node_name: Name of the node
            messages: List of all messages
            
        Returns:
            tuple[list, list]: (tx_messages, rx_messages)
        """
        tx_messages = []
        rx_messages = []
        
        for msg in messages:
            # Check if node is a sender
            if node_name in msg['senders']:
                tx_messages.append(msg)
            
            # Check if node is a receiver of any signal
            is_receiver = False
            for signal in msg['signals']:
                if node_name in signal['receivers']:
                    is_receiver = True
                    break
            
            if is_receiver:
                rx_messages.append(msg)
                
        return tx_messages, rx_messages

    def add_message_to_tree(self, parent_item: QTreeWidgetItem, message: dict):
        """
        Add a message to the tree under the specified parent
        
        Args:
            parent_item: Parent tree item
            message: Message dictionary
        """
        msg_item = QTreeWidgetItem()
        msg_item.setText(0, f"{message['name']} (ID: 0x{message['frame_id']:X})")
        msg_item.setIcon(0, self.get_message_icon())
        parent_item.addChild(msg_item)

    def add_signal_to_tree(self, parent_item: QTreeWidgetItem, signal: dict):
        """
        Add a signal to the tree under the specified parent
        
        Args:
            parent_item: Parent tree item
            signal: Signal dictionary
        """
        signal_item = QTreeWidgetItem()
        signal_item.setText(0, signal['name'])
        signal_item.setIcon(0, self.get_signal_icon())
        parent_item.addChild(signal_item)

    def update_display(self, handler: DBC_IO_Handler):
        """Update the display with information from the handler"""
        if not handler or not handler.is_valid():
            self.clear_display()
            return
            
        self.current_handler = handler
            
        # Update file name and show the label
        file_info = handler.get_file_info()
        self.file_name_label.setText(f"File: {file_info['file_name']}")
        self.file_name_label.show()
        
        # Add bus load calculator button
        if not self.bus_load_button:
            self.bus_load_button = QPushButton("Bus Load Calculator")
            self.bus_load_button.setToolTip("Calculate CAN bus load based on message properties")
            self.bus_load_button.clicked.connect(self.show_bus_load_calculator)
            # Insert before the stretch
            self.buttons_layout.insertWidget(self.buttons_layout.count() - 1, self.bus_load_button)
        
        # Show the main splitter when file is loaded
        self.main_splitter.show()
        
        # Update tree
        self.tree_widget.clear()
        
        # Create root items
        nodes_root = QTreeWidgetItem(self.tree_widget)
        nodes_root.setText(0, "Network Nodes")
        nodes_root.setExpanded(False)
        
        messages_root = QTreeWidgetItem(self.tree_widget)
        messages_root.setText(0, "Messages")
        messages_root.setExpanded(False)
        
        signals_root = QTreeWidgetItem(self.tree_widget)
        signals_root.setText(0, "Signals")
        signals_root.setExpanded(False)
        
        # Get all nodes
        nodes = handler.get_nodes()
        
        # Add nodes with their messages and signals
        for node in nodes:
            node_item = QTreeWidgetItem()
            node_item.setText(0, node['name'])
            if node['comment']:
                node_item.setToolTip(0, node['comment'])
            node_item.setIcon(0, self.get_node_icon())
            nodes_root.addChild(node_item)
            
            # Get messages and signals for this node from handler
            node_messages = handler.get_node_messages(node['name'])
            node_signals = handler.get_node_signals(node['name'])
            
            # Add Tx Messages group
            tx_messages_group = QTreeWidgetItem()
            tx_messages_group.setText(0, "Tx Messages")
            node_item.addChild(tx_messages_group)
            for msg in node_messages['tx_messages']:
                self.add_message_to_tree(tx_messages_group, msg)
            
            # Add Rx Messages group
            rx_messages_group = QTreeWidgetItem()
            rx_messages_group.setText(0, "Rx Messages")
            node_item.addChild(rx_messages_group)
            for msg in node_messages['rx_messages']:
                self.add_message_to_tree(rx_messages_group, msg)
            
            # Add Tx Signals group
            tx_signals_group = QTreeWidgetItem()
            tx_signals_group.setText(0, "Tx Signals")
            node_item.addChild(tx_signals_group)
            for signal in node_signals['tx_signals']:
                self.add_signal_to_tree(tx_signals_group, signal)
            
            # Add Rx Signals group
            rx_signals_group = QTreeWidgetItem()
            rx_signals_group.setText(0, "Rx Signals")
            node_item.addChild(rx_signals_group)
            for signal in node_signals['rx_signals']:
                self.add_signal_to_tree(rx_signals_group, signal)

        # Add messages to Messages root
        messages = handler.get_messages()
        for msg in messages:
            msg_item = QTreeWidgetItem()
            msg_item.setText(0, f"{msg['name']} (ID: 0x{msg['frame_id']:X})")
            msg_item.setIcon(0, self.get_message_icon())
            messages_root.addChild(msg_item)
            
            # Add message details as child items
            details_item = QTreeWidgetItem()
            details_item.setText(0, f"Length: {msg['length']} bytes")
            msg_item.addChild(details_item)
            
            if msg['comment']:
                comment_item = QTreeWidgetItem()
                comment_item.setText(0, f"Comment: {msg['comment']}")
                msg_item.addChild(comment_item)
                
            if msg['senders']:
                senders_item = QTreeWidgetItem()
                senders_item.setText(0, f"Senders: {', '.join(msg['senders'])}")
                msg_item.addChild(senders_item)
            
            # Add signals group under message
            if msg['signals']:
                signals_item = QTreeWidgetItem()
                signals_item.setText(0, "Signals")
                msg_item.addChild(signals_item)
                
                # Add each signal with its details
                for signal in msg['signals']:
                    signal_item = QTreeWidgetItem()
                    signal_item.setText(0, signal['name'])
                    signal_item.setIcon(0, self.get_signal_icon())
                    signals_item.addChild(signal_item)
                    
                    # Add signal details as child items
                    signal_details = [
                        f"Start bit: {signal['start']}",
                        f"Length: {signal['length']} bits",
                        f"Byte order: {signal['byte_order']}",
                        f"Signed: {'Yes' if signal['is_signed'] else 'No'}",
                        f"Scale: {signal['scale']}",
                        f"Offset: {signal['offset']}"
                    ]
                    
                    # Add optional signal details if they exist
                    if signal['minimum'] is not None:
                        signal_details.append(f"Minimum: {signal['minimum']}")
                    if signal['maximum'] is not None:
                        signal_details.append(f"Maximum: {signal['maximum']}")
                    if signal['unit']:
                        signal_details.append(f"Unit: {signal['unit']}")
                    if signal['comment']:
                        signal_details.append(f"Comment: {signal['comment']}")
                    if signal['receivers']:
                        signal_details.append(f"Receivers: {', '.join(signal['receivers'])}")
                    
                    # Add all details as child items
                    for detail in signal_details:
                        detail_item = QTreeWidgetItem()
                        detail_item.setText(0, detail)
                        signal_item.addChild(detail_item)
        
        # Add signals to Signals root
        signals = handler.get_signals()
        for signal in signals:
            signal_item = QTreeWidgetItem()
            signal_item.setText(0, f"{signal['name']} ({signal['message_name']} - ID: 0x{signal['message_id']:X})")
            signal_item.setIcon(0, self.get_signal_icon())
            signals_root.addChild(signal_item)
            
            # Add signal details as child items
            signal_details = [
                f"Start bit: {signal['start']}",
                f"Length: {signal['length']} bits",
                f"Byte order: {signal['byte_order']}",
                f"Signed: {'Yes' if signal['is_signed'] else 'No'}",
                f"Scale: {signal['scale']}",
                f"Offset: {signal['offset']}"
            ]
            
            # Add optional signal details if they exist
            if signal['minimum'] is not None:
                signal_details.append(f"Minimum: {signal['minimum']}")
            if signal['maximum'] is not None:
                signal_details.append(f"Maximum: {signal['maximum']}")
            if signal['unit']:
                signal_details.append(f"Unit: {signal['unit']}")
            if signal['comment']:
                signal_details.append(f"Comment: {signal['comment']}")
            if signal['receivers']:
                signal_details.append(f"Receivers: {', '.join(signal['receivers'])}")
            
            # Add all details as child items
            for detail in signal_details:
                detail_item = QTreeWidgetItem()
                detail_item.setText(0, detail)
                signal_item.addChild(detail_item)
            
    def get_node_icon(self):
        """Returns a default icon for nodes"""
        return QIcon()
        
    def get_message_icon(self):
        """Returns a default icon for messages"""
        return QIcon()
        
    def get_signal_icon(self):
        """Returns a default icon for signals"""
        return QIcon()
            
    def clear_display(self):
        """Clear all displayed information"""
        self.file_name_label.hide()  # Hide the label instead of setting text
        self.tree_widget.clear()
        self.signals_table.setVisible(False)
        self.messages_table.setVisible(False)
        self.nodes_table.setVisible(False)
        self.main_splitter.hide()
        self.current_handler = None
        
        # Remove bus load calculator button if it exists
        if self.bus_load_button:
            self.bus_load_button.setParent(None)  # Remove from layout
            self.bus_load_button = None

    def is_message_item(self, item):
        """Check if the tree item represents a message"""
        # Check if item text contains "(ID:" which is our message format
        if "(ID:" in item.text(0):
            # Make sure it's not under a Signals parent (which also shows message ID)
            parent = item.parent()
            if parent and parent.text(0) == "Messages":
                return True
            # Check if it's under Tx/Rx Messages in a node
            if parent and parent.text(0) in ["Tx Messages", "Rx Messages"]:
                return True
        return False
        
    def get_message_data_from_item(self, item):
        """Get message data from a tree item"""
        # Extract message name from the item text (format: "name (ID: 0xXX)")
        message_name = item.text(0).split(" (ID:")[0]
        
        # If it's under a node's Tx/Rx messages
        parent = item.parent()
        if parent and parent.text(0) in ["Tx Messages", "Rx Messages"]:
            node_item = parent.parent()
            if node_item:
                node_name = node_item.text(0)
                node_messages = self.current_handler.get_node_messages(node_name)
                # Search in tx_messages or rx_messages based on parent text
                messages_list = node_messages['tx_messages'] if parent.text(0) == "Tx Messages" else node_messages['rx_messages']
                for msg in messages_list:
                    if msg['name'] == message_name:
                        return msg
        
        # If it's under the main Messages root or anywhere else
        messages = self.current_handler.get_messages()
        for msg in messages:
            if msg['name'] == message_name:
                return msg
                
        return None

    def show_bus_load_calculator(self):
        """Show the bus load calculator dialog."""
        if not self.current_handler or not self.current_handler.is_valid():
            return
            
        # Get messages from the handler
        messages = self.current_handler.get_messages()
        
        # Create and show the dialog
        dialog = BusLoadDialog(messages, self)
        dialog.exec_() 