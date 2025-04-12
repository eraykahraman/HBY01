from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean
from sqlalchemy.sql import func
from utils.db_manager import Base
import datetime
import enum
import hashlib
import os

class UserRole(enum.Enum):
    """Enum for user roles with different permission levels"""
    BASIC_USER = "basic_user"
    MODULE_OWNER = "module_owner"
    NETCOM_ENGINEER = "netcom_engineer"

class User(Base):
    """Model for user accounts with authentication and roles"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(64), nullable=False)
    
    # User role determines permissions
    role = Column(String(20), nullable=False, default=UserRole.BASIC_USER.value)
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<User id={self.id}, username={self.username}, role={self.role}>"
    
    @staticmethod
    def hash_password(password, salt=None):
        """
        Hash a password with a salt for secure storage
        
        Args:
            password (str): Plain text password
            salt (str, optional): Salt for hashing. If None, generates a random salt.
            
        Returns:
            tuple: (password_hash, salt)
        """
        if salt is None:
            salt = os.urandom(32).hex()  # Generate a random salt
            
        # Hash the password with the salt
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # Number of iterations
        )
        password_hash = hash_obj.hex()
        
        return password_hash, salt
    
    def verify_password(self, password):
        """
        Verify if the provided password matches the stored hash
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        password_hash, _ = self.hash_password(password, self.salt)
        return password_hash == self.password_hash
    
    def has_permission(self, permission):
        """
        Check if the user has a specific permission based on their role
        
        Args:
            permission (str): Permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        # Define role-based permissions
        role_permissions = {
            UserRole.BASIC_USER.value: ['view_dbc'],
            UserRole.MODULE_OWNER.value: ['view_dbc', 'edit_dbc'],
            UserRole.NETCOM_ENGINEER.value: ['view_dbc', 'edit_dbc', 'add_dbc', 'delete_dbc', 'manage_users']
        }
        
        # Check if user's role has the requested permission
        return permission in role_permissions.get(self.role, []) 