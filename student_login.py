import tkinter as tk
from tkinter import messagebox
import sqlite3

def login_student():
    username = entry_user.get().strip()
    password = entry_pass.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=? AND role='student'", (username, password))
    result = c.fetchone()
    conn.close()

    if result:
        messagebox.showinfo("Login Success", f"Welcome Student: {username}")
        root.destroy()
        # You can import dashboard_student here if exists:
        # import dashboard_student
    else:
        messagebox.showerror("Login Failed", "Invalid credentials or not a student.")

# --- GUI ---
root = tk.Tk()
root.title("Student Login - Smart Attendance System")
root.geometry("300x200")
root.resizable(False, False)

tk.Label(root, text="Student Username").pack(pady=5)
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Password").pack(pady=5)
entry_pass = tk.Entry(root, show="*")
entry_pass.pack()

tk.Button(root, text="Login", command=login_student, bg="green", fg="white").pack(pady=15)

root.mainloop()
