import sqlite3

def clean_database():
    # Connect to the database
    conn = sqlite3.connect('devreplay.db')
    cursor = conn.cursor()
    
    # List of tables to keep
    tables_to_keep = ['entries']
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    # Drop unused tables
    for table in tables:
        table_name = table[0]
        if table_name not in tables_to_keep and table_name != 'sqlite_sequence':
            print(f"Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("\nDatabase cleanup completed!")
    print("Kept table: entries")
    print("Removed all other tables.")

if __name__ == "__main__":
    clean_database() 