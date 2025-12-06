# DBC Master - CAN Database Management Tool

DBC Master is a comprehensive tool for managing and analyzing CAN database (DBC) files. It provides a user-friendly interface for viewing, editing, and analyzing CAN network configurations.

## Quick Start - Building the Executable

### Prerequisites

1. **Python 3.8+** installed on your system
2. **Git** (optional, for cloning the repository)

### Installation & Build Steps

#### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd HBY01
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv myvenv
myvenv\Scripts\activate

# Linux/MacOS
python3 -m venv myvenv
source myvenv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Build the Executable

**Option A: Using cx_Freeze (Recommended)**
```bash
python setup.py build
```

**Option B: Using PyInstaller**
```bash
pyinstaller --onefile --windowed main.py --name DBC_Master
```

#### 5. Locate the Executable

**cx_Freeze Output:**
- Location: `build/exe.win-amd64-3.x/DBC_Master.exe`
- Contains: Executable + all dependencies in a folder

**PyInstaller Output:**
- Location: `dist/DBC_Master.exe`
- Contains: Single executable file

### Running the Application

#### Development Mode
```bash
python main.py
```

#### Production Mode
```bash
# Navigate to build directory
cd build/exe.win-amd64-3.x/
./DBC_Master.exe
```

## Build Configuration Details

### cx_Freeze Configuration (`setup.py`)

The build process is configured in `setup.py` with the following settings:

**Included Packages:**
- `PyQt5` - GUI framework
- `sqlalchemy` - Database ORM
- `cantools` - CAN bus tools
- `psycopg2` - PostgreSQL adapter
- `pydantic` - Data validation
- `deepdiff` - Object comparison
- `orjson` - Fast JSON processing
- `textparser` - Text parsing utilities
- `bitstruct` - Binary data handling
- `can` - CAN bus library

**Excluded Packages:**
- `matplotlib`, `numpy`, `pandas` - Large data science libraries
- `tkinter` - Alternative GUI (not needed)
- `test`, `distutils` - Development tools
- `PyQt5.QtQml`, `PyQt5.QtQuick` - Unused Qt modules

**Build Options:**
- **Base**: `Win32GUI` (Windows) - Creates GUI application without console window
- **Target**: `DBC_Master.exe`
- **Entry Point**: `main.py`
- **Optimization**: Level 0 (no optimization for better debugging)

### PyInstaller Alternative

If you prefer a single-file executable:

```bash
pyinstaller --onefile --windowed --name DBC_Master main.py
```

**Options:**
- `--onefile`: Creates a single executable file
- `--windowed`: Hides console window (Windows)
- `--name`: Sets the output filename

## Troubleshooting

### Common Build Issues

#### 1. Missing Dependencies
```bash
# If build fails due to missing packages
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

#### 2. PyQt5 Issues
```bash
# Reinstall PyQt5 if GUI doesn't work
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip
pip install PyQt5==5.15.9
```

#### 3. cx_Freeze Build Errors
```bash
# Clean build directory and retry
rm -rf build/
python setup.py build
```

#### 4. PyInstaller Build Errors
```bash
# Clean PyInstaller cache
rm -rf build/ dist/ __pycache__/
pyinstaller --clean main.py
```

### Runtime Issues

#### 1. "Missing DLL" Errors
- Ensure all dependencies are properly included in the build
- Check if system DLLs are missing (Visual C++ Redistributable on Windows)

#### 2. Database Connection Issues
- Verify PostgreSQL is installed and running (if using database features)
- Check connection strings in configuration

#### 3. GUI Not Displaying
- Ensure PyQt5 is properly installed
- Check for conflicting Qt installations

## Development Setup

### Project Structure
```
HBY01/
├── main.py                 # Application entry point
├── setup.py               # Build configuration
├── requirements.txt       # Python dependencies
├── controller/           # Business logic controllers
├── model/               # Data models
├── view/                # GUI components
└── database/            # Database configuration
```

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-qt

# Run tests
pytest
```

### Code Quality
```bash
# Install linting tools
pip install pylint black

# Run linting
pylint controller/ model/ view/
black .
```

## Deployment

### Windows Deployment
1. Build the executable using cx_Freeze or PyInstaller
2. Test the executable on a clean Windows machine
3. Create an installer using tools like Inno Setup or NSIS
4. Include any required system dependencies (Visual C++ Redistributable)

### Linux Deployment
1. Build using cx_Freeze
2. Package as AppImage or create a .deb/.rpm package
3. Include system dependencies in package metadata

### macOS Deployment
1. Build using cx_Freeze
2. Create a .dmg file
3. Sign the application for distribution

## Core Features

### 1. DBC File Management
- Import and load multiple DBC files
- Export DBC files with change tracking
- View and manage multiple DBC files simultaneously
- Open DBC files in separate windows for detailed analysis

### 2. Network Analysis
- View network topology with gateway nodes
- Analyze message routing between different CAN networks
- Check message compatibility and routing paths
- Visualize network nodes and their connections

### 3. Message Management
- View detailed message information including:
  - Frame IDs
  - Message length
  - Senders and receivers
  - Cycle time
  - Send type
  - Frame format (Standard/Extended)
  - CAN FD support
- Edit message properties
- Track message changes

### 4. Signal Management
- View and edit signal properties:
  - Start bit
  - Length
  - Byte order
  - Signed/Unsigned
  - Scale and offset
  - Minimum/Maximum values
  - Units
  - Comments
- Support for multiplexed signals
- Signal value tables and choices

### 5. Node Management
- View and manage network nodes
- Node properties including:
  - Node name
  - Comments
  - Address information
  - J1939 specific properties
  - AUTOSAR specific properties
- Track node message transmission and reception

### 6. Advanced Features
- Bus load calculation
- Message comparison between different DBC files
- Change tracking and history
- Support for J1939 protocol
- Support for AUTOSAR
- Environment variable management
- Value table management

## Technical Details

### Supported Protocols
- Standard CAN
- CAN FD
- J1939
- AUTOSAR

### File Format Support
- DBC files
- Export to text format for change tracking

### Data Management
- In-memory database handling
- Change tracking and validation
- Automatic data structure updates
- Error handling and validation

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]

## Support

[Add support contact information here] 