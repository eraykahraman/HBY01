from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QMessageBox,
    QMenu, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from view.vehicle_dialog import VehicleDialog, DBC_Vehicle_AssignDialog

class VehicleView(QWidget):
    """Widget for displaying and managing vehicles"""
    
    vehicle_selected = pyqtSignal(dict)  # Emits selected vehicle data
    
    def __init__(self, dbc_controller, auth_service, parent=None):
        super().__init__(parent)
        self.dbc_controller = dbc_controller
        self.auth_service = auth_service
        self.vehicles = []
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Vehicles")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        # Add vehicle button (only for Netcom Engineers)
        self.add_vehicle_btn = QPushButton("Create Vehicle")
        self.add_vehicle_btn.clicked.connect(self.show_add_vehicle_dialog)
        # Only show for Netcom Engineers
        self.add_vehicle_btn.setVisible(self.auth_service.has_permission("manage_users"))
        header_layout.addWidget(self.add_vehicle_btn)
        
        # Add DBC to vehicle button (only enabled when a vehicle is selected)
        self.add_dbc_btn = QPushButton("Add DBC File")
        self.add_dbc_btn.clicked.connect(self.add_dbc_to_selected_vehicle)
        self.add_dbc_btn.setEnabled(False)  # Initially disabled until a vehicle is selected
        # Only show for Netcom Engineers
        self.add_dbc_btn.setVisible(self.auth_service.has_permission("manage_users"))
        header_layout.addWidget(self.add_dbc_btn)
        
        layout.addLayout(header_layout)
        
        # Vehicles list
        self.vehicles_list = QListWidget()
        self.vehicles_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.vehicles_list.customContextMenuRequested.connect(self.show_context_menu)
        self.vehicles_list.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.vehicles_list)
        
        # Initially load vehicles
        self.load_vehicles()
    
    def show_add_vehicle_dialog(self):
        """Show dialog for adding a new vehicle"""
        if not self.auth_service.has_permission("manage_users"):
            QMessageBox.warning(
                self,
                "Permission Denied",
                "You need Netcom Engineer permissions to add vehicles."
            )
            return
            
        dialog = VehicleDialog(self)
        result = dialog.exec_()
        
        if result == dialog.Accepted:
            vehicle_data = dialog.getVehicleData()
            vehicle_id = self.dbc_controller.vehicle_service.create_vehicle(
                name=vehicle_data.get("name"),
                make=vehicle_data.get("make"),
                model=vehicle_data.get("model"),
                year=vehicle_data.get("year"),
                vin=vehicle_data.get("vin"),
                description=vehicle_data.get("description")
            )
            
            if vehicle_id:
                QMessageBox.information(
                    self,
                    "Vehicle Created",
                    f"Vehicle '{vehicle_data.get('name')}' created successfully."
                )
                # Reload the vehicles list
                self.load_vehicles()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to create vehicle. Check database connection."
                )
    
    def show_edit_vehicle_dialog(self, vehicle_data):
        """Show dialog for editing a vehicle"""
        if not self.auth_service.has_permission("manage_users"):
            QMessageBox.warning(
                self,
                "Permission Denied",
                "You need Netcom Engineer permissions to edit vehicles."
            )
            return
            
        dialog = VehicleDialog(self, vehicle_data)
        result = dialog.exec_()
        
        if result == dialog.Accepted:
            updated_data = dialog.getVehicleData()
            success = self.dbc_controller.vehicle_service.update_vehicle(
                vehicle_data.get("id"),
                name=updated_data.get("name"),
                make=updated_data.get("make"),
                model=updated_data.get("model"),
                year=updated_data.get("year"),
                vin=updated_data.get("vin"),
                description=updated_data.get("description")
            )
            
            if success:
                QMessageBox.information(
                    self,
                    "Vehicle Updated",
                    f"Vehicle '{updated_data.get('name')}' updated successfully."
                )
                # Reload the vehicles list
                self.load_vehicles()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to update vehicle. Check database connection."
                )
    
    def show_assign_dbc_dialog(self, vehicle_data):
        """Show dialog for assigning DBC files to a vehicle"""
        if not self.auth_service.has_permission("manage_users"):
            QMessageBox.warning(
                self,
                "Permission Denied",
                "You need Netcom Engineer permissions to assign DBC files."
            )
            return
            
        dialog = DBC_Vehicle_AssignDialog(
            self.dbc_controller,
            self,
            vehicle_data.get("id")
        )
        dialog.exec_()
        
        # No need to refresh the vehicle list after assignment
    
    def delete_vehicle(self, vehicle_data):
        """Delete a vehicle after confirmation"""
        if not self.auth_service.has_permission("manage_users"):
            QMessageBox.warning(
                self,
                "Permission Denied",
                "You need Netcom Engineer permissions to delete vehicles."
            )
            return
            
        # Ask for confirmation
        result = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete vehicle '{vehicle_data.get('name')}'?\n\n"
            "This will also delete all DBC files associated with this vehicle.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            success = self.dbc_controller.vehicle_service.delete_vehicle(vehicle_data.get("id"))
            
            if success:
                QMessageBox.information(
                    self,
                    "Vehicle Deleted",
                    f"Vehicle '{vehicle_data.get('name')}' and its DBC files deleted successfully."
                )
                # Reload the vehicles list
                self.load_vehicles()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Failed to delete vehicle. Check database connection."
                )
    
    def load_vehicles(self):
        """Load vehicles from the database"""
        self.vehicles = self.dbc_controller.get_vehicles()
        self.update_vehicles_list()
    
    def update_vehicles_list(self):
        """Update the vehicles list widget with current data"""
        self.vehicles_list.clear()
        
        for vehicle in self.vehicles:
            # Create list item with vehicle name
            name = vehicle.get("name", "Unnamed Vehicle")
            make_model = ""
            
            # Add make/model if available
            if vehicle.get("make") or vehicle.get("model"):
                make_model = f" ({vehicle.get('make', '')} {vehicle.get('model', '')})"
            
            item = QListWidgetItem(f"{name}{make_model}")
            item.setData(Qt.UserRole, vehicle)
            self.vehicles_list.addItem(item)
    
    def on_selection_changed(self):
        """Handle selection changes in the vehicles list"""
        selected_items = self.vehicles_list.selectedItems()
        if selected_items:
            vehicle = selected_items[0].data(Qt.UserRole)
            self.vehicle_selected.emit(vehicle)
            # Enable the add DBC button when a vehicle is selected
            self.add_dbc_btn.setEnabled(True)
        else:
            # Disable the add DBC button when no vehicle is selected
            self.add_dbc_btn.setEnabled(False)
    
    def show_context_menu(self, position):
        """Show context menu for the vehicles list"""
        item = self.vehicles_list.itemAt(position)
        if not item:
            return
            
        vehicle = item.data(Qt.UserRole)
        if not vehicle:
            return
            
        # Create context menu
        menu = QMenu()
        
        # Only show these actions for users with proper permissions
        if self.auth_service.has_permission("manage_users"):
            edit_action = menu.addAction("Edit Vehicle")
            assign_action = menu.addAction("Assign DBC Files")
            menu.addSeparator()
            delete_action = menu.addAction("Delete Vehicle")
            
            # Show the menu
            action = menu.exec_(self.vehicles_list.mapToGlobal(position))
            
            if action == edit_action:
                self.show_edit_vehicle_dialog(vehicle)
            elif action == assign_action:
                self.show_assign_dbc_dialog(vehicle)
            elif action == delete_action:
                self.delete_vehicle(vehicle)
    
    def add_dbc_to_selected_vehicle(self):
        """Add DBC file to the currently selected vehicle"""
        selected_items = self.vehicles_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "No Vehicle Selected",
                "Please select a vehicle first to add DBC files."
            )
            return
            
        vehicle = selected_items[0].data(Qt.UserRole)
        self.show_assign_dbc_dialog(vehicle)
    
    def update_permissions(self):
        """Update UI based on current user permissions"""
        has_permission = self.auth_service.has_permission("manage_users")
        self.add_vehicle_btn.setVisible(has_permission)
        self.add_dbc_btn.setVisible(has_permission) 