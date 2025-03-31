from typing import Optional, Dict, Any, List
from cantools.database import Database
import os
from model.dbc_model import DBCModel
from PyQt5.QtCore import QObject, pyqtSignal

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
        self.model = model
        self.database: Optional[Database] = None
        self.is_loaded: bool = False
        self.nodes: List[Dict[str, Any]] = []  # Store the list of nodes
        self.messages: List[Dict[str, Any]] = []  # Store the list of messages
        self.signals: List[Dict[str, Any]] = []  # Store the list of all signals
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
                # Parse nodes and messages after successful load
                self.nodes = self.parse_nodes()
                self.messages = self.parse_messages()
                self.signals = self.parse_all_signals()  # Parse all signals
                self.nodes_changed.emit(self.nodes)
                self.messages_changed.emit(self.messages)
                self.signals_changed.emit(self.signals)  # Emit signals list
                return True, None
            else:
                return False, self.last_error or "Failed to load DBC file"
            
        except Exception as e:
            return False, f"Error loading DBC file: {str(e)}"
            
    def get_database(self) -> Optional[Database]:
        """
        Returns the DBC database
        """
        return self.model.get_dbc(self.file_path)
        
    def get_file_info(self) -> Dict[str, Any]:
        """
        Get information about the DBC file
        
        Returns:
            Dict[str, Any]: Dictionary containing file information
        """
        db = self.get_database()
        return {
            "file_path": self.file_path,
            "file_name": os.path.basename(self.file_path),
            "is_loaded": self.is_loaded,
            "messages_count": len(db.messages) if db else 0,
            "nodes_count": len(db.nodes) if db else 0
        }
        
    def parse_nodes(self) -> List[Dict[str, Any]]:
        """
        Parse all nodes from the DBC database
        
        Returns:
            List[Dict[str, Any]]: List of dictionaries containing node information
                Each dictionary contains:
                - name (str): The name of the node
                - comment (Optional[str]): The comment associated with the node
        """
        if not self.is_valid():
            return []
            
        nodes = []
        try:
            for node in self.database.nodes:
                # Check if node is a string (node name) or a Node object
                if isinstance(node, str):
                    node_info = {
                        "name": node,
                        "comment": None
                    }
                else:
                    node_info = {
                        "name": node.name,
                        "comment": node.comment if hasattr(node, 'comment') else None
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
        """
        if not self.is_valid():
            return []
            
        messages = []
        try:
            for msg in self.database.messages:
                # Check if message has all required attributes
                if not hasattr(msg, 'name'):
                    continue
                    
                # Parse signals
                signals = []
                for signal in getattr(msg, 'signals', []):
                    if not hasattr(signal, 'name'):
                        continue
                        
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
                        "receivers": [
                            node.name if hasattr(node, 'name') else str(node)
                            for node in getattr(signal, 'receivers', [])
                        ]
                    }
                    signals.append(signal_info)
                    
                message_info = {
                    "name": msg.name,
                    "frame_id": getattr(msg, 'frame_id', 0),
                    "length": getattr(msg, 'length', 0),
                    "comment": getattr(msg, 'comment', None),
                    "senders": [
                        node.name if hasattr(node, 'name') else str(node)
                        for node in getattr(msg, 'senders', [])
                    ],
                    "signals": signals
                }
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
                        ]
                    }
                    all_signals.append(signal_info)
        except Exception as e:
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