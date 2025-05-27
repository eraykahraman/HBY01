from sqlalchemy import create_engine, text
from database.session import db_session
from database.models import Base
from sqlalchemy.exc import ProgrammingError

def migrate():
    """Add role column to users table"""
    try:
        with db_session.get_session() as session:
            # Check if column already exists
            try:
                session.execute(text("SELECT role FROM users LIMIT 1"))
                print("Role column already exists")
                return
            except ProgrammingError:
                pass  # Column doesn't exist, proceed with adding it

            # Add role column with default value
            session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'generic_user'
            """))
            session.commit()
            print("Successfully added role column to users table")
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        session.rollback()
        raise e

def recreate_tables():
    """Drop and recreate all tables"""
    db_session.drop_tables()
    db_session.create_tables()

if __name__ == "__main__":
    migrate() 