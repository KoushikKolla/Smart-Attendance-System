import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd

def fetch_data():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance")
    rows = cursor.fetchall()
    conn.close()
    return rows

def load_data():
    records = fetch_data()
    for row in tree.get_children():
        tree.delete(row)
    for row in records:
        tree.insert("", tk.END, values=row)

def export_to_excel():
    records = fetch_data()
    if not records:
        messagebox.showinfo("No Data", "No attendance records found.")
        return
    df = pd.DataFrame(records, columns=["ID", "Name", "Date", "Time"])
    df.to_excel("attendance_report.xlsx", index=False)
    messagebox.showinfo("Exported", "Attendance exported to attendance_report.xlsx")

# GUI
root = tk.Tk()
root.title("Attendance Viewer")
root.geometry("600x400")

frame = ttk.Frame(root)
frame.pack(pady=10)

tree = ttk.Treeview(frame, columns=("ID", "Name", "Date", "Time"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Name", text="Name")
tree.heading("Date", text="Date")
tree.heading("Time", text="Time")

tree.column("ID", width=50)
tree.column("Name", width=150)
tree.column("Date", width=100)
tree.column("Time", width=100)

tree.pack()

btn_frame = ttk.Frame(root)
btn_frame.pack(pady=20)

load_btn = ttk.Button(btn_frame, text="Load Attendance", command=load_data)
load_btn.grid(row=0, column=0, padx=10)

export_btn = ttk.Button(btn_frame, text="Export to Excel", command=export_to_excel)
export_btn.grid(row=0, column=1, padx=10)

root.mainloop()
