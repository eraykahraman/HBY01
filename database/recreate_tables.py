import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.session import recreate_tables

if __name__ == "__main__":
    print("Recreating database tables...")
    recreate_tables()
    print("Database tables recreated successfully!") 