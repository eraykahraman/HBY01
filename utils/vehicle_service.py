import logging
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from sqlalchemy import inspect

from model.dbc_orm import Vehicle, DBCFile
from utils import db_manager, config

class VehicleService:
    """
    Service class for Vehicle database operations.
    Provides methods for storing and retrieving Vehicle data.
    """
    
    def __init__(self, custom_db_manager = None):
        """
        Initialize the Vehicle service.
        
        Args:
            custom_db_manager: Database manager to use (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.db_manager = custom_db_manager if custom_db_manager else db_manager
    
    def is_database_enabled(self) -> bool:
        """
        Check if database is enabled and initialized.
        
        Returns:
            bool: True if enabled and initialized, False otherwise
        """
        return config.get("database", "enabled") and self.db_manager.engine is not None
    
    def create_vehicle(self, name: str, make: str = None, model: str = None, 
                      year: int = None, vin: str = None, 
                      description: str = None) -> Optional[int]:
        """
        Create a new vehicle in the database.
        
        Args:
            name (str): Vehicle name (required)
            make (str, optional): Vehicle manufacturer
            model (str, optional): Vehicle model
            year (int, optional): Vehicle year
            vin (str, optional): Vehicle Identification Number
            description (str, optional): Vehicle description
            
        Returns:
            Optional[int]: ID of the created vehicle or None if failed
        """
        if not self.is_database_enabled():
            self.logger.warning("Database not enabled, skipping vehicle creation")
            return None
        
        try:
            session = self.db_manager.get_session()
            
            try:
                # Create new vehicle record
                vehicle = Vehicle(
                    name=name,
                    make=make,
                    model=model,
                    year=year,
                    vin=vin,
                    description=description,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                session.add(vehicle)
                session.commit()
                
                return vehicle.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error creating vehicle: {str(e)}")
                return None
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error creating vehicle: {str(e)}")
            return None
    
    def get_vehicle(self, vehicle_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a vehicle by ID.
        
        Args:
            vehicle_id (int): Vehicle ID
            
        Returns:
            Optional[Dict[str, Any]]: Vehicle dictionary or None if not found
        """
        if not self.is_database_enabled():
            return None
        
        try:
            session = self.db_manager.get_session()
            
            try:
                vehicle = session.query(Vehicle).get(vehicle_id)
                
                if not vehicle:
                    return None
                
                result = {
                    "id": vehicle.id,
                    "name": vehicle.name,
                    "make": vehicle.make,
                    "model": vehicle.model,
                    "year": vehicle.year,
                    "vin": vehicle.vin,
                    "description": vehicle.description,
                    "created_at": vehicle.created_at,
                    "updated_at": vehicle.updated_at
                }
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error getting vehicle: {str(e)}")
            return None
    
    def update_vehicle(self, vehicle_id: int, **kwargs) -> bool:
        """
        Update a vehicle's attributes.
        
        Args:
            vehicle_id (int): Vehicle ID
            **kwargs: Attributes to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_database_enabled():
            return False
        
        try:
            session = self.db_manager.get_session()
            
            try:
                vehicle = session.query(Vehicle).get(vehicle_id)
                
                if not vehicle:
                    return False
                
                # Update provided attributes
                for key, value in kwargs.items():
                    if hasattr(vehicle, key):
                        setattr(vehicle, key, value)
                
                # Always update the updated_at timestamp
                vehicle.updated_at = datetime.utcnow()
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error updating vehicle: {str(e)}")
                return False
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error updating vehicle: {str(e)}")
            return False
    
    def delete_vehicle(self, vehicle_id: int) -> bool:
        """
        Delete a vehicle and all its associated DBC files.
        
        Args:
            vehicle_id (int): Vehicle ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_database_enabled():
            return False
        
        try:
            session = self.db_manager.get_session()
            
            try:
                vehicle = session.query(Vehicle).get(vehicle_id)
                
                if not vehicle:
                    return False
                
                # SQLAlchemy will handle cascade deletion of associated DBC files
                session.delete(vehicle)
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error deleting vehicle: {str(e)}")
                return False
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error deleting vehicle: {str(e)}")
            return False
    
    def get_all_vehicles(self) -> List[Dict[str, Any]]:
        """
        Get all vehicles from the database.
        
        Returns:
            List[Dict[str, Any]]: List of vehicle dictionaries
        """
        if not self.is_database_enabled():
            return []
        
        try:
            session = self.db_manager.get_session()
            
            try:
                vehicles = session.query(Vehicle).all()
                
                result = []
                for vehicle in vehicles:
                    result.append({
                        "id": vehicle.id,
                        "name": vehicle.name,
                        "make": vehicle.make,
                        "model": vehicle.model,
                        "year": vehicle.year,
                        "vin": vehicle.vin,
                        "description": vehicle.description,
                        "created_at": vehicle.created_at,
                        "updated_at": vehicle.updated_at
                    })
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error getting all vehicles: {str(e)}")
            return []
    
    def get_vehicle_dbc_files(self, vehicle_id: int) -> List[Dict[str, Any]]:
        """
        Get all DBC files associated with a vehicle.
        
        Args:
            vehicle_id (int): Vehicle ID
            
        Returns:
            List[Dict[str, Any]]: List of DBC file dictionaries
        """
        if not self.is_database_enabled():
            return []
        
        try:
            session = self.db_manager.get_session()
            
            try:
                # Check if the vehicle_id column exists in the dbc_files table
                inspector = inspect(self.db_manager.engine)
                columns = inspector.get_columns('dbc_files')
                column_names = [col['name'] for col in columns]
                
                if 'vehicle_id' not in column_names:
                    self.logger.warning("vehicle_id column not found in dbc_files table - returning empty list")
                    return []
                
                # Query for DBC files with matching vehicle_id
                dbc_files = session.query(DBCFile).filter_by(vehicle_id=vehicle_id).all()
                
                result = []
                for dbc_file in dbc_files:
                    result.append({
                        "id": dbc_file.id,
                        "filename": dbc_file.filename,
                        "filepath": dbc_file.filepath,
                        "file_size": dbc_file.file_size,
                        "file_hash": dbc_file.file_hash,
                        "version": dbc_file.version,
                        "created_at": dbc_file.created_at,
                        "updated_at": dbc_file.updated_at,
                        "last_accessed": dbc_file.last_accessed,
                        "nodes_count": dbc_file.nodes_count,
                        "messages_count": dbc_file.messages_count,
                        "signals_count": dbc_file.signals_count,
                        "file_metadata": dbc_file.file_metadata
                    })
                
                return result
                
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error getting vehicle DBC files: {str(e)}")
            return []
    
    def assign_dbc_to_vehicle(self, dbc_id: int, vehicle_id: int) -> bool:
        """
        Assign a DBC file to a vehicle.
        
        Args:
            dbc_id (int): DBC file ID
            vehicle_id (int): Vehicle ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_database_enabled():
            return False
        
        try:
            session = self.db_manager.get_session()
            
            try:
                dbc_file = session.query(DBCFile).get(dbc_id)
                vehicle = session.query(Vehicle).get(vehicle_id)
                
                if not dbc_file or not vehicle:
                    return False
                
                # Assign DBC to vehicle
                dbc_file.vehicle_id = vehicle_id
                
                session.commit()
                return True
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error assigning DBC to vehicle: {str(e)}")
                return False
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error assigning DBC to vehicle: {str(e)}")
            return False 