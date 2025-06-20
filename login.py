import tkinter as tk
from tkinter import messagebox
import sqlite3
import os

# --- DB Setup ---
def setup_db():
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('student', 'faculty'))
    )''')

    # Add default faculty user
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                  ("admin", "admin123", "faculty"))
    conn.commit()
    conn.close()

# --- Login Logic ---
def login():
    username = entry_user.get().strip()
    password = entry_pass.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()

    if result:
        role = result[0]
        messagebox.showinfo("Login Success", f"Welcome {role.capitalize()}!")
        login_window.destroy()

        try:
            if role == "faculty":
                os.system("python dashboard_faculty.py")
            else:
                os.system("python dashboard_student.py")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open dashboard: {e}")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# --- GUI Setup ---
setup_db()

login_window = tk.Tk()
login_window.title("Login - Smart Attendance")
login_window.geometry("300x220")
login_window.resizable(False, False)

tk.Label(login_window, text="Smart Attendance System", font=("Helvetica", 14, "bold")).pack(pady=10)
tk.Label(login_window, text="Username").pack()
entry_user = tk.Entry(login_window)
entry_user.pack(pady=2)

tk.Label(login_window, text="Password").pack()
entry_pass = tk.Entry(login_window, show="*")
entry_pass.pack(pady=2)

tk.Button(login_window, text="Login", command=login, bg="blue", fg="white", width=20).pack(pady=15)

login_window.mainloop()

