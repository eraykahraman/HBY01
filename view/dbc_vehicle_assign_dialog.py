from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QMessageBox, QDialogButtonBox,
    QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt

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