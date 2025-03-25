# DBC File Management Application

A PyQt5-based application for managing and viewing DBC (Database CAN) files. This application allows users to load, view, and analyze DBC files with a comprehensive user interface.

## Features

### File Management
- Load and manage multiple DBC files simultaneously
- Open multiple DBC files in separate windows for side-by-side comparison
- View DBC content in a hierarchical tree structure

### Message Viewing
- Display all messages with their IDs, lengths, and signal counts
- Sort messages by any attribute (ID, name, length, etc.)
- Filter messages using text or dropdown filters
- Show signals as expandable rows under messages
- Double-click messages to view detailed information

### Signal Analysis
- View all signals across all messages in a dedicated signals table
- Display comprehensive signal attributes (bit position, length, scale, offset, etc.)
- Sort signals by any attribute
- Filter signals using customized filters for each attribute type
- Highlight signals with special properties (multiplexers, choices, etc.)

### Tree Navigation
- Hierarchical tree view shows messages and nodes
- Messages displayed with IDs for easy identification
- Expandable signal groups to browse signal details
- View ECU/node information from the DBC file

### Detail View
- Non-modal message detail popups allow viewing multiple messages simultaneously
- Tabbed interface for signal information and message properties
- Shows DBC file origin in detail views
- Highlights selected signals when opening from signal view
- Displays all signal attributes and choices/enumerations

### User Interface
- Resizable columns in all tables
- Clear indication of sort direction
- Interactive filter widgets for each column
- Enhanced visual feedback for selected items

## Project Structure

```
├── controller/
│   └── DBC_IO_Controller.py    # Handles DBC file operations and signals
├── model/
│   └── dbc_model.py            # Manages DBC data
├── view/
│   ├── main_window.py          # Main application window
│   ├── dbc_listview.py         # List view for DBC files
│   ├── dbc_display_view.py     # Tree and table views for DBC content
│   └── message_detail_view.py  # Detailed message and signal information
└── main.py                     # Application entry point
```

## Key Components and Methods

### DBCDisplayView
This is the main view component for displaying DBC file contents.

#### Key Methods:
- `display_dbc_content(instance_id)`: Loads and displays all DBC content in the tree view with hierarchical organization
- `populate_messages_table()`: Populates the message table with all messages from the loaded DBC
- `populate_signals_table()`: Creates and populates a comprehensive table of all signals
- `on_tree_item_clicked(item, column)`: Handles navigation in the tree view
- `show_message_details(message)`: Opens a non-modal dialog with detailed message information
- `show_signal_details(signal, message)`: Opens a message detail view with a specific signal highlighted
- `apply_filters()`: Filters the message table based on user-defined criteria
- `apply_signal_filters()`: Filters the signal table with attribute-specific filters
- `sort_table(column, order)`: Handles custom sorting of the message table
- `sort_signals_table(column, order)`: Provides specialized sorting for the signals table

### MessageDetailView
Provides detailed information about messages and signals.

#### Key Methods:
- `setup_ui()`: Creates the tabbed interface for message details
- `setup_properties_tab()`: Displays message properties like ID, length, etc.
- `setup_signals_tab()`: Shows a table of all signals with their attributes
- `highlight_selected_signal()`: Highlights and scrolls to a specific signal if selected

### DBC_IO_Controller
Handles file operations and communication between model and views.

#### Key Methods:
- `import_dbc(parent_window)`: Opens a file dialog and loads a DBC file
- `remove_dbc(file_path)`: Removes a DBC file from the application
- `get_dbc(file_path)`: Retrieves a loaded DBC file

## Signal Flow

### Message Detail Flow
```
User double-clicks message → on_table_cell_double_clicked()
↓
show_message_details(message) → Creates MessageDetailView
↓
MessageDetailView displays message properties and signals
```

### Signal Filtering Flow
```
User enters filter text → filter widget's event triggers apply_signal_filters()
↓
apply_signal_filters() collects and filters all table rows
↓
Update table with filtered rows
↓
Re-apply current sort if active
```

### Tree Navigation Flow
```
User clicks tree item → on_tree_item_clicked(item, column)
↓
Check item type (Messages, Signals, specific message, or signal)
↓
Populate appropriate table or show details
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv myvenv
   # On Windows:
   myvenv\Scripts\activate
   # On Linux/Mac:
   source myvenv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. Click "Import DBC" to load a DBC file
3. Use the tree view to browse messages, signals, and nodes
4. Click on "Messages" to view all messages in a sortable/filterable table
5. Click on "Signals" to view all signals across all messages
6. Double-click on any message to view its details
7. Use the expand buttons (▶) in the message table to view signals for a specific message
8. Adjust column widths by dragging the column dividers
9. Sort any table by clicking on the column headers

## Creating an Executable

To create a standalone executable:

1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Create the executable:
   ```bash
   pyinstaller --onefile --windowed --name "DBC Viewer" --hidden-import=numpy.core.multiarray --hidden-import=numpy.core.numeric --hidden-import=cantools main.py
   ```

3. Find the executable in the `dist` folder

## Architecture

The application follows the Model-View-Controller (MVC) pattern:

- **Model**: Manages the DBC data using the cantools library
- **View**: Creates and handles the user interface components
- **Controller**: Coordinates data flow between model and views

## Dependencies

- PyQt5: GUI framework
- cantools: DBC file parsing and interpretation
- numpy: Used by cantools for signal calculations
- Optional: PyInstaller for creating standalone executables

## Signal Documentation

### Controller Signals (DBC_IO_Controller)

| Signal Name | Parameters | Description | Receiver |
|-------------|------------|-------------|-----------|
| `dbc_loaded` | `(str, object)` | Emitted when a DBC file is successfully loaded. Parameters: file path and database object | MainWindow |
| `dbc_error` | `str` | Emitted when there's an error loading a DBC file. Parameter: error message | MainWindow |
| `dbc_removed` | `str` | Emitted when a DBC file is successfully removed. Parameter: file path | MainWindow |

### List View Signals (DBCListView)

| Signal Name | Parameters | Description | Receiver |
|-------------|------------|-------------|-----------|
| `dbc_selected` | `str` | Emitted when a DBC file is selected in the list. Parameter: file path | MainWindow |
| `dbc_removed` | `str` | Emitted when user requests DBC file removal. Parameter: file path | MainWindow |

## Key Methods

### MainWindow Methods

#### `on_dbc_selected(self, instance_id)`
- Handles DBC file selection from the list
- Updates status bar with selected file
- Creates or shows display view
- Updates display view with DBC content

#### `on_dbc_removed(self, file_path)`
- Handles DBC file removal
- Updates status bar with removal confirmation
- Removes item from list view
- Maintains UI consistency

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License


## Contact

