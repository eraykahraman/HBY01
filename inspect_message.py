import cantools
from cantools.database.can.message import Message
import inspect
import sys

def inspect_message_class():
    """Inspect the Message class properties from cantools"""
    print("Starting Message class inspection...")
    
    # Create a simple message to inspect
    print("Creating test message...")
    message = Message(
        frame_id=0x123,
        name="TestMessage",
        length=8,
        senders=["Node1"],
        signals=[]
    )
    
    # Print message attributes
    print("\n=== Message Class Attributes ===")
    
    # Standard properties
    properties = []
    for name in dir(Message):
        if not name.startswith('_') and not callable(getattr(Message, name)):
            properties.append(name)
    print(f"Properties: {', '.join(properties)}")
    
    # Methods
    methods = []
    for name in dir(Message):
        if not name.startswith('_') and callable(getattr(Message, name)):
            methods.append(name)
    print(f"Methods: {', '.join(methods)}")
    
    # Instance attributes
    print("\n=== Message Instance Attributes ===")
    attributes = []
    for attr in dir(message):
        if not attr.startswith('_') and not callable(getattr(message, attr)):
            attributes.append(attr)
    print(f"Attributes: {', '.join(attributes)}")
    
    # Instance methods
    instance_methods = []
    for name in dir(message):
        if not name.startswith('_') and callable(getattr(message, name)):
            instance_methods.append(name)
    print(f"Instance Methods: {', '.join(instance_methods)}")
    
    # Specific attributes we're interested in
    print("\n=== Special Attributes ===")
    print(f"Has 'send_type' attribute: {'send_type' in dir(message)}")
    
    # Try to set and get send_type
    print("\n=== Testing send_type ===")
    try:
        # Try to get current send_type
        print(f"Current send_type: {getattr(message, 'send_type', None)}")
        
        # Try to set send_type directly
        try:
            print("Trying to set send_type directly...")
            message.send_type = "PERIODIC"
            print("Setting message.send_type directly: Success")
        except Exception as e:
            print(f"Setting message.send_type directly: Failed - {str(e)}")
        
        # Try to set via setattr
        try:
            print("Trying to set send_type via setattr...")
            setattr(message, 'send_type', "PERIODIC")
            print("Setting via setattr: Success")
        except Exception as e:
            print(f"Setting via setattr: Failed - {str(e)}")
            
        # Check if send_type was set
        print(f"New send_type: {getattr(message, 'send_type', None)}")
    except Exception as e:
        print(f"Error testing send_type: {str(e)}")
    
    # Possible ways to handle send_type
    print("\n=== Possible send_type values ===")
    print("Common send_type values in DBC files:")
    print("- CYCLIC: Message is sent cyclically at regular intervals")
    print("- SPONTANEOUS: Message is sent when needed")
    print("- TRIGGERED: Message is sent when triggered by specific events")
    print("- CYCLIC_IF_ACTIVE: Message is sent cyclically when active")
    print("- NONE: No send type specified")
    
    # Message creation with send_type
    print("\n=== Creating Message with send_type ===")
    try:
        print("Creating message with send_type parameter...")
        message_with_send_type = Message(
            frame_id=0x234,
            name="MessageWithSendType",
            length=8,
            senders=["Node1"],
            signals=[],
            send_type="CYCLIC"
        )
        print(f"Created message with send_type: {getattr(message_with_send_type, 'send_type', None)}")
        
        # Try to modify it after creation
        try:
            print("Trying to modify send_type after creation...")
            message_with_send_type.send_type = "SPONTANEOUS"
            print(f"Modified send_type: {message_with_send_type.send_type}")
        except Exception as e:
            print(f"Failed to modify send_type: {str(e)}")
    except Exception as e:
        print(f"Failed to create message with send_type: {str(e)}")

def inspect_message_send_type():
    """Inspect and test the send_type attribute of Message class"""
    print("=== Testing Message send_type attribute ===")
    
    # 1. Create a message with send_type 
    print("\n1. Creating message with send_type in constructor:")
    try:
        message = Message(
            frame_id=0x123,
            name="TestMessage",
            length=8,
            senders=["Node1"],
            signals=[],
            send_type="CYCLIC"
        )
        print(f"  - Created successfully")
        print(f"  - send_type value: {message.send_type}")
        
        # Try to update the send_type
        print("\n2. Attempting to update send_type directly:")
        try:
            original_send_type = message.send_type
            message.send_type = "SPONTANEOUS"
            print(f"  - Direct assignment successful: {message.send_type}")
        except Exception as e:
            print(f"  - Direct assignment failed: {str(e)}")
            
            # Try with setattr
            print("\n3. Attempting to update send_type using setattr:")
            try:
                setattr(message, 'send_type', "SPONTANEOUS")
                print(f"  - setattr successful: {message.send_type}")
            except Exception as e:
                print(f"  - setattr failed: {str(e)}")
                
                # Try with _send_type attribute if it exists
                print("\n4. Checking for _send_type internal attribute:")
                has_private_attr = hasattr(message, '_send_type')
                print(f"  - Has _send_type attribute: {has_private_attr}")
                
                if has_private_attr:
                    try:
                        message._send_type = "SPONTANEOUS"
                        print(f"  - Updated _send_type: {message._send_type}")
                        print(f"  - Public send_type now: {message.send_type}")
                    except Exception as e:
                        print(f"  - Failed to update _send_type: {str(e)}")
                
                # Look at how the property is defined
                print("\n5. Examining property definition:")
                
                try:
                    send_type_property = Message.__class__.__dict__.get('send_type')
                    if send_type_property and isinstance(send_type_property, property):
                        print(f"  - send_type is defined as a property with:")
                        print(f"    - getter: {send_type_property.fget}")
                        print(f"    - setter: {send_type_property.fset}")
                    else:
                        print(f"  - send_type is not a standard property")
                except Exception as e:
                    print(f"  - Error examining property: {str(e)}")
    except Exception as e:
        print(f"Error creating message: {str(e)}")
    
    # 6. Create and update a completely new Message object
    print("\n6. Creating a new message object:")
    try:
        # Inspect Message constructor
        message_init_params = inspect.signature(Message.__init__).parameters
        print(f"  - Message constructor accepts send_type: {'send_type' in message_init_params}")
        
        # Create a new message without send_type
        message = Message(
            frame_id=0x234,
            name="AnotherMessage",
            length=8,
            senders=["Node1"],
            signals=[]
        )
        print(f"  - Created message without send_type")
        print(f"  - Default send_type: {message.send_type}")
        
        # Create message dictionary
        message_dict = {
            "name": "Message2",
            "frame_id": 0x345,
            "length": 8,
            "senders": ["Node1"],
            "signals": [],
            "send_type": "CYCLIC" 
        }
        
        # Try creating a new message from dictionary
        print("\n7. Creating message from dictionary with send_type:")
        try:
            new_msg = Message(**message_dict)
            print(f"  - Created successfully")
            print(f"  - send_type: {new_msg.send_type}")
        except Exception as e:
            print(f"  - Failed: {str(e)}")
    except Exception as e:
        print(f"Error in testing: {str(e)}")
        
    # 8. Check the source code for clues
    print("\n8. Possible solution approaches:")
    print("  a. Since send_type is read-only, you must create a new Message object with the desired send_type")
    print("  b. Extract all attributes from the original message")
    print("  c. Create a new message with the same attributes but updated send_type")
    print("  d. Replace the old message in the database with the new one")

if __name__ == "__main__":
    print("Script started")
    inspect_message_class()
    inspect_message_send_type()
    print("Script completed") 