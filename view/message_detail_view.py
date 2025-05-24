from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QScrollArea, QWidget, QTableWidget,
                            QTableWidgetItem, QHeaderView, QFrame, QSizePolicy,
                            QTabWidget, QMessageBox, QStyle)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from .signal_layout_view import SignalLayoutView
from .signal_detail_view import SignalDetailView
from .message_edit_dialog import MessageEditDialog

class MessageDetailView(QDialog):
    message_edited = pyqtSignal(dict, dict)  # old_message, new_message
    
    def __init__(self, message_data, handler, parent=None):
        super().__init__(parent)
        self.message_data = message_data.copy()  # Make a copy to track changes
        self.handler = handler
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set window properties
        self.setWindowTitle(f"Message Details: {self.message_data['name']}")
        self.setMinimumSize(700, 600)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowSystemMenuHint)
        
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create header with message name
        header_frame = QFrame()
        header_frame.setFrameShape(QFrame.StyledPanel)
        header_frame.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(10, 10, 10, 10)
        
        self.message_name_label = QLabel(self.message_data['name'])
        self.message_name_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_layout.addWidget(self.message_name_label)
        
        message_id = QLabel(f"ID: 0x{self.message_data['frame_id']:X}")
        message_id.setFont(QFont("Arial", 10))
        header_layout.addWidget(message_id)
        
        # Add Edit button
        edit_button = QPushButton("Edit")
        edit_button.setToolTip("Edit message name")
        edit_button.setMinimumWidth(80)
        edit_button.clicked.connect(self.open_edit_dialog)
        header_layout.addWidget(edit_button)
        
        main_layout.addWidget(header_frame)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Add Details tab
        details_tab = self.create_details_table()
        tab_widget.addTab(details_tab, "Details")
        
        # Add Signals tab
        signals_tab = self.create_signals_table()
        tab_widget.addTab(signals_tab, "Signals")
        
        # Add Signal Layout tab
        signal_layout_tab = self.create_signal_layout_tab()
        tab_widget.addTab(signal_layout_tab, "Signal Layout")
        
        main_layout.addWidget(tab_widget)
        
        # Add close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setFixedWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
    def create_details_table(self):
        """Create the details table widget"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        table = QTableWidget()
        table.setColumnCount(2)
        table.setHorizontalHeaderLabels(["Property", "Value"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.setStyleSheet("""
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
        
        # Helper function to format value
        def format_value(value):
            if value is None:
                return "Not specified"
            if isinstance(value, bool):
                return "Yes" if value else "No"
            if isinstance(value, (dict, list)) and not value:
                return "None"
            if isinstance(value, dict):
                return ", ".join([f"{k}: {v}" for k, v in value.items()])
            if isinstance(value, list):
                return ", ".join(str(v) for v in value)
            return str(value)
        
        # Check if any signal is a multiplexer
        is_multiplexed = False
        for signal in self.message_data['signals']:
            if signal.get('is_multiplexer', False):
                is_multiplexed = True
                break
        
        # Get J1939 specifics if available
        j1939_specifics = self.message_data.get('j1939_specifics', {}) or {}
        if not isinstance(j1939_specifics, dict):
            j1939_specifics = {}
        
        # Determine protocol type
        protocol = "Standard CAN"
        if self.message_data.get('is_fd', False):
            protocol = "CAN FD"
        elif j1939_specifics:
            protocol = "J1939"
        
        # Define all properties with their values
        properties = [
            # Basic Properties
            ("Basic Properties", None),  # Header
            ("Name", self.message_data['name']),
            ("Frame ID", f"0x{self.message_data['frame_id']:X}"),
            ("Length", f"{self.message_data['length']} bytes"),
            ("Protocol", protocol),
            ("Signals Count", str(len(self.message_data['signals']))),
            ("Comment", self.message_data['comment'] if self.message_data['comment'] else "No comment"),
            
            # Senders
            ("Senders", None),  # Header
            ("Senders List", ", ".join(self.message_data['senders']) if self.message_data['senders'] else "None"),
            
            # Receivers
            ("Receivers", None),  # Header
            ("Receivers List", ", ".join(self.message_data.get('receivers', [])) if self.message_data.get('receivers', []) else "None"),
            
            # Frame Format
            ("Frame Format", None),  # Header
            ("Frame Format Type", self.message_data.get('frame_format', 'Not specified')),
            ("Extended Frame", format_value(self.message_data.get('is_extended_frame', False))),
            ("CAN FD", format_value(self.message_data.get('is_fd', False))),
            ("Bus Name", format_value(self.message_data.get('bus_name'))),
            
            # Header Information
            ("Header Information", None),  # Header
            ("Header ID", f"0x{self.message_data.get('header_id', 0):X}" if self.message_data.get('header_id') is not None else "Not specified"),
            ("Header Byte Order", format_value(self.message_data.get('header_byte_order'))),
            ("Unused Bit Pattern", f"0x{self.message_data.get('unused_bit_pattern', 0):X}"),
            
            # Timing Information
            ("Timing Information", None),  # Header
        ]
        
        # Add Send Type if it exists, otherwise show N/A
        send_type = self.message_data.get('send_type')
        if send_type:
            properties.append(("Send Type", format_value(send_type)))
        else:
            properties.append(("Send Type", "N/A"))
            
        # Add Cycle Time
        cycle_time = self.message_data.get('cycle_time')
        if cycle_time is None and hasattr(self.message_data, 'dbc') and hasattr(self.message_data.dbc, 'attributes'):
            attr = self.message_data.dbc.attributes.get('GenMsgCycleTime')
            if attr is not None and hasattr(attr, 'value'):
                cycle_time = attr.value
        properties.append(("Cycle Time", f"{cycle_time} ms" if cycle_time is not None else "Not specified"))
        
        # Add available send types only if they exist
        if self.message_data.get('send_type_choices'):
            properties.append(("Available Send Types", self.format_send_type_choices()))
            
        # Add available frame format choices if they exist
        if self.message_data.get('frame_format_choices'):
            properties.append(("Available Frame Formats", self.format_frame_format_choices()))
            
        # Multiplexing
        properties.extend([
            ("Multiplexing", None),  # Header
            ("Is Multiplexed", format_value(is_multiplexed)),
        ])
        
        # J1939 Properties
        properties.extend([
            ("J1939 Properties", None),  # Header
            ("PGN", format_value(j1939_specifics.get('pgn'))),
            ("Priority", format_value(j1939_specifics.get('priority'))),
            ("Source Address", format_value(j1939_specifics.get('source_address'))),
            ("Destination Address", format_value(j1939_specifics.get('destination_address'))),
            ("PDU Format", format_value(j1939_specifics.get('pdu_format'))),
            ("PDU Specific", format_value(j1939_specifics.get('pdu_specific'))),
            ("Name", format_value(j1939_specifics.get('name'))),
            ("ID", format_value(j1939_specifics.get('id'))),
        ])
        
        # DBC Specifics
        dbc_specifics = self.message_data.get('dbc_specifics', {}) or {}
        if dbc_specifics and isinstance(dbc_specifics, dict):
            properties.extend([
                ("DBC Specifics", None),  # Header
            ])
            for key, value in dbc_specifics.items():
                properties.append((key, format_value(value)))
        
        # AUTOSAR Specifics
        autosar_specifics = self.message_data.get('autosar_specifics', {}) or {}
        if autosar_specifics and isinstance(autosar_specifics, dict):
            properties.extend([
                ("AUTOSAR Specifics", None),  # Header
            ])
            for key, value in autosar_specifics.items():
                properties.append((key, format_value(value)))
        
        # Contained Messages
        properties.append(("Contained Messages", None))  # Header
        
        # Add contained messages if they exist
        if self.message_data.get('contained_messages') and len(self.message_data['contained_messages']) > 0:
            for i, contained_msg in enumerate(self.message_data['contained_messages']):
                properties.append((f"Contained Message {i+1}", f"{contained_msg['name']} (ID: 0x{contained_msg['frame_id']:X}, Length: {contained_msg['length']} bytes)"))
        else:
            properties.append(("Contained Messages", "None"))
        
        # Filter out any None entries that might have been conditionally added
        properties = [prop for prop in properties if prop is not None]
        
        # Set table rows
        table.setRowCount(len(properties))
        
        # Add all rows to table
        for row, (prop_name, prop_value) in enumerate(properties):
            # Check if this is a header row
            if prop_value is None:
                header_item = QTableWidgetItem(prop_name)
                header_item.setBackground(Qt.lightGray)
                header_item.setFont(QFont("Arial", 11, QFont.Bold))
                table.setItem(row, 0, header_item)
                table.setSpan(row, 0, 1, 2)
            else:
                name_item = QTableWidgetItem(prop_name)
                name_item.setFont(QFont("Arial", 10))
                value_item = QTableWidgetItem(str(prop_value))
                value_item.setFont(QFont("Arial", 10))
                
                table.setItem(row, 0, name_item)
                table.setItem(row, 1, value_item)
        
        scroll_area.setWidget(table)
        return scroll_area
        
    def create_signals_table(self):
        """Create the signals table with tabs for receivers"""
        # Container widget
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Add "Add Signal" button at the top
        button_layout = QHBoxLayout()
        add_signal_button = QPushButton("Add Signal")
        add_signal_button.setIcon(self.style().standardIcon(QStyle.SP_FileDialogNewFolder))
        add_signal_button.clicked.connect(self.open_add_signal_dialog)
        button_layout.addWidget(add_signal_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Create tab widget for organizing signals by receivers
        signals_tab_widget = QTabWidget()
        
        # Add "All Signals" tab first
        all_signals_tab = self.create_signal_list_tab(self.message_data['signals'], "All Signals")
        signals_tab_widget.addTab(all_signals_tab, f"All Signals ({len(self.message_data['signals'])})")
        
        # Organize signals by receivers
        receiver_signals = {}
        
        # Group signals by receiver
        for signal in self.message_data['signals']:
            receivers = signal['receivers']
            if not receivers:
                # Skip signals with no receivers
                continue
            
            for receiver in receivers:
                if receiver not in receiver_signals:
                    receiver_signals[receiver] = []
                receiver_signals[receiver].append(signal)
        
        # Create a tab for each receiver with their signals
        for receiver, signals in receiver_signals.items():
            receiver_tab = self.create_signal_list_tab(signals, f"Received by {receiver}")
            signals_tab_widget.addTab(receiver_tab, f"{receiver} ({len(signals)})")
        
        layout.addWidget(signals_tab_widget)
        return container

    def create_signal_layout_tab(self):
        """Create a tab with the signal layout visualization"""
        # Use a container widget to hold the layout view
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Import signal layout here to avoid circular imports
        from .signal_layout_view import SignalLayoutViewWidget
        
        # Create signal layout widget (a version without dialog popup)
        signal_layout_widget = SignalLayoutViewWidget(self.message_data)
        layout.addWidget(signal_layout_widget)
        
        return container

    def create_signal_list_tab(self, signals, title):
        """Create a tab with a list of signals"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        table = QTableWidget()
        columns = [
            "Name", "Start Bit", "Length", "Byte Order", "Signed",
            "Scale", "Offset", "Minimum", "Maximum", "Unit", 
            "Is Multiplexer", "Multiplexer ID", "Is Float", "Choices",
            "Receivers"
        ]
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)
        
        # Enable manual column resizing
        for i in range(len(columns)):
            table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        
        # Set stretch for the last column
        table.horizontalHeader().setStretchLastSection(True)
        
        # Set column widths
        column_widths = {
            "Name": 150,
            "Start Bit": 80,
            "Length": 80,
            "Byte Order": 100,
            "Signed": 80,
            "Scale": 80,
            "Offset": 80,
            "Minimum": 80,
            "Maximum": 80,
            "Unit": 80,
            "Is Multiplexer": 100,
            "Multiplexer ID": 100,
            "Is Float": 80,
            "Choices": 150,
            "Receivers": 200
        }
        
        # Apply initial column widths
        for i, col in enumerate(columns):
            table.setColumnWidth(i, column_widths.get(col, 100))
        
        table.setStyleSheet("""
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
        
        # Helper function to format value
        def format_value(value):
            if value is None:
                return ""
            if isinstance(value, bool):
                return "Yes" if value else "No"
            if isinstance(value, (dict, list)) and not value:
                return ""
            if isinstance(value, dict):
                return ", ".join([f"{k}: {v}" for k, v in value.items()])
            return str(value)
        
        # Add signals data
        table.setRowCount(len(signals))
        
        for row, signal in enumerate(signals):
            # Count choices if available
            choices_str = ""
            if signal.get('choices') and isinstance(signal.get('choices'), dict):
                choices = signal.get('choices')
                choices_str = ", ".join([f"{k}={v}" for k, v in choices.items()])
                if len(choices_str) > 50:
                    choices_str = f"{len(choices)} choices"
            
            items = [
                QTableWidgetItem(signal['name']),
                QTableWidgetItem(str(signal['start'])),
                QTableWidgetItem(str(signal['length'])),
                QTableWidgetItem(signal['byte_order']),
                QTableWidgetItem(format_value(signal['is_signed'])),
                QTableWidgetItem(str(signal['scale'])),
                QTableWidgetItem(str(signal['offset'])),
                QTableWidgetItem(str(signal['minimum']) if signal['minimum'] is not None else ''),
                QTableWidgetItem(str(signal['maximum']) if signal['maximum'] is not None else ''),
                QTableWidgetItem(signal['unit'] if signal['unit'] else ''),
                QTableWidgetItem(format_value(signal.get('is_multiplexer', False))),
                QTableWidgetItem(format_value(signal.get('multiplexer_id'))),
                QTableWidgetItem(format_value(signal.get('is_float', False))),
                QTableWidgetItem(choices_str),
                QTableWidgetItem(', '.join(signal['receivers']) if signal['receivers'] else '')
            ]
            
            for col, item in enumerate(items):
                table.setItem(row, col, item)
        
        # Connect double-click handler to open signal details
        table.itemDoubleClicked.connect(lambda item: self.show_signal_details(signals[item.row()]))
        
        scroll_area.setWidget(table)
        return scroll_area
    
    def show_signal_details(self, signal):
        """Show details for a signal"""
        # Make a copy of the signal data to avoid modifying the original
        signal_copy = signal.copy()
        
        # Add message information if it's missing
        if 'message_name' not in signal_copy:
            signal_copy['message_name'] = self.message_data['name']
        if 'message_id' not in signal_copy:
            signal_copy['message_id'] = self.message_data['frame_id']
        
        # Find handler from parent chain (assume parent is DBCDisplayView)
        handler = None
        parent = self.parent()
        while parent:
            if hasattr(parent, 'current_handler'):
                handler = parent.current_handler
                break
            parent = parent.parent() if hasattr(parent, 'parent') else None
        
        signal_detail = SignalDetailView(signal_copy, handler, self)
        signal_detail.show()

    def open_edit_dialog(self):
        """Open the edit dialog for this message"""
        edit_dialog = MessageEditDialog(
            self.message_data['name'],
            self.message_data,
            self.handler,
            self
        )
        
        # Connect edit signals
        edit_dialog.name_edited.connect(self.handle_name_edited)
        edit_dialog.frame_id_edited.connect(self.handle_frame_id_edited)
        edit_dialog.extended_frame_edited.connect(self.handle_extended_frame_edited)
        edit_dialog.message_deleted.connect(self.handle_message_deleted)
        edit_dialog.senders_edited.connect(self.handle_senders_edited)
        edit_dialog.receivers_edited.connect(self.handle_receivers_edited)
        edit_dialog.send_type_edited.connect(self.handle_send_type_edited)
        edit_dialog.frame_format_edited.connect(self.handle_frame_format_edited)
        edit_dialog.cycle_time_edited.connect(self.handle_cycle_time_edited)
        
        edit_dialog.exec_()

    def handle_name_edited(self, new_name):
        if new_name == self.message_data['name']:
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
        
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_name(
            self.message_data['name'],
            new_name
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data and UI
        self.message_data['name'] = new_name
        self.message_name_label.setText(new_name)
        self.setWindowTitle(f"Message Details: {new_name}")
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_frame_id_edited(self, new_frame_id: int):
        """Handle when frame ID is edited"""
        if new_frame_id == self.message_data['frame_id']:
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
        
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_frame_id(
            self.message_data['name'],
            new_frame_id
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data and UI
        self.message_data['frame_id'] = new_frame_id
        self.setWindowTitle(f"Message Details: {self.message_data['name']}")
        
        # Update frame ID in header
        for i in range(self.layout().count()):
            item = self.layout().itemAt(i)
            if isinstance(item.widget(), QFrame):  # Header frame
                header_layout = item.widget().layout()
                for j in range(header_layout.count()):
                    widget = header_layout.itemAt(j).widget()
                    if isinstance(widget, QLabel) and "ID:" in widget.text():
                        widget.setText(f"ID: 0x{new_frame_id:X}")
                        break
                break
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_extended_frame_edited(self, is_extended: bool):
        """Handle when extended frame flag is edited"""
        if is_extended == self.message_data.get('is_extended_frame', False):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
        
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_is_extended_frame(
            self.message_data['name'],
            is_extended
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.message_data['is_extended_frame'] = is_extended
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_message_deleted(self, message_name: str):
        """Handle message deletion"""
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for deletion.")
            return
            
        success, error = self.handler.edit_controller.delete_message(message_name)
        if not success:
            QMessageBox.critical(self, "Delete Error", error)
            return
            
        # Track the deletion
        if self.handler and hasattr(self.handler, 'change_tracker'):
            self.handler.change_tracker.add_message_deletion(message_name)
            
        # Close the dialog since the message no longer exists
        self.accept()

    def handle_senders_edited(self, new_senders: list):
        """Handle when senders are edited"""
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_senders(
            self.message_data['name'],
            new_senders
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.message_data['senders'] = new_senders
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_receivers_edited(self, new_receivers: list):
        """Handle when receivers are edited"""
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_receivers(
            self.message_data['name'],
            new_receivers
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.message_data['receivers'] = new_receivers
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_send_type_edited(self, new_send_type: str):
        """Handle when send type is edited"""
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
            
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_send_type(
            self.message_data['name'],
            new_send_type
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.message_data['send_type'] = new_send_type
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_frame_format_edited(self, new_frame_format: str):
        """Handle when frame format is edited"""
        if new_frame_format == self.message_data.get('frame_format', 'Not specified'):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
        
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_frame_format(
            self.message_data['name'],
            new_frame_format
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.message_data['frame_format'] = new_frame_format
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_cycle_time_edited(self, new_cycle_time: float):
        """Handle when cycle time is edited"""
        if new_cycle_time == self.message_data.get('cycle_time', 0):
            return  # No change
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for editing.")
            return
        
        old_message = self.message_data.copy()
        success, error = self.handler.edit_controller.edit_message_cycle_time(
            self.message_data['name'],
            new_cycle_time
        )
        if not success:
            QMessageBox.critical(self, "Edit Error", error)
            return
            
        # Update local data
        self.message_data['cycle_time'] = new_cycle_time
        
        # Emit signal with old and new message data
        self.handle_message_edited(old_message, self.message_data)

    def handle_message_edited(self, old_message: dict, new_message: dict):
        """Handle when message is edited and OK is clicked"""
        if self.handler and hasattr(self.handler, 'change_tracker'):
            self.handler.change_tracker.add_message_change(
                old_message,
                new_message
            )
        self.message_edited.emit(old_message, new_message)

    def format_send_type_choices(self):
        """Format the send type choices for display in the details table"""
        send_type_choices = self.message_data.get('send_type_choices')
        if not send_type_choices:
            return "Not specified"
            
        # Format based on data type
        if isinstance(send_type_choices, dict):
            # If it's a dictionary, format as "key: value"
            return ", ".join([f"{k}: {v}" for k, v in send_type_choices.items()])
        elif isinstance(send_type_choices, list):
            # If it's a list, just join with commas
            return ", ".join([str(v) for v in send_type_choices])
        else:
            # Otherwise, convert to string
            return str(send_type_choices)

    def format_frame_format_choices(self):
        """Format the frame format choices for display in the details table"""
        frame_format_choices = self.message_data.get('frame_format_choices')
        if not frame_format_choices:
            return "Not specified"
            
        # Format based on data type
        if isinstance(frame_format_choices, dict):
            # If it's a dictionary, format as "key: value"
            return ", ".join([f"{k}: {v}" for k, v in frame_format_choices.items()])
        elif isinstance(frame_format_choices, list):
            # If it's a list, just join with commas
            return ", ".join([str(v) for v in frame_format_choices])
        else:
            # Otherwise, convert to string
            return str(frame_format_choices)

    def open_add_signal_dialog(self):
        """Open the dialog to add a new signal to this message"""
        from .signal_add_dialog import SignalAddDialog
        
        dialog = SignalAddDialog(self.message_data, self.handler, self)
        dialog.signal_added.connect(self.handle_signal_added)
        dialog.exec_()
        
    def handle_signal_added(self, signal):
        """Handle when a new signal is added to the message"""
        if not self.handler or not self.handler.edit_controller:
            QMessageBox.critical(self, "Error", "Unable to find DBC handler for adding signal.")
            return
            
        # Try to add the signal to the message
        success, error = self.handler.edit_controller.add_signal(
            self.message_data['name'],
            signal
        )
        
        if not success:
            QMessageBox.critical(self, "Add Signal Error", error)
            return
            
        # Update the local message data to include the new signal
        self.message_data['signals'].append(signal)
        
        # Refresh the UI to show the new signal
        QMessageBox.information(self, "Signal Added", f"Signal '{signal['name']}' has been added successfully.")
        
        # Find the tab widget
        for i in range(self.layout().count()):
            widget = self.layout().itemAt(i).widget()
            if isinstance(widget, QTabWidget):
                # Find the "Signals" tab
                for j in range(widget.count()):
                    if widget.tabText(j).startswith("Signals"):
                        # Replace the tab with a new one
                        signals_tab = self.create_signals_table()
                        widget.removeTab(j)
                        widget.insertTab(j, signals_tab, f"Signals ({len(self.message_data['signals'])})")
                        # Keep the current tab active instead of switching to signal layout
                        widget.setCurrentIndex(j)
                        break
                
                # Update the signal layout tab
                for j in range(widget.count()):
                    if widget.tabText(j) == "Signal Layout":
                        # Replace the signal layout tab with a new one
                        signal_layout_tab = self.create_signal_layout_tab()
                        widget.removeTab(j)
                        widget.insertTab(j, signal_layout_tab, "Signal Layout")
                        break
                break