import logging
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

from model.user_orm import User, UserRole
from utils import db_manager, config

class AuthService:
    """
    Service class for user authentication and authorization.
    Handles user login, session management, and permission checking.
    """
    
    def __init__(self, db_manager_instance=None):
        """
        Initialize the authentication service.
        
        Args:
            db_manager_instance: Database manager to use (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.db_manager = db_manager_instance if db_manager_instance else db_manager
        self.current_user = None
    
    def login(self, username: str, password: str) -> tuple[bool, str]:
        """
        Authenticate a user with username and password.
        
        Args:
            username (str): User's username
            password (str): User's password
            
        Returns:
            tuple: (success, message)
        """
        try:
            session = self.db_manager.get_session()
            
            try:
                # Find user by username
                user = session.query(User).filter_by(username=username).first()
                
                if not user:
                    return False, "Invalid username or password"
                
                if not user.is_active:
                    return False, "Account is disabled"
                
                # Verify password
                if not user.verify_password(password):
                    return False, "Invalid username or password"
                
                # Update last login time
                user.last_login = datetime.utcnow()
                session.commit()
                
                # Set current user
                self.current_user = {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": user.role,
                    "is_verified": user.is_verified,
                    "created_at": user.created_at,
                    "last_login": user.last_login
                }
                
                return True, "Login successful"
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error during login: {str(e)}")
                return False, "Database error occurred"
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error during login: {str(e)}")
            return False, "Authentication error"
    
    def logout(self):
        """
        Log out the current user.
        """
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """
        Check if a user is currently authenticated.
        
        Returns:
            bool: True if user is authenticated, False otherwise
        """
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently authenticated user.
        
        Returns:
            Optional[Dict[str, Any]]: User information or None if not authenticated
        """
        return self.current_user
    
    def has_permission(self, permission: str) -> bool:
        """
        Check if the current user has a specific permission.
        
        Args:
            permission (str): Permission to check
            
        Returns:
            bool: True if user has permission, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        # Define role-based permissions
        role_permissions = {
            UserRole.BASIC_USER.value: ['view_dbc'],
            UserRole.MODULE_OWNER.value: ['view_dbc', 'edit_dbc'],
            UserRole.NETCOM_ENGINEER.value: ['view_dbc', 'edit_dbc', 'add_dbc', 'delete_dbc', 'manage_users']
        }
        
        # Check if user's role has the requested permission
        return permission in role_permissions.get(self.current_user["role"], [])
    
    def register_user(self, username: str, email: str, password: str, role: str = UserRole.BASIC_USER.value) -> tuple[bool, str, Optional[int]]:
        """
        Register a new user.
        
        Args:
            username (str): User's username
            email (str): User's email
            password (str): User's password
            role (str, optional): User's role
            
        Returns:
            tuple: (success, message, user_id)
        """
        try:
            session = self.db_manager.get_session()
            
            try:
                # Check if username already exists
                existing_user = session.query(User).filter_by(username=username).first()
                if existing_user:
                    return False, "Username already exists", None
                
                # Check if email already exists
                existing_email = session.query(User).filter_by(email=email).first()
                if existing_email:
                    return False, "Email already exists", None
                
                # Hash password
                password_hash, salt = User.hash_password(password)
                
                # Create new user
                user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    salt=salt,
                    role=role,
                    is_active=True,
                    is_verified=False,
                    created_at=datetime.utcnow()
                )
                
                session.add(user)
                session.commit()
                
                return True, "User registered successfully", user.id
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Database error during registration: {str(e)}")
                return False, "Database error occurred", None
            finally:
                self.db_manager.close_session(session)
                
        except Exception as e:
            self.logger.error(f"Error during registration: {str(e)}")
            return False, "Registration error", None 