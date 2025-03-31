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
        
        # Tree view
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)  # Hide the header since we'll use root items
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
        
        # Update tree
        self.tree_widget.clear()
        
        # Create root items
        nodes_root = QTreeWidgetItem(self.tree_widget)
        nodes_root.setText(0, "Network Nodes")
        nodes_root.setExpanded(True)
        
        messages_root = QTreeWidgetItem(self.tree_widget)
        messages_root.setText(0, "Messages")
        messages_root.setExpanded(True)
        
        # Add nodes
        nodes = handler.get_nodes()
        for node in nodes:
            node_item = QTreeWidgetItem(nodes_root)
            node_item.setText(0, node['name'])
            if node['comment']:
                node_item.setToolTip(0, node['comment'])
            node_item.setIcon(0, self.get_node_icon())
            
        # Add messages
        messages = handler.get_messages()
        for msg in messages:
            msg_item = QTreeWidgetItem(messages_root)
            msg_item.setText(0, f"{msg['name']} (ID: 0x{msg['frame_id']:X})")
            
            # Add message details as child items
            details_item = QTreeWidgetItem(msg_item)
            details_item.setText(0, f"Length: {msg['length']} bytes")
            
            if msg['comment']:
                comment_item = QTreeWidgetItem(msg_item)
                comment_item.setText(0, f"Comment: {msg['comment']}")
                
            if msg['senders']:
                senders_item = QTreeWidgetItem(msg_item)
                senders_item.setText(0, f"Senders: {', '.join(msg['senders'])}")
            
            # Add signals group
            if msg['signals']:
                signals_item = QTreeWidgetItem(msg_item)
                signals_item.setText(0, "Signals")
                
                # Add each signal with its details
                for signal in msg['signals']:
                    signal_item = QTreeWidgetItem(signals_item)
                    signal_item.setText(0, signal['name'])
                    
                    # Add signal details
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
                        detail_item = QTreeWidgetItem(signal_item)
                        detail_item.setText(0, detail)
                    
                    signal_item.setIcon(0, self.get_signal_icon())
                
            msg_item.setIcon(0, self.get_message_icon())
            
    def get_node_icon(self):
        """Returns a default icon for nodes"""
        # You can replace this with actual icon loading
        return QIcon()
        
    def get_message_icon(self):
        """Returns a default icon for messages"""
        # You can replace this with actual icon loading
        return QIcon()
        
    def get_signal_icon(self):
        """Returns a default icon for signals"""
        # You can replace this with actual icon loading
        return QIcon()
            
    def clear_display(self):
        """Clear all displayed information"""
        self.file_name_label.setText("File: No file selected")
        self.tree_widget.clear() 