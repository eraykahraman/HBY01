# DBC Master

A desktop application for viewing, editing, and managing CAN Database (DBC) files with database integration and vehicle management capabilities.

## Features

### Core Functionality
- **DBC File Management**
  - Import and view DBC files (nodes, messages, signals)
  - Store DBC files in a database for future access
  - Export DBC files to local storage
  - In-memory editing of DBC content

### User Management
- **Role-Based Access Control**
  - Different permissions for various user roles:
    - Basic User: View DBC files
    - Netcom Engineer: Full access including vehicle management and DBC file assignment
  - Login/logout functionality with secure authentication

### Vehicle Management
- **Vehicle Operations**
  - Create, view, edit, and delete vehicles
  - Associate DBC files with specific vehicles
  - View DBC files associated with each vehicle
  - Bus load calculation for vehicle communication networks

### User Interface
- **Advanced UI Components**
  - Integrated list views for DBC files and vehicles in the left panel with mode switching
  - Tree view for exploring DBC file content (nodes, messages, signals) in the right panel
  - Tabbed interface separating DBC viewing from vehicle management
  - Context menus for quick actions
  - Detailed DBC content viewing with signal/message selection

## Architecture

DBC Master follows the Model-View-Controller (MVC) design pattern:

### Model
- **Database Models**: ORM classes for database interaction (`model/dbc_orm.py`)
- **Data Structures**: Classes representing DBC elements (nodes, messages, signals)

### View
- **Main Windows**: Primary application interfaces (`view/main_window.py`)
- **Specialized Views**: 
  - DBC List View (`view/dbc_listview.py`)
  - DBC Display View (`view/dbc_display_view.py`)
  - Vehicle View (`view/vehicle_view.py`)
- **Dialogs**: Configuration and data entry forms

### Controller
- **DBC I/O Controller**: Manages DBC file operations (`controller/DBC_IO_Controller.py`)
- **Service Layers**: Business logic implementation
  - Database Service
  - Vehicle Service
  - Authentication Service

## Key Components

### DBC List View (`view/dbc_listview.py`)
The DBC List View is a critical component that provides the user interface for managing DBC files and vehicles in the application.

#### Functionality
- Controls the entire left panel of the application
- Manages both DBC files and vehicle listings in a single component
- Toggles between DBC files mode and vehicles mode
- Handles user selection of DBC files and vehicles
- Manages the authentication UI elements (login/logout)
- Provides context menus for additional actions
- Controls the visibility of UI elements based on user permissions

#### Implementation Details
- Extends `QWidget` with a custom layout containing multiple sub-components
- Embeds the `VehicleView` component for displaying vehicles
- Contains a `QListWidget` for displaying DBC files
- Implements dynamic UI updates based on authentication state
- Emits signals to notify other components about user interactions:
  - `handler_selected`: When a user selects a DBC file
  - `handler_removed`: When a user removes a DBC file
  - `handler_open_in_new_window`: When a user chooses to open a file in a new window
  - `login_clicked`: When the login button is clicked
  - `logout_clicked`: When the logout button is clicked
  - `import_clicked`: When the import button is clicked
  - `vehicle_selected`: When a vehicle is selected

#### Integration
- Integrated with `MainWindow` to provide the primary interface for the left panel
- Communicates with `DBC_IO_Controller` for file operations
- Feeds selected handlers to `DBCDisplayView` for detailed viewing
- Updates UI components based on authentication status

### DBC Display View (`view/dbc_display_view.py`)
This component displays the detailed content of DBC files in the right panel.

#### Functionality
- Shows detailed information about the selected DBC file
- Displays a hierarchical view of nodes, messages, and signals using a tree widget
- Provides detailed tables for signals, messages, and nodes
- Includes a bus load calculator for analyzing CAN bus traffic

#### Implementation Details
- Uses a `QTreeWidget` to display the hierarchical structure of DBC content
- Implements detailed tables for viewing different aspects of the DBC file
- Provides contextual information based on user selection in the tree

## Signal Communication

The application uses PyQt signal-slot mechanism for communication between components:

### Core Signals
- `DBC_IO_Controller`:
  - `handlers_changed`: Emitted when DBC handlers list is updated
  - `handler_removed`: Emitted when a DBC handler is removed
  - `handler_created`: Emitted when a new DBC handler is created
  - `db_error`: Emitted when a database error occurs

- `DBCListView`:
  - `handler_selected`: Emitted when a DBC file is selected in the list
  - `handler_removed`: Emitted when a DBC file is removed from the list
  - `handler_open_in_new_window`: Emitted to open a DBC file in a new window
  - `login_clicked`: Emitted when the login button is clicked
  - `logout_clicked`: Emitted when the logout button is clicked
  - `import_clicked`: Emitted when the import button is clicked
  - `vehicle_selected`: Emitted when a vehicle is selected

- `VehicleView`:
  - `vehicle_selected`: Emitted when a vehicle is selected in the list

### Signal Flow Examples
1. **DBC File Selection**: 
   - User clicks on a DBC file in the list view
   - `DBCListView.on_dbc_selection_changed()` is triggered
   - `DBCListView.handler_selected` signal is emitted
   - `MainWindow` receives the signal and calls `on_handler_selected()`
   - The DBC display view updates to show the DBC file content

2. **User Authentication**:
   - User clicks the login button
   - `DBCListView.on_login_clicked()` is triggered
   - `DBCListView.login_clicked` signal is emitted
   - `MainWindow` receives the signal and shows the login dialog
   - Upon successful login, `MainWindow.handle_login_success()` is called
   - `DBCListView.update_ui_for_authentication()` updates the UI based on user permissions

3. **Mode Switching**:
   - User clicks the "Vehicles" button in the left panel
   - `DBCListView.show_vehicles()` is triggered
   - The left panel switches from DBC files to vehicle listing
   - When a vehicle is selected, `DBCListView.vehicle_selected` signal is emitted
   - `MainWindow` receives the signal and displays the vehicle information

## Critical Methods

### DBC File Handling
- `DBC_IO_Controller.import_dbc()`: Imports a DBC file via file dialog
- `DBC_IO_Controller.import_dbc_from_path()`: Imports a DBC file directly from path
- `DBC_IO_Controller.get_vehicle_dbc_files()`: Retrieves DBC files associated with a vehicle
- `DBC_IO_Handler.load_dbc()`: Parses and loads DBC file content

### UI Management
- `MainWindow.on_handler_selected()`: Handles DBC file selection and updates the display
- `MainWindow.handle_login_success()`: Updates UI when a user logs in
- `DBCDisplayView.update_display()`: Updates the tree view with DBC file content
- `DBCListView.update_handlers()`: Updates the list of displayed DBC files
- `DBCListView.update_ui_for_authentication()`: Updates UI based on authentication state
- `DBCListView.show_vehicles()`: Switches the left panel to show vehicles
- `DBCListView.show_dbc_files()`: Switches the left panel to show DBC files

### Vehicle Management
- `VehicleService.create_vehicle()`: Creates a new vehicle in the database
- `VehicleService.assign_dbc_to_vehicle()`: Associates a DBC file with a vehicle
- `VehicleService.get_vehicle_dbc_files()`: Retrieves DBC files for a vehicle

### Authentication
- `AuthService.login()`: Authenticates a user
- `AuthService.has_permission()`: Checks if the current user has a specific permission

## Installation

1. Clone the repository
2. Install the required dependencies:
   ```
   python -m pip install -r requirements.txt
   ```
3. Run the application:
   ```
   python main.py
   ```

### Troubleshooting

If you encounter the error `ModuleNotFoundError: No module named 'PyQt5'`, install PyQt5 manually:
```
python -m pip install PyQt5
```

## Dependencies

The application relies on the following main libraries:
- PyQt5 for the UI components
- SQLAlchemy for database operations
- cantools for DBC file parsing 