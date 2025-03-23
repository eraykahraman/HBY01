# DBC File Management Application

A PyQt5-based application for managing and viewing DBC (Database CAN) files. This application allows users to load, view, and manage DBC files with a user-friendly interface.

## Features

- Load and manage multiple DBC files
- View DBC content in a hierarchical tree structure
- Display messages and signals from DBC files
- User-friendly interface with status feedback
- Error handling and validation

## Project Structure

```
├── controller/
│   └── DBC_IO_Controller.py    # Handles DBC file operations and signals
├── model/
│   └── dbc_model.py           # Manages DBC data
├── view/
│   ├── main_window.py         # Main application window
│   ├── dbc_listview.py        # List view for DBC files
│   └── dbc_display_view.py    # Tree view for DBC content
└── main.py                    # Application entry point
```

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

### Signal Flow

1. **DBC Loading Flow**:
   ```
   User clicks Import → Controller.import_dbc()
   ↓
   If successful: Controller.dbc_loaded.emit()
   ↓
   MainWindow.on_dbc_loaded() → Updates UI
   ↓
   If failed: Controller.dbc_error.emit()
   ↓
   MainWindow.on_dbc_error() → Shows error dialog
   ```

2. **DBC Selection Flow**:
   ```
   User selects DBC in list → DBCListView.dbc_selected.emit()
   ↓
   MainWindow.on_dbc_selected() → Updates display view
   ```

3. **DBC Removal Flow**:
   ```
   User clicks remove → DBCListView.dbc_removed.emit()
   ↓
   MainWindow.on_dbc_removed() → Updates UI
   ↓
   Controller.remove_dbc() → Controller.dbc_removed.emit()
   ↓
   MainWindow.on_dbc_removed() → Updates UI again
   ```

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

## Dependencies

- PyQt5
- cantools
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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
3. Select a DBC file from the list to view its contents
4. Use the remove button (×) to remove DBC files

## Architecture

The application follows the Model-View-Controller (MVC) pattern:

- **Model**: Handles data management and storage
- **View**: Manages UI components and user interaction
- **Controller**: Coordinates between Model and View, handles signals

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License


## Contact

