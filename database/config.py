from typing import Dict, Any
import os
from sqlalchemy.engine.url import URL

class DatabaseConfig:
    """Database configuration settings"""
    
    # Default database settings
    DEFAULT_SETTINGS = {
        'drivername': 'postgresql',
        'host': 'localhost',
        'port': 5432,
        'username': 'dbc1',
        'password': 's7s5dbaE',
        'database': 'dbc'
        
    }
    
    @classmethod
    def get_settings(cls) -> Dict[str, Any]:
        """Get database settings from environment variables or use defaults"""
        return {
            'drivername': os.getenv('DB_DRIVER', cls.DEFAULT_SETTINGS['drivername']),
            'host': os.getenv('DB_HOST', cls.DEFAULT_SETTINGS['host']),
            'port': int(os.getenv('DB_PORT', cls.DEFAULT_SETTINGS['port'])),
            'username': os.getenv('DB_USER', cls.DEFAULT_SETTINGS['username']),
            'password': os.getenv('DB_PASSWORD', cls.DEFAULT_SETTINGS['password']),
            'database': os.getenv('DB_NAME', cls.DEFAULT_SETTINGS['database'])
        }
    
    @classmethod
    def get_url(cls) -> URL:
        """Get SQLAlchemy URL object from settings"""
        return URL.create(**cls.get_settings()) 