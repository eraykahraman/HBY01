from .add_role_column import migrate as add_role_column

def run_all_migrations():
    """Run all database migrations in order"""
    print("Starting database migrations...")
    
    # Add role column
    print("Running migration: Add role column")
    add_role_column()
    
    print("All migrations completed successfully!")

if __name__ == "__main__":
    run_all_migrations() 