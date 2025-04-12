from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox,
    QDialogButtonBox, QSpinBox, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, pyqtSignal

class VehicleDialog(QDialog):
    """Dialog for creating or editing a vehicle"""
    
    def __init__(self, parent=None, vehicle_data=None):
        super().__init__(parent)
        self.vehicle_data = vehicle_data  # None for new vehicle, dict for editing
        
        self.setWindowTitle("Vehicle" if vehicle_data else "New Vehicle")
        self.setMinimumWidth(400)
        self.setModal(True)
        
        self.initUI()
        
        # If editing a vehicle, load its data
        if self.vehicle_data:
            self.loadVehicleData()
    
    def initUI(self):
        """Initialize the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Create form layout for vehicle fields
        form_layout = QFormLayout()
        
        # Vehicle name field (required)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter vehicle name")
        form_layout.addRow("Name*:", self.name_input)
        
        # Make field
        self.make_input = QLineEdit()
        self.make_input.setPlaceholderText("Enter manufacturer")
        form_layout.addRow("Make:", self.make_input)
        
        # Model field
        self.model_input = QLineEdit()
        self.model_input.setPlaceholderText("Enter model")
        form_layout.addRow("Model:", self.model_input)
        
        # Year field
        self.year_input = QSpinBox()
        self.year_input.setRange(1900, 2100)
        self.year_input.setValue(2023)
        form_layout.addRow("Year:", self.year_input)
        
        # VIN field
        self.vin_input = QLineEdit()
        self.vin_input.setPlaceholderText("Enter VIN")
        self.vin_input.setMaxLength(17)
        form_layout.addRow("VIN:", self.vin_input)
        
        # Description field
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Enter description")
        form_layout.addRow("Description:", self.description_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal,
            self
        )
        buttons.accepted.connect(self.validateAndAccept)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
    
    def loadVehicleData(self):
        """Load existing vehicle data into the form"""
        self.name_input.setText(self.vehicle_data.get("name", ""))
        self.make_input.setText(self.vehicle_data.get("make", ""))
        self.model_input.setText(self.vehicle_data.get("model", ""))
        
        year = self.vehicle_data.get("year")
        if year:
            self.year_input.setValue(year)
            
        self.vin_input.setText(self.vehicle_data.get("vin", ""))
        self.description_input.setText(self.vehicle_data.get("description", ""))
    
    def validateAndAccept(self):
        """Validate inputs before accepting the dialog"""
        # Check required fields
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "Missing Information", "Vehicle name is required")
            return
        
        # Create a dictionary with the vehicle data
        self.vehicle_data = {
            "name": self.name_input.text().strip(),
            "make": self.make_input.text().strip(),
            "model": self.model_input.text().strip(),
            "year": self.year_input.value(),
            "vin": self.vin_input.text().strip(),
            "description": self.description_input.text().strip()
        }
        
        # If an existing vehicle, keep its ID
        if self.vehicle_data and "id" in self.vehicle_data:
            self.vehicle_data["id"] = self.vehicle_data["id"]
        
        self.accept()
    
    def getVehicleData(self):
        """Get the vehicle data from the dialog"""
        return self.vehicle_data

class DBC_Vehicle_AssignDialog(QDialog):
    """Dialog for assigning DBC files to a vehicle"""
    
    def __init__(self, dbc_controller, parent=None, vehicle_id=None):
        super().__init__(parent)
        self.dbc_controller = dbc_controller
        self.vehicle_id = vehicle_id
        self.parent = parent
        
        self.setWindowTitle("Assign DBC Files to Vehicle")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setModal(True)
        
        self.initUI()
        
        # Load available DBC files and vehicle data
        self.loadData()
    
    def initUI(self):
        """Initialize the dialog UI components"""
        layout = QVBoxLayout(self)
        
        # Vehicle info header
        self.vehicle_info_label = QLabel()
        self.vehicle_info_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.vehicle_info_label)
        
        # Create horizontal layout for lists
        lists_layout = QHBoxLayout()
        
        # Left side - Available DBC files
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available DBC Files:"))
        self.available_files_list = QListWidget()
        available_layout.addWidget(self.available_files_list)
        
        # Import new DBC button
        self.import_button = QPushButton("Import New DBC")
        self.import_button.clicked.connect(self.import_new_dbc)
        available_layout.addWidget(self.import_button)
        
        # Buttons in the middle
        buttons_layout = QVBoxLayout()
        self.assign_btn = QPushButton(">")
        self.assign_btn.clicked.connect(self.assignFile)
        self.unassign_btn = QPushButton("<")
        self.unassign_btn.clicked.connect(self.unassignFile)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.assign_btn)
        buttons_layout.addWidget(self.unassign_btn)
        buttons_layout.addStretch()
        
        # Right side - Assigned DBC files
        assigned_layout = QVBoxLayout()
        assigned_layout.addWidget(QLabel("Assigned DBC Files:"))
        self.assigned_files_list = QListWidget()
        assigned_layout.addWidget(self.assigned_files_list)
        
        # Add the three vertical layouts to the horizontal layout
        lists_layout.addLayout(available_layout)
        lists_layout.addLayout(buttons_layout)
        lists_layout.addLayout(assigned_layout)
        
        # Add lists layout to main layout
        layout.addLayout(lists_layout)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
    
    def loadData(self):
        """Load vehicle information and DBC files"""
        if not self.vehicle_id:
            self.vehicle_info_label.setText("No vehicle selected")
            return
            
        # Get vehicle info
        vehicles = self.dbc_controller.get_vehicles()
        vehicle = next((v for v in vehicles if v.get("id") == self.vehicle_id), None)
        
        if not vehicle:
            self.vehicle_info_label.setText("Vehicle not found")
            return
            
        # Set vehicle info header
        make_model = f"{vehicle.get('make', '')} {vehicle.get('model', '')}".strip()
        if make_model:
            self.vehicle_info_label.setText(f"Vehicle: {vehicle.get('name')} ({make_model})")
        else:
            self.vehicle_info_label.setText(f"Vehicle: {vehicle.get('name')}")
            
        # Get all DBC files in the database
        all_db_files = self.dbc_controller.db_service.get_dbc_files()
        
        # Get files assigned to this vehicle
        vehicle_files = self.dbc_controller.get_vehicle_dbc_files(self.vehicle_id)
        
        # Extract IDs of assigned files
        assigned_ids = [f.get("id") for f in vehicle_files]
        
        # Populate available files list with all DBC files from database
        self.available_files_list.clear()
        for file in all_db_files:
            if file.get("id") not in assigned_ids:
                item = QListWidgetItem(file.get("filename"))
                item.setData(Qt.UserRole, file)
                self.available_files_list.addItem(item)
                
        # Populate assigned files list
        self.assigned_files_list.clear()
        for file in vehicle_files:
            item = QListWidgetItem(file.get("filename"))
            item.setData(Qt.UserRole, file)
            self.assigned_files_list.addItem(item)
    
    def assignFile(self):
        """Assign selected DBC file to the vehicle"""
        selected_items = self.available_files_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            file_data = item.data(Qt.UserRole)
            if self.dbc_controller.vehicle_service.assign_dbc_to_vehicle(file_data.get("id"), self.vehicle_id):
                # Move from available to assigned list
                row = self.available_files_list.row(item)
                self.available_files_list.takeItem(row)
                
                # Add to assigned list
                self.assigned_files_list.addItem(item)
    
    def unassignFile(self):
        """Remove DBC file from vehicle assignment"""
        selected_items = self.assigned_files_list.selectedItems()
        if not selected_items:
            return
            
        for item in selected_items:
            file_data = item.data(Qt.UserRole)
            # Unassign by setting vehicle_id to None
            if self.dbc_controller.vehicle_service.assign_dbc_to_vehicle(file_data.get("id"), None):
                # Move from assigned to available list
                row = self.assigned_files_list.row(item)
                self.assigned_files_list.takeItem(row)
                
                # Add to available list
                self.available_files_list.addItem(item)
    
    def import_new_dbc(self):
        """Import a new DBC file and directly assign it to this vehicle"""
        # Check if the user has add_dbc permission (Netcom Engineer)
        if not self.dbc_controller.auth_service.has_permission("add_dbc"):
            QMessageBox.warning(
                self,
                "Permission Denied",
                "You need Netcom Engineer permissions to import DBC files."
            )
            return
            
        # Import new DBC file and associate with current vehicle
        handler, file_name, error = self.dbc_controller.import_dbc(
            self.parent, 
            store_in_db=True,  # Force storing in database
            vehicle_id=self.vehicle_id
        )
        
        if error:
            QMessageBox.critical(
                self,
                "DBC Import Error",
                error,
                QMessageBox.Ok
            )
        elif file_name:
            QMessageBox.information(
                self,
                "DBC Imported",
                f"DBC file '{file_name}' was imported and assigned to this vehicle."
            )
            # Refresh the lists
            self.loadData() 