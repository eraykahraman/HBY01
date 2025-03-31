from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QTreeWidget, QTreeWidgetItem,
                            QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
                            QHeaderView, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from controller.dbc_io_handler import DBC_IO_Handler

class DBCDisplayView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_handler = None
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
        
        # Create main content widget
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(5)
        
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
        content_layout.addWidget(self.tree_widget)
        
        # Table view for signals
        self.table_widget = QTableWidget()
        self.table_widget.setStyleSheet("""
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
        content_layout.addWidget(self.table_widget)
        
        # Set size ratio between tree and table (30:70)
        content_layout.setStretch(0, 30)
        content_layout.setStretch(1, 70)
        
        layout.addWidget(content_widget)
        
    def setup_signals_table(self):
        """Setup the signals table structure"""
        columns = [
            "Name", "Message", "Message ID", "Start Bit", "Length", "Byte Order",
            "Signed", "Scale", "Offset", "Minimum", "Maximum", "Unit", "Comment", "Receivers"
        ]
        self.table_widget.setColumnCount(len(columns))
        self.table_widget.setHorizontalHeaderLabels(columns)
        header = self.table_widget.horizontalHeader()
        # Only make certain columns auto-resize
        for i, col in enumerate(columns):
            if col in ["Name", "Message", "Message ID", "Unit", "Comment", "Receivers"]:
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
            else:
                header.setSectionResizeMode(i, QHeaderView.Fixed)
                self.table_widget.setColumnWidth(i, 80)  # Fixed width for numeric columns
        
        self.table_widget.setVisible(False)  # Hide table initially
        
    def update_signals_table(self, signals):
        """Update the signals table with data"""
        # Temporarily disable sorting while updating
        self.table_widget.setSortingEnabled(False)
        
        # Clear existing items
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(len(signals))
        
        # Prepare all items first
        table_items = []
        for signal in signals:
            row_items = [
                QTableWidgetItem(signal['name']),
                QTableWidgetItem(signal['message_name']),
                QTableWidgetItem(f"0x{signal['message_id']:X}"),
                QTableWidgetItem(str(signal['start'])),
                QTableWidgetItem(str(signal['length'])),
                QTableWidgetItem(signal['byte_order']),
                QTableWidgetItem('Yes' if signal['is_signed'] else 'No'),
                QTableWidgetItem(str(signal['scale'])),
                QTableWidgetItem(str(signal['offset'])),
                QTableWidgetItem(str(signal['minimum']) if signal['minimum'] is not None else ''),
                QTableWidgetItem(str(signal['maximum']) if signal['maximum'] is not None else ''),
                QTableWidgetItem(signal['unit'] if signal['unit'] else ''),
                QTableWidgetItem(signal['comment'] if signal['comment'] else ''),
                QTableWidgetItem(', '.join(signal['receivers']) if signal['receivers'] else '')
            ]
            table_items.append(row_items)
        
        # Set all items at once
        for row, row_items in enumerate(table_items):
            for col, item in enumerate(row_items):
                self.table_widget.setItem(row, col, item)
        
        # Re-enable sorting
        self.table_widget.setSortingEnabled(True)
        self.table_widget.setVisible(True)
            
    def on_tree_item_clicked(self, item):
        """Handle tree item clicks"""
        if not self.current_handler:
            return
            
        # Check if the clicked item is the Signals root
        if item.text(0) == "Signals":
            signals = self.current_handler.get_signals()
            self.update_signals_table(signals)
        else:
            self.table_widget.setVisible(False)
        
    def update_display(self, handler: DBC_IO_Handler):
        """Update the display with information from the handler"""
        if not handler or not handler.is_valid():
            self.clear_display()
            return
            
        self.current_handler = handler
            
        # Update file name
        file_info = handler.get_file_info()
        self.file_name_label.setText(f"File: {file_info['file_name']}")
        
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
        
        # Add nodes
        nodes = handler.get_nodes()
        for node in nodes:
            node_item = QTreeWidgetItem()
            node_item.setText(0, node['name'])
            if node['comment']:
                node_item.setToolTip(0, node['comment'])
            node_item.setIcon(0, self.get_node_icon())
            nodes_root.addChild(node_item)
            
        # Add messages with their signals
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
        
        # Add all signals in a flat list under Signals root with their details
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
            
        # Hide the table initially
        self.table_widget.setVisible(False)
            
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
        self.file_name_label.setText("File: No file selected")
        self.tree_widget.clear()
        self.table_widget.setVisible(False)
        self.current_handler = None 