from typing import Optional, Dict, Any, List, TYPE_CHECKING
from cantools.database import Database
import os
from model.dbc_model import DBCModel
from PyQt5.QtCore import QObject, pyqtSignal
from controller.edit_controller import EditController  # Move this out of TYPE_CHECKING
from .change_tracker import ChangeTracker

if TYPE_CHECKING:
    from controller.edit_controller import EditController

class DBC_IO_Handler(QObject):
    # Signals emitted when nodes or messages list changes
    nodes_changed = pyqtSignal(list)
    messages_changed = pyqtSignal(list)
    signals_changed = pyqtSignal(list)  # New signal for signals list changes
    
    def __init__(self, file_path: str, model: DBCModel):
        """
        Initialize a DBC IO Handler for a specific DBC file
        
        Args:
            file_path (str): Path to the DBC file
            model (DBCModel): Reference to the main DBC model
        """
        super().__init__()
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.model = model
        self.database: Optional[Database] = None
        self.is_loaded: bool = False
        self.nodes: List[Dict[str, Any]] = []  # Store the list of nodes
        self.messages: List[Dict[str, Any]] = []  # Store the list of messages
        self.signals: List[Dict[str, Any]] = []  # Store the list of all signals
        self.edit_controller: Optional[EditController] = None
        self.change_tracker = ChangeTracker()
        # Connect to model signals to capture error messages
        self.model.dbc_error.connect(self._on_model_error)
        self.last_error: Optional[str] = None
        
    def _on_model_error(self, error_msg: str):
        """Store the last error message from the model"""
        self.last_error = error_msg
        
    def load_dbc(self) -> tuple[bool, Optional[str]]:
        """
        Load the DBC file into memory using the DBCModel
        
        Returns:
            tuple[bool, Optional[str]]: (Success status, Error message if any)
        """
        try:
            if not os.path.exists(self.file_path):
                return False, f"File not found: {self.file_path}"
                
            self.last_error = None  # Reset last error before attempting load
            if self.model.load_dbc(self.file_path):
                self.database = self.model.get_dbc(self.file_path)
                self.is_loaded = True
                # Create EditController instance
                self.edit_controller = EditController(self)
                # Parse nodes and messages after successful load
                self.nodes = self.parse_nodes()
                self.messages = self.parse_messages()
                self.signals = self.parse_all_signals()  # Parse all signals
                self.nodes_changed.emit(self.nodes)
                self.messages_changed.emit(self.messages)
                self.signals_changed.emit(self.signals)
                return True, None
            return False, self.last_error
        except Exception as e:
            return False, str(e)
            
    def get_database(self) -> Optional[Database]:
        """
        Returns the DBC database
        """
        # Always return our instance, not a new one from the model
        return self.database
        
    def update_database(self):
        """
        Update the in-memory data structures after database changes
        """
        if self.is_loaded and self.database:
            # Fix any None values in signals to prevent parsing errors
            self._validate_database_signals()
            
            # Update the model's database
            self.model.dbc_files[self.file_path] = self.database
            # Update local data structures
            self.nodes = self.parse_nodes()
            self.messages = self.parse_messages()
            self.signals = self.parse_all_signals()
            # Emit signals
            self.nodes_changed.emit(self.nodes)
            self.messages_changed.emit(self.messages)
            self.signals_changed.emit(self.signals)
        
    def _validate_database_signals(self):
        """
        Validate and fix any None values in signals that might cause parsing errors
        """
        if not self.database or not hasattr(self.database, 'messages'):
            return
            
        try:
            for message in self.database.messages:
                if not hasattr(message, 'signals'):
                    continue
                    
                for signal in message.signals:
                    # Ensure scale is never None
                    if signal.scale is None:
                        signal.scale = 1.0
                        
                    # Ensure offset is never None
                    if signal.offset is None:
                        signal.offset = 0.0
                        
                    # Calculate default min/max based on length and signedness
                    if signal.is_signed:
                        default_min = -(2 ** (signal.length - 1))
                        default_max = (2 ** (signal.length - 1)) - 1
                    else:
                        default_min = 0.0
                        default_max = (2 ** signal.length) - 1
                        
                    # Ensure minimum is never None
                    if signal.minimum is None:
                        signal.minimum = default_min
                        
                    # Ensure maximum is never None
                    if signal.maximum is None:
                        signal.maximum = default_max
                        
        except Exception as e:
            # Keep this error logging as it's important
            print(f"Warning: Error validating database signals: {str(e)}")
        
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the DBC file
        
        Returns:
            Dict[str, Any]: Dictionary containing file information
                - file_path (str): Full path to the DBC file
                - file_name (str): Name of the DBC file
                - is_loaded (bool): Whether the file is currently loaded
                - messages_count (int): Number of messages in the file
                - nodes_count (int): Number of nodes in the file
                - signals_count (int): Number of signals in the file
                - version (Optional[str]): Version of the DBC file
                - bit_timing (Optional[Dict[str, int]]): Bit timing information
                - nodes_timing (Optional[Dict[str, int]]): Node timing information
                - environment_variables (Optional[List[str]]): List of environment variables
                - environment_variable_data (Optional[List[Dict]]): Environment variable data
                - value_tables (Optional[List[Dict]]): Value tables
                - attributes (Optional[Dict[str, Any]]): File attributes
                - dbc_specifics (Optional[Dict[str, Any]]): DBC-specific information
                - autosar_specifics (Optional[Dict[str, Any]]): AUTOSAR-specific information
                - j1939_specifics (Optional[Dict[str, Any]]): J1939-specific information
        """
        db = self.get_database()
        if not db:
            return {
                "file_path": self.file_path,
                "file_name": self.file_name,
                "is_loaded": self.is_loaded,
                "messages_count": 0,
                "nodes_count": 0,
                "signals_count": 0
            }
            
        # Count signals
        signals_count = sum(len(msg.signals) for msg in db.messages)
        
        # Get additional database information
        file_info = {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "is_loaded": self.is_loaded,
            "messages_count": len(db.messages),
            "nodes_count": len(db.nodes),
            "signals_count": signals_count,
            "version": getattr(db, 'version', None),
            "bit_timing": getattr(db, 'bit_timing', None),
            "nodes_timing": getattr(db, 'nodes_timing', None),
            "environment_variables": [var.name for var in getattr(db, 'environment_variables', [])],
            "environment_variable_data": [
                {
                    "name": var.name,
                    "var_type": getattr(var, 'var_type', None),
                    "minimum": getattr(var, 'minimum', None),
                    "maximum": getattr(var, 'maximum', None),
                    "unit": getattr(var, 'unit', None),
                    "initial_value": getattr(var, 'initial_value', None),
                    "ev_id": getattr(var, 'ev_id', None),
                    "access_type": getattr(var, 'access_type', None),
                    "access_nodes": getattr(var, 'access_nodes', None)
                }
                for var in getattr(db, 'environment_variables', [])
            ],
            "value_tables": [
                {
                    "name": table.name,
                    "values": getattr(table, 'values', {})
                }
                for table in getattr(db, 'value_tables', [])
            ],
            "attributes": getattr(db, 'attributes', None),
            "dbc_specifics": getattr(db, 'dbc_specifics', None),
            "autosar_specifics": getattr(db, 'autosar_specifics', None),
            "j1939_specifics": getattr(db, 'j1939_specifics', None)
        }
        
        return file_info
        
    def parse_nodes(self) -> List[Dict[str, Any]]:
        """
        Parse all nodes from the DBC database
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing node information
                Each dictionary contains:
                - name (str): The name of the node
                - comment (Optional[str]): The comment associated with the node
                - address (Optional[str]): Node address from NmStationAddress attribute in hex format (e.g. "0xFE")
                - attributes (Optional[Dict[str, Any]]): Node attributes
                - ecu_ext_ref (Optional[str]): ECU external reference
                - dbc_specifics (Optional[Dict[str, Any]]): DBC-specific node information
                - autosar_specifics (Optional[Dict[str, Any]]): AUTOSAR-specific node information
                - j1939_specifics (Optional[Dict[str, Any]]): J1939-specific node information
                - function_name (Optional[str]): Function name (J1939)
                - manufacturer_code (Optional[int]): Manufacturer code (J1939)
                - manufacturer_specific_ecu_code (Optional[int]): Manufacturer-specific ECU code (J1939)
                - identity_number (Optional[int]): Identity number (J1939)
                - industry_group (Optional[int]): Industry group (J1939)
                - vehicle_system_instance (Optional[int]): Vehicle system instance (J1939)
                - vehicle_system (Optional[int]): Vehicle system (J1939)
                - function (Optional[int]): Function (J1939)
                - function_instance (Optional[int]): Function instance (J1939)
                - ecu_instance (Optional[int]): ECU instance (J1939)
                - manufacturer_ext (Optional[int]): Manufacturer extension (J1939)
                - is_j1939 (bool): Whether the node is a J1939 node
        """
        if not self.is_valid():
            return []
            
        nodes = []
        try:
            # Get attribute definition for NmStationAddress
            nm_station_address_def = None
            if hasattr(self.database, 'dbc') and hasattr(self.database.dbc, 'attribute_definitions'):
                nm_station_address_def = self.database.dbc.attribute_definitions.get('NmStationAddress')

            for node in self.database.nodes:
                # Check if node is a string (node name) or a Node object
                if isinstance(node, str):
                    node_info = {
                        "name": node,
                        "comment": None,
                        "address": None  # Default to None for string nodes
                    }
                else:
                    # Get node address from NmStationAddress attribute
                    node_address = None
                    if hasattr(node, 'dbc'):
                        if hasattr(node.dbc, 'attributes'):
                            if 'NmStationAddress' in node.dbc.attributes:
                                attr = node.dbc.attributes['NmStationAddress']
                                if hasattr(attr, 'value'):
                                    # If we have the attribute definition, use it to properly parse the value
                                    if nm_station_address_def:
                                        try:
                                            # Convert value according to attribute definition type
                                            if hasattr(nm_station_address_def, 'type'):
                                                if nm_station_address_def.type == 'INT':
                                                    node_address = int(attr.value)
                                                elif nm_station_address_def.type == 'HEX':
                                                    node_address = int(attr.value, 16)
                                                else:
                                                    node_address = attr.value
                                            else:
                                                # Default to integer if no type specified
                                                node_address = int(attr.value)
                                        except (ValueError, TypeError):
                                            # If conversion fails, use raw value
                                            node_address = attr.value
                                    else:
                                        # If no definition found, try to convert to int
                                        try:
                                            node_address = int(attr.value)
                                        except (ValueError, TypeError):
                                            node_address = attr.value
                            else:
                                # Try to get default value from attribute definition
                                if nm_station_address_def and hasattr(nm_station_address_def, 'default_value'):
                                    node_address = nm_station_address_def.default_value

                    # Convert address to hex format if it's a number
                    if node_address is not None:
                        try:
                            # Convert to integer first to handle both string and int inputs
                            node_address_int = int(node_address)
                            # Format as hex with 0x prefix
                            node_address = f"0x{node_address_int:02X}"
                        except (ValueError, TypeError):
                            # If conversion fails, keep the original value
                            pass

                    node_info = {
                        "name": node.name,
                        "comment": node.comment if hasattr(node, 'comment') else None,
                        "address": node_address,  # Use the hex formatted address
                        "attributes": getattr(node, 'attributes', None),
                        "ecu_ext_ref": getattr(node, 'ecu_ext_ref', None),
                        "dbc_specifics": getattr(node, 'dbc_specifics', None),
                        "autosar_specifics": getattr(node, 'autosar_specifics', None),
                        "j1939_specifics": getattr(node, 'j1939_specifics', None),
                        "function_name": getattr(node, 'function_name', None),
                        "manufacturer_code": getattr(node, 'manufacturer_code', None),
                        "manufacturer_specific_ecu_code": getattr(node, 'manufacturer_specific_ecu_code', None),
                        "identity_number": getattr(node, 'identity_number', None),
                        "industry_group": getattr(node, 'industry_group', None),
                        "vehicle_system_instance": getattr(node, 'vehicle_system_instance', None),
                        "vehicle_system": getattr(node, 'vehicle_system', None),
                        "function": getattr(node, 'function', None),
                        "function_instance": getattr(node, 'function_instance', None),
                        "ecu_instance": getattr(node, 'ecu_instance', None),
                        "manufacturer_ext": getattr(node, 'manufacturer_ext', None),
                        "is_j1939": getattr(node, 'is_j1939', False)
                    }
                nodes.append(node_info)
        except Exception as e:
            print(f"Error parsing node: {str(e)}")
            # Return empty list on error
            return []
            
        return nodes

    def parse_messages(self) -> List[Dict[str, Any]]:
        """
        Parse all messages from the DBC database
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing message information
                Each dictionary contains:
                - name (str): The name of the message
                - frame_id (int): The CAN frame ID
                - length (int): The message length in bytes
                - comment (Optional[str]): The comment associated with the message
                - senders (List[str]): List of node names that can send this message
                - receivers (List[str]): List of node names that receive this message (derived from signal receivers)
                - signals (List[Dict]): List of signals in the message, each containing:
                    - name (str): Signal name
                    - start (int): Start bit
                    - length (int): Signal length in bits
                    - byte_order (str): Byte order ('little_endian' or 'big_endian')
                    - is_signed (bool): Whether the signal is signed
                    - scale (float): Signal scaling factor
                    - offset (float): Signal offset
                    - minimum (Optional[float]): Minimum value
                    - maximum (Optional[float]): Maximum value
                    - unit (Optional[str]): Signal unit
                    - comment (Optional[str]): Signal comment
                    - receivers (List[str]): List of receiving nodes
                - contained_messages (Optional[List[Dict]]): List of contained messages
                - header_id (Optional[int]): Header ID for the message
                - header_byte_order (str): Byte order for the header ('little_endian' or 'big_endian')
                - unused_bit_pattern (int): Pattern for unused bits
                - send_type (Optional[str]): Type of sending mechanism
                - cycle_time (Optional[int]): Cycle time in milliseconds
                - is_extended_frame (bool): Whether the message uses extended frame format
                - is_fd (bool): Whether the message uses CAN FD format
                - bus_name (Optional[str]): Name of the bus the message belongs to
                - send_type_choices (Optional[Dict[int, str]]): Available choices for send_type
        """
        if not self.is_valid():
            return []
            
        messages = []
        try:
            # Extract send type choices if available
            send_type_choices = None
            frame_format_choices = None
            default_frame_format = None
            default_send_type = None
            if hasattr(self.database, 'dbc') and hasattr(self.database.dbc, 'attribute_definitions'):
                # Extract send type choices
                send_type_def = self.database.dbc.attribute_definitions.get('GenMsgSendType')
                if send_type_def and hasattr(send_type_def, 'choices'):
                    send_type_choices = send_type_def.choices
                    
                    # Get default send type if available
                    if hasattr(send_type_def, 'default_value'):
                        default_value = send_type_def.default_value
                        
                        if send_type_choices:
                            # Try to convert string to int if it represents a number
                            try:
                                default_value_int = int(default_value)
                                default_value = default_value_int
                            except (ValueError, TypeError):
                                pass
                                
                            if isinstance(send_type_choices, list) and isinstance(default_value, int):
                                if 0 <= default_value < len(send_type_choices):
                                    default_send_type = send_type_choices[default_value]
                            elif isinstance(send_type_choices, list) and default_value == "0":
                                # Special case for "0" string with list choices
                                default_send_type = send_type_choices[0]
                            elif isinstance(send_type_choices, dict) and default_value in send_type_choices:
                                default_send_type = send_type_choices[default_value]
                            else:
                                default_send_type = str(default_value)
                        else:
                            default_send_type = str(default_value)

                # Extract frame format choices and default
                frame_format_def = self.database.dbc.attribute_definitions.get('VFrameFormat')
                if frame_format_def:
                    if hasattr(frame_format_def, 'choices'):
                        frame_format_choices = frame_format_def.choices
                    
                    # Get default frame format
                    if hasattr(frame_format_def, 'default_value'):
                        default_value = frame_format_def.default_value
                        
                        if frame_format_choices:
                            # Try to convert string to int if it represents a number
                            try:
                                default_value_int = int(default_value)
                                default_value = default_value_int
                            except (ValueError, TypeError):
                                pass
                                
                            if isinstance(frame_format_choices, list) and isinstance(default_value, int):
                                if 0 <= default_value < len(frame_format_choices):
                                    default_frame_format = frame_format_choices[default_value]
                            elif isinstance(frame_format_choices, list) and default_value == "0":
                                # Special case for "0" string with list choices
                                default_frame_format = frame_format_choices[0]
                            elif isinstance(frame_format_choices, dict) and default_value in frame_format_choices:
                                default_frame_format = frame_format_choices[default_value]
                            else:
                                default_frame_format = str(default_value)
                        else:
                            default_frame_format = str(default_value)

            for msg in self.database.messages:
                # Check if message has all required attributes
                if not hasattr(msg, 'name'):
                    continue
                    
                # Parse signals
                signals = []
                # Collect all unique receivers across all signals in this message
                all_receivers = set()
                
                for signal in getattr(msg, 'signals', []):
                    if not hasattr(signal, 'name'):
                        continue
                        
                    # Get signal receivers
                    signal_receivers = [
                        node.name if hasattr(node, 'name') else str(node)
                        for node in getattr(signal, 'receivers', [])
                    ]
                    
                    # Add to the set of all receivers for this message
                    all_receivers.update(signal_receivers)
                    
                    signal_info = {
                        "name": signal.name,
                        "start": getattr(signal, 'start', 0),
                        "length": getattr(signal, 'length', 1),
                        "byte_order": "little_endian" if getattr(signal, 'byte_order', 'little_endian') == 'little_endian' else "big_endian",
                        "is_signed": getattr(signal, 'is_signed', False),
                        "scale": float(getattr(signal, 'scale', 1.0)),
                        "offset": float(getattr(signal, 'offset', 0.0)),
                        "minimum": float(getattr(signal, 'minimum', 0)) if hasattr(signal, 'minimum') else None,
                        "maximum": float(getattr(signal, 'maximum', 0)) if hasattr(signal, 'maximum') else None,
                        "unit": getattr(signal, 'unit', None),
                        "comment": getattr(signal, 'comment', None),
                        "receivers": signal_receivers
                    }
                    signals.append(signal_info)
                
                # Parse contained messages if they exist
                contained_messages = []
                if hasattr(msg, 'contained_messages') and msg.contained_messages:
                    for contained_msg in msg.contained_messages:
                        contained_msg_info = {
                            "name": contained_msg.name,
                            "frame_id": getattr(contained_msg, 'frame_id', 0),
                            "length": getattr(contained_msg, 'length', 0)
                        }
                        contained_messages.append(contained_msg_info)
                    
                message_info = {
                    "name": msg.name,
                    "frame_id": getattr(msg, 'frame_id', 0),
                    "length": getattr(msg, 'length', 0),
                    "comment": getattr(msg, 'comment', None),
                    "senders": [
                        node.name if hasattr(node, 'name') else str(node)
                        for node in getattr(msg, 'senders', [])
                    ],
                    "receivers": sorted(list(all_receivers)),  # Add sorted list of all unique receivers
                    "signals": signals,
                    "contained_messages": contained_messages,
                    "header_id": getattr(msg, 'header_id', None),
                    "header_byte_order": getattr(msg, 'header_byte_order', 'big_endian'),
                    "unused_bit_pattern": getattr(msg, 'unused_bit_pattern', 0),
                    "send_type": getattr(msg, 'send_type', None),
                    "cycle_time": getattr(msg, 'cycle_time', None),
                    "is_extended_frame": getattr(msg, 'is_extended_frame', False),
                    "is_fd": getattr(msg, 'is_fd', False),
                    "bus_name": getattr(msg, 'bus_name', None),
                    "send_type_choices": send_type_choices,
                    "frame_format_choices": frame_format_choices
                    # frame_format will be set below
                }
                
                # Patch: Always extract cycle_time from DBC attribute if not set
                if (message_info['cycle_time'] is None or message_info['cycle_time'] == "") and hasattr(msg, 'dbc') and hasattr(msg.dbc, 'attributes'):
                    attr = msg.dbc.attributes.get('GenMsgCycleTime')
                    if attr is not None and hasattr(attr, 'value'):
                        message_info['cycle_time'] = attr.value
                
                # Extract frame format attribute if it exists in message.dbc.attributes
                has_frame_format = False
                if hasattr(msg, 'dbc') and hasattr(msg.dbc, 'attributes'):
                    if 'VFrameFormat' in msg.dbc.attributes:
                        has_frame_format = True
                        frame_format_attr = msg.dbc.attributes['VFrameFormat']
                        if hasattr(frame_format_attr, 'value') and frame_format_choices:
                            # If it's an index into choices list
                            if isinstance(frame_format_choices, list) and isinstance(frame_format_attr.value, int):
                                if 0 <= frame_format_attr.value < len(frame_format_choices):
                                    message_info['frame_format'] = frame_format_choices[frame_format_attr.value]
                            # If it's a key into choices dict
                            elif isinstance(frame_format_choices, dict) and frame_format_attr.value in frame_format_choices:
                                message_info['frame_format'] = frame_format_choices[frame_format_attr.value]
                            else:
                                message_info['frame_format'] = str(frame_format_attr)
                        else:
                            message_info['frame_format'] = str(frame_format_attr)
                    elif default_frame_format is not None:
                        # Apply default frame format only if not explicitly set
                        message_info['frame_format'] = default_frame_format
                elif default_frame_format is not None:
                    # Still apply default if msg doesn't have dbc attributes at all
                    message_info['frame_format'] = default_frame_format
                
                # Extract send_type attribute if it exists in message.dbc.attributes
                if hasattr(msg, 'dbc') and hasattr(msg.dbc, 'attributes'):
                    if 'GenMsgSendType' in msg.dbc.attributes:
                        send_type_attr = msg.dbc.attributes['GenMsgSendType']
                        if hasattr(send_type_attr, 'value') and send_type_choices:
                            # If it's an index into choices list
                            if isinstance(send_type_choices, list) and isinstance(send_type_attr.value, int):
                                if 0 <= send_type_attr.value < len(send_type_choices):
                                    message_info['send_type'] = send_type_choices[send_type_attr.value]
                            # If it's a key into choices dict
                            elif isinstance(send_type_choices, dict) and send_type_attr.value in send_type_choices:
                                message_info['send_type'] = send_type_choices[send_type_attr.value]
                            else:
                                message_info['send_type'] = str(send_type_attr)
                
                # We need to handle the case where send_type is already set but might be a numeric value
                # This comprehensive conversion will handle all numeric send_type values
                if message_info['send_type'] is not None and send_type_choices:
                    # Convert any numeric send_type value to its string representation
                    send_type_value = None
                    
                    # Handle send_type if it's a string containing a number (e.g., "0", "1", "2")
                    if isinstance(message_info['send_type'], str) and message_info['send_type'].isdigit():
                        send_type_value = int(message_info['send_type'])
                    # Handle send_type if it's already an integer (e.g., 0, 1, 2)
                    elif isinstance(message_info['send_type'], int):
                        send_type_value = message_info['send_type']
                    # Also try to convert non-digit strings that might represent numbers (e.g. "0x2")
                    elif isinstance(message_info['send_type'], str):
                        try:
                            # Try to interpret as an integer in any base
                            send_type_value = int(message_info['send_type'], 0)
                        except ValueError:
                            # Not a valid number, keep as is
                            pass
                        
                    # If we have a numeric value, convert it using the choices
                    if send_type_value is not None:
                        if isinstance(send_type_choices, list) and 0 <= send_type_value < len(send_type_choices):
                            message_info['send_type'] = send_type_choices[send_type_value]
                        elif isinstance(send_type_choices, dict) and send_type_value in send_type_choices:
                            message_info['send_type'] = send_type_choices[send_type_value]
                # Apply default send_type if no send_type is defined for this message
                elif message_info['send_type'] is None and default_send_type is not None:
                    message_info['send_type'] = default_send_type
                    
                messages.append(message_info)
        except Exception as e:
            print(f"Error parsing message: {str(e)}")
            # Return empty list on error
            return []
            
        return messages

    def parse_all_signals(self) -> List[Dict[str, Any]]:
        """
        Parse all signals from all messages in the DBC database
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing signal information
                Each dictionary contains all signal information plus:
                - message_name (str): Name of the parent message
                - message_id (int): Frame ID of the parent message
                - multiplexer_id (Optional[int]): Multiplexer ID if signal is multiplexed
                - multiplexer_signal (Optional[str]): Name of the multiplexer signal
                - multiplexer_values (Optional[Dict[int, str]]): Mapping of multiplexer values to signal names
                - is_multiplexer (bool): Whether the signal is a multiplexer
                - choices (Optional[Dict[int, str]]): Mapping of raw values to choice names
                - is_float (bool): Whether the signal represents a floating-point value
                - decimal (Optional[int]): Number of decimal places for display
                - spn (Optional[int]): Suspect Parameter Number (J1939)
                - pgn (Optional[int]): Parameter Group Number (J1939)
                - sa (Optional[int]): Source Address (J1939)
                - da (Optional[int]): Destination Address (J1939)
                - priority (Optional[int]): Priority of the signal (J1939)
                - address (Optional[int]): Address of the signal (J1939)
                - is_j1939 (bool): Whether the signal is a J1939 signal
        """
        if not self.is_valid():
            return []
            
        all_signals = []
        try:
            for msg in self.database.messages:
                if not hasattr(msg, 'name'):
                    continue
                    
                for signal in getattr(msg, 'signals', []):
                    if not hasattr(signal, 'name'):
                        continue
                        
                    # Get multiplexer ID from multiplexer_ids if available
                    multiplexer_id = signal.multiplexer_ids[0] if hasattr(signal, 'multiplexer_ids') and signal.multiplexer_ids else None
                    
                    signal_info = {
                        "name": signal.name,
                        "message_name": msg.name,
                        "message_id": getattr(msg, 'frame_id', 0),
                        "start": getattr(signal, 'start', 0),
                        "length": getattr(signal, 'length', 1),
                        "byte_order": "little_endian" if getattr(signal, 'byte_order', 'little_endian') == 'little_endian' else "big_endian",
                        "is_signed": getattr(signal, 'is_signed', False),
                        "scale": float(getattr(signal, 'scale', 1.0)),
                        "offset": float(getattr(signal, 'offset', 0.0)),
                        "minimum": float(getattr(signal, 'minimum', 0)) if hasattr(signal, 'minimum') else None,
                        "maximum": float(getattr(signal, 'maximum', 0)) if hasattr(signal, 'maximum') else None,
                        "unit": getattr(signal, 'unit', None),
                        "comment": getattr(signal, 'comment', None),
                        "receivers": [
                            node.name if hasattr(node, 'name') else str(node)
                            for node in getattr(signal, 'receivers', [])
                        ],
                        # Additional signal fields
                        "multiplexer_id": multiplexer_id,
                        "multiplexer_signal": getattr(signal, 'multiplexer_signal', None),
                        "multiplexer_values": getattr(signal, 'multiplexer_values', None),
                        "is_multiplexer": getattr(signal, 'is_multiplexer', False),
                        "choices": getattr(signal, 'choices', None),
                        "is_float": getattr(signal, 'is_float', False),
                        "decimal": getattr(signal, 'decimal', None),
                        "spn": getattr(signal, 'spn', None),
                        "pgn": getattr(signal, 'pgn', None),
                        "sa": getattr(signal, 'sa', None),
                        "da": getattr(signal, 'da', None),
                        "priority": getattr(signal, 'priority', None),
                        "address": getattr(signal, 'address', None),
                        "is_j1939": getattr(signal, 'is_j1939', False)
                    }
                    all_signals.append(signal_info)
        except Exception as e:
            # Keep this error logging as it's important for troubleshooting
            print(f"Error parsing signals: {str(e)}")
            return []
            
        return all_signals

    def get_nodes(self) -> List[Dict[str, Any]]:
        """
        Returns the current list of nodes
        
        Returns:
            List[Dict[str, Any]]: List of node information dictionaries
        """
        return self.nodes

    def get_messages(self) -> List[Dict[str, Any]]:
        """
        Returns the current list of messages
        
        Returns:
            List[Dict[str, Any]]: List of message information dictionaries
        """
        return self.messages

    def get_signals(self) -> List[Dict[str, Any]]:
        """
        Returns the current list of all signals
        
        Returns:
            List[Dict[str, Any]]: List of signal information dictionaries
        """
        return self.signals
        
    def unload(self) -> bool:
        """
        Unload the DBC file from memory using the model
        
        Returns:
            bool: True if successfully unloaded, False otherwise
        """
        if self.model.remove_dbc(self.file_path):
            self.database = None
            self.is_loaded = False
            self.nodes = []  # Clear nodes list
            self.messages = []  # Clear messages list
            self.signals = []  # Clear signals list
            self.nodes_changed.emit(self.nodes)
            self.messages_changed.emit(self.messages)
            self.signals_changed.emit(self.signals)
            return True
        return False
        
    def cleanup(self):
        """
        Clean up handler resources and disconnect signals
        """
        # Disconnect from model signals
        try:
            self.model.dbc_error.disconnect(self._on_model_error)
        except:
            pass  # Signal might already be disconnected
        
        # Clear references
        self.database = None
        self.model = None
        self.is_loaded = False
        self.last_error = None
        self.nodes = []
        self.messages = []
        self.signals = []
        
    def is_valid(self) -> bool:
        """
        Check if the handler is valid and has a loaded database
        
        Returns:
            bool: True if the handler is valid and has a loaded database
        """
        return self.is_loaded and self.get_database() is not None
        
    def get_file_path(self) -> str:
        """
        Returns the file path of this handler
        """
        return self.file_path 

    def get_node_messages(self, node_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get Tx and Rx messages for a specific node
        
        Args:
            node_name (str): Name of the node to get messages for
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing:
                - tx_messages: List of messages where node is sender
                - rx_messages: List of messages where node receives signals
                Each message contains all fields from parse_messages method
        """
        tx_messages = []
        rx_messages = []
        
        for msg in self.messages:
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
                
        return {
            "tx_messages": tx_messages,
            "rx_messages": rx_messages
        } 

    def get_node_signals(self, node_name: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get Tx and Rx signals for a specific node
        
        Args:
            node_name (str): Name of the node to get signals for
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Dictionary containing:
                - tx_signals: List of signals from messages where node is sender
                - rx_signals: List of signals where node is a receiver
                Each signal contains all fields from parse_all_signals method
        """
        tx_signals = []
        rx_signals = []
        
        # Get node's messages first
        node_messages = self.get_node_messages(node_name)
        
        # Get Tx signals from Tx messages
        for msg in node_messages['tx_messages']:
            for signal in msg['signals']:
                signal_info = signal.copy()  # Create a copy to avoid modifying original
                signal_info['message_name'] = msg['name']
                signal_info['message_id'] = msg['frame_id']
                tx_signals.append(signal_info)
        
        # Get Rx signals from Rx messages
        for msg in node_messages['rx_messages']:
            for signal in msg['signals']:
                if node_name in signal['receivers']:
                    signal_info = signal.copy()  # Create a copy to avoid modifying original
                    signal_info['message_name'] = msg['name']
                    signal_info['message_id'] = msg['frame_id']
                    rx_signals.append(signal_info)
        
        return {
            "tx_signals": tx_signals,
            "rx_signals": rx_signals
        } 

    def get_changes_summary(self) -> str:
        """Get summary of changes made to this DBC file"""
        return self.change_tracker.get_changes_summary()
        
    def has_changes(self) -> bool:
        """Check if there are any tracked changes"""
        return self.change_tracker.has_changes()
        
    def clear_changes(self):
        """Clear tracked changes"""
        self.change_tracker.clear_changes()

    def add_node(self, node_data: dict):
        """
        Add a new node using the edit controller and update nodes list.
        Args:
            node_data (dict): Node data from dialog
        Returns:
            tuple[bool, str]: (success, error_message)
        """
        if not self.edit_controller:
            return False, "Edit controller not initialized"
        success, error = self.edit_controller.add_node(node_data)
        if success:
            self.nodes = self.parse_nodes()
            self.nodes_changed.emit(self.nodes)
        return success, error 