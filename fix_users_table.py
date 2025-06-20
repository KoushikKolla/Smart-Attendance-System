import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Add 'name' column if not exists
try:
    cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
    print("✅ 'name' column added to users table.")
except:
    print("ℹ️ 'name' column may already exist.")

conn.commit()
conn.close()
