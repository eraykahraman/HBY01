from werkzeug.security import generate_password_hash, check_password_hash
from database.repository import UserRepository
from database.models import UserRole
from PyQt5.QtWidgets import QDialog

class UserController:
    @staticmethod
    def validate_role(role: str) -> bool:
        """Validate if the role is valid"""
        return role in [r.value for r in UserRole]

    @staticmethod
    def register(username: str, password: str, role: str = UserRole.GENERIC_USER.value) -> (bool, str, str):
        """
        Register a new user
        
        Args:
            username (str): Username for the new user
            password (str): Password for the new user
            role (str): User role (default: generic_user)
            
        Returns:
            tuple: (success, message, role)
        """
        if not username or not password:
            return False, "Username and password are required.", role
            
        if not UserController.validate_role(role):
            return False, f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}", role
            
        if UserRepository.get_user_by_username(username):
            return False, "Username already exists.", role
            
        password_hash = generate_password_hash(password)
        user = UserRepository.create_user(username, password_hash, role)
        
        if user:
            return True, "Registration successful.", user.role
        return False, "Registration failed.", role

    @staticmethod
    def login(username: str, password: str) -> (bool, str, str):
        """
        Login a user
        
        Args:
            username (str): Username to login
            password (str): Password to verify
            
        Returns:
            tuple: (success, message, role)
        """
        password_hash = UserRepository.get_user_password_hash(username)
        if not password_hash:
            return False, "User not found.", UserRole.GENERIC_USER.value
            
        if check_password_hash(password_hash, password):
            role = UserRepository.get_user_role(username)
            return True, "Login successful.", role
        return False, "Invalid password.", UserRole.GENERIC_USER.value

    @staticmethod
    def get_user_role(username: str) -> str:
        """
        Get the role of a user
        
        Args:
            username (str): Username to get role for
            
        Returns:
            str: User role or default role if not found
        """
        role = UserRepository.get_user_role(username)
        return role if role else UserRole.GENERIC_USER.value

    @staticmethod
    def update_user_role(username: str, new_role: str) -> (bool, str):
        """
        Update the role of a user
        
        Args:
            username (str): Username to update
            new_role (str): New role to set
            
        Returns:
            tuple: (success, message)
        """
        if not UserController.validate_role(new_role):
            return False, f"Invalid role. Must be one of: {', '.join([r.value for r in UserRole])}"
            
        if UserRepository.update_user_role(username, new_role):
            return True, "Role updated successfully."
        return False, "User not found." 