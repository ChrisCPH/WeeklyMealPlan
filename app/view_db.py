import sqlite3

# Connect to the database
conn = sqlite3.connect('instance/recipes.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [t[0] for t in cursor.fetchall()]
print("Tables found:", tables, "\n")

# Loop through each table
for table in tables:
    print(f"--- Table: {table} ---")
    
    # Get column names
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    print("Columns:", columns)
    
    # Fetch first 5 rows
    cursor.execute(f"SELECT * FROM {table} LIMIT 5;")
    rows = cursor.fetchall()
    
    if rows:
        for row in rows:
            row_dict = dict(zip(columns, row))
            print(row_dict)
    else:
        print("No rows found.")
    
    print("\n")

conn.close()

# This is just for testing/debugging the database
# Use: python view_db.py