from werkzeug.security import generate_password_hash, check_password_hash
from database.repository import UserRepository
from PyQt5.QtWidgets import QDialog

class UserController:
    @staticmethod
    def register(username: str, password: str) -> (bool, str):
        if not username or not password:
            return False, "Username and password are required."
        if UserRepository.get_user_by_username(username):
            return False, "Username already exists."
        password_hash = generate_password_hash(password)
        user = UserRepository.create_user(username, password_hash)
        if user:
            return True, "Registration successful."
        return False, "Registration failed."

    @staticmethod
    def login(username: str, password: str) -> (bool, str):
        password_hash = UserRepository.get_user_password_hash(username)
        if not password_hash:
            return False, "User not found."
        if check_password_hash(password_hash, password):
            return True, "Login successful."
        return False, "Invalid password." 