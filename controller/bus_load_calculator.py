from typing import Dict, List, Any, Optional, Tuple

class BusLoadCalculator:
    """
    Calculates CAN bus load based on message properties from a DBC file.
    """
    
    def __init__(self, bit_rate: int = 500000):
        """
        Initialize the bus load calculator with a default bit rate.
        
        Args:
            bit_rate (int): CAN bus bit rate in bits per second (default: 500 kbps)
        """
        self.bit_rate = bit_rate
        
    def set_bit_rate(self, bit_rate: int) -> None:
        """
        Set the CAN bus bit rate.
        
        Args:
            bit_rate (int): CAN bus bit rate in bits per second
        """
        self.bit_rate = bit_rate
        
    def calculate_message_bits(self, message: Dict[str, Any]) -> int:
        """
        Calculate the total number of bits for a CAN message.
        
        Args:
            message (Dict[str, Any]): Message dictionary from DBC_IO_Handler
            
        Returns:
            int: Total number of bits for the message
        """
        # Get message properties
        length = message.get('length', 0)
        is_extended = message.get('is_extended_frame', False)
        is_fd = message.get('is_fd', False)
        
        # Calculate overhead bits
        if is_fd:
            # CAN FD overhead
            overhead = 67  # SOF, ID, RTR, IDE, r0, EDL, BRS, ESI, DLC, CRC, ACK, EOF, IFS
        else:
            # Standard CAN overhead
            overhead = 47  # SOF, ID, RTR, IDE, r0, DLC, CRC, ACK, EOF, IFS
            
        # Calculate data bits
        if is_fd:
            # CAN FD has different bit rates for standard and data phases
            # For simplicity, we'll use the standard phase rate for all bits
            data_bits = length * 8
        else:
            # Standard CAN: 8 bits per byte
            data_bits = length * 8
            
        # Add ID field bits (11 for standard, 29 for extended)
        id_bits = 29 if is_extended else 11
        
        # Total bits = overhead + id_bits + data_bits
        total_bits = overhead + id_bits + data_bits
        
        return total_bits
        
    def calculate_message_transmission_time(self, message: Dict[str, Any]) -> float:
        """
        Calculate the transmission time for a message in milliseconds.
        
        Args:
            message (Dict[str, Any]): Message dictionary from DBC_IO_Handler
            
        Returns:
            float: Transmission time in milliseconds
        """
        total_bits = self.calculate_message_bits(message)
        transmission_time_ms = (total_bits / self.bit_rate) * 1000
        return transmission_time_ms
        
    def calculate_message_load(self, message: Dict[str, Any]) -> float:
        """
        Calculate the bus load contribution of a single message.
        
        Args:
            message (Dict[str, Any]): Message dictionary from DBC_IO_Handler
            
        Returns:
            float: Bus load contribution as a percentage
        """
        # Get cycle time in milliseconds
        cycle_time_ms = message.get('cycle_time')
        
        # If cycle time is not available, return 0
        if cycle_time_ms is None or cycle_time_ms <= 0:
            return 0.0
            
        # Calculate transmission time in milliseconds
        transmission_time_ms = self.calculate_message_transmission_time(message)
        
        # Calculate load as percentage
        load_percentage = (transmission_time_ms / cycle_time_ms) * 100
        
        return load_percentage
        
    def calculate_total_bus_load(self, messages: List[Dict[str, Any]]) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate the total bus load and individual message contributions.
        
        Args:
            messages (List[Dict[str, Any]]): List of message dictionaries from DBC_IO_Handler
            
        Returns:
            Tuple[float, List[Dict[str, Any]]]: 
                - Total bus load as a percentage
                - List of message load details
        """
        total_load = 0.0
        message_loads = []
        
        for message in messages:
            # Calculate load for this message
            load = self.calculate_message_load(message)
            
            # Add to total load
            total_load += load
            
            # Add message details to the list
            message_loads.append({
                'name': message.get('name', 'Unknown'),
                'id': message.get('frame_id', 0),
                'length': message.get('length', 0),
                'cycle_time': message.get('cycle_time', 0),
                'is_extended': message.get('is_extended_frame', False),
                'is_fd': message.get('is_fd', False),
                'transmission_time_ms': self.calculate_message_transmission_time(message),
                'load_percentage': load
            })
            
        # Add protocol overhead (typically 10-20%)
        overhead_factor = 1.15  # 15% overhead
        total_load_with_overhead = total_load * overhead_factor
        
        return total_load_with_overhead, message_loads 