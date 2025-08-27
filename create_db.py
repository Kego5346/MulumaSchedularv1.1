import sqlite3
import shutil
import os

DB_FILE = 'scheduler.db'
BACKUP_FILE = 'scheduler_backup.db'

# Step 1: Check if DB file exists and make a backup
if os.path.exists(DB_FILE):
    shutil.copyfile(DB_FILE, BACKUP_FILE)
    print(f"Backup created: {BACKUP_FILE}")
else:
    print(f"No existing database found. A new database will be created.")

# Step 2: Connect (this will fail if the old DB is corrupted)
try:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Step 3: Check if 'date' column exists
    c.execute("PRAGMA table_info(task);")
    columns = [col[1] for col in c.fetchall()]  # col[1] is column name

    if 'date' not in columns:
        c.execute("ALTER TABLE task ADD COLUMN date TEXT;")
        print("Column 'date' added successfully.")
    else:
        print("Column 'date' already exists. No changes made.")
    
    conn.commit()
    conn.close()
    print("Database upgrade completed successfully!")

except sqlite3.DatabaseError:
    print("ERROR: The existing database is corrupted. Creating a new database instead.")
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS task (
        id INTEGER PRIMARY KEY,
        name TEXT,
        surname TEXT,
        backlog TEXT,
        process TEXT,
        done TEXT,
        date TEXT
    )
    """)
    conn.commit()
    conn.close()
    print("New database created successfully!")
