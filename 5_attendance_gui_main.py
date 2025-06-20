import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import cv2
import pandas as pd
from datetime import datetime

# Attendance DB Logic
def insert_or_skip(user_id, name):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER,
                    name TEXT,
                    date TEXT,
                    time TEXT
                )''')

    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    c.execute("SELECT * FROM attendance WHERE id=? AND date=?", (user_id, date))
    if c.fetchone() is None:
        c.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", (user_id, name, date, time))
        conn.commit()
        print(f"✅ Attendance marked for {name}")
    conn.close()

def get_user_name(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Unknown"

# Load and display attendance records
def load_data():
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attendance WHERE date = date('now')")
    rows = cursor.fetchall()
    conn.close()

    for i in tree.get_children():
        tree.delete(i)
    for row in rows:
        tree.insert("", tk.END, values=row)

# Export to Excel
def export_to_excel():
    conn = sqlite3.connect("attendance.db")
    df = pd.read_sql_query("SELECT * FROM attendance", conn)
    df.to_excel("attendance_report.xlsx", index=False)
    conn.close()
    messagebox.showinfo("Exported", "Attendance exported to attendance_report.xlsx")

# Start Attendance via webcam
def start_attendance():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cam = cv2.VideoCapture(0)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            face_id, confidence = recognizer.predict(gray[y:y+h, x:x+w])
            if confidence < 70:
                name = get_user_name(face_id)
                insert_or_skip(face_id, name)
                label = f"{name} ({round(100 - confidence)}%)"
            else:
                label = "Unknown"
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, label, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Attendance System (Press q to quit)', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

# GUI App
root = tk.Tk()
root.title("Smart Attendance System")
root.geometry("700x500")

style = ttk.Style()
style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))

# Buttons
btn_frame = ttk.Frame(root)
btn_frame.pack(pady=20)

ttk.Button(btn_frame, text="Start Attendance", command=start_attendance).grid(row=0, column=0, padx=10)
ttk.Button(btn_frame, text="Load Today's Records", command=load_data).grid(row=0, column=1, padx=10)
ttk.Button(btn_frame, text="Export to Excel", command=export_to_excel).grid(row=0, column=2, padx=10)

# Table
tree = ttk.Treeview(root, columns=("ID", "Name", "Date", "Time"), show="headings", height=15)
for col in ("ID", "Name", "Date", "Time"):
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(pady=10)

root.mainloop()
