import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )
""")

# Optional: add a sample user (ID must match face ID)
cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (1, 'Koushik'))
cursor.execute("INSERT OR IGNORE INTO users (id, name) VALUES (?, ?)", (2, 'Rahul'))

conn.commit()
conn.close()
print("User table created and sample users added.")
