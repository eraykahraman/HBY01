from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
import logging

# Base class for all database models
Base = declarative_base()

class DatabaseManager:
    """
    Manager class for database operations.
    Handles connection management, session creation, and basic operations.
    """
    
    def __init__(self, connection_string=None):
        """
        Initialize the database manager with optional connection string.
        
        Args:
            connection_string (str, optional): SQLAlchemy connection string.
                Format: postgresql://username:password@host:port/database
        """
        self.engine = None
        self.session_factory = None
        self.Session = None
        self.logger = logging.getLogger(__name__)
        
        if connection_string:
            self.initialize(connection_string)
    
    def initialize(self, connection_string):
        """
        Initialize the database connection with the given connection string.
        
        Args:
            connection_string (str): SQLAlchemy connection string
                Format: postgresql://username:password@host:port/database
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=5,
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=1800,  # Recycle connections after 30 minutes
                echo=False  # Set to True for SQL query logging
            )
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            # Create scoped session - thread-safe session registry
            self.Session = scoped_session(self.session_factory)
            
            # Test connection
            self.engine.connect().close()
            
            self.logger.info("Database connection initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Database initialization failed: {str(e)}")
            self.engine = None
            self.session_factory = None
            self.Session = None
            return False
    
    def create_tables(self):
        """
        Create all tables defined using the Base class.
        
        Returns:
            bool: True if tables created successfully, False otherwise
        """
        if not self.engine:
            self.logger.error("Engine not initialized. Call initialize() first.")
            return False
            
        try:
            Base.metadata.create_all(self.engine)
            self.logger.info("Database tables created successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create database tables: {str(e)}")
            return False
    
    def get_session(self):
        """
        Get a new database session.
        
        Returns:
            Session: SQLAlchemy session object or None if not initialized
        """
        if not self.Session:
            self.logger.error("Session factory not initialized. Call initialize() first.")
            return None
            
        return self.Session()
    
    def close_session(self, session):
        """
        Close the given database session.
        
        Args:
            session: SQLAlchemy session to close
        """
        if session:
            try:
                session.close()
            except Exception as e:
                self.logger.error(f"Error closing session: {str(e)}")
    
    def dispose(self):
        """
        Dispose of the engine and all its database connections.
        """
        if self.engine:
            self.engine.dispose()
            self.logger.info("Database engine disposed")
            
    def execute_query(self, query, params=None):
        """
        Execute a raw SQL query.
        
        Args:
            query (str): SQL query string
            params (dict, optional): Parameters for the query
            
        Returns:
            Result: Query result or None if execution failed
        """
        if not self.engine:
            self.logger.error("Engine not initialized. Call initialize() first.")
            return None
            
        try:
            with self.engine.connect() as connection:
                if params:
                    result = connection.execute(query, params)
                else:
                    result = connection.execute(query)
                return result
        except Exception as e:
            self.logger.error(f"Query execution failed: {str(e)}")
            return None 