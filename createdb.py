import sqlite3

conn = sqlite3.connect('scheduler.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS task (
    id INTEGER PRIMARY KEY,
    name TEXT,
    surname TEXT,
    backlog TEXT,
    process TEXT,
    done TEXT,
    date TEXT
)
''')

conn.commit()
conn.close()
