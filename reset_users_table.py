import sqlite3

conn = sqlite3.connect("attendance.db")
cursor = conn.cursor()

# Drop old users table if exists
cursor.execute("DROP TABLE IF EXISTS users")
conn.commit()
conn.close()

print("✅ Old 'users' table dropped. Now run login.py again.")
