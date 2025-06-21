import tkinter as tk
from tkinter import ttk, messagebox
import cv2
import os
import sqlite3
import pandas as pd
import numpy as np
from PIL import Image
from datetime import datetime

# Create required folders
os.makedirs("dataset", exist_ok=True)
os.makedirs("trainer", exist_ok=True)

# --- Database for face registration ---
def save_user_to_db(user_id, name):
    with sqlite3.connect("attendance.db") as conn:
        c = conn.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS face_users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
        c.execute("INSERT OR REPLACE INTO face_users (id, name) VALUES (?, ?)", (user_id, name))
        conn.commit()

# --- Face Registration Function ---
def register_face():
    try:
        user_id = int(entry_id.get())
        name = entry_name.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Please enter a valid name.")
            return

        save_user_to_db(user_id, name)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        cam = cv2.VideoCapture(0)
        sample_count = 0

        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                sample_count += 1
                cv2.imwrite(f"dataset/User.{user_id}.{sample_count}.jpg", gray[y:y + h, x:x + w])
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(img, f"Samples: {sample_count}/30", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                            (255, 255, 255), 2)

            cv2.imshow('Registering Face - Press Q to Quit', img)
            if cv2.waitKey(1) & 0xFF == ord('q') or sample_count >= 30:
                break

        cam.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Done", f"Face registration completed for {name}.")

    except ValueError:
        messagebox.showerror("Input Error", "ID must be a number.")

# --- Model Training Function ---
def train_model():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_samples, ids = [], []

    image_paths = [os.path.join("dataset", f) for f in os.listdir("dataset") if f.endswith(".jpg")]
    for path in image_paths:
        try:
            gray_img = Image.open(path).convert('L')
            img_numpy = np.array(gray_img, 'uint8')
            user_id = int(os.path.split(path)[-1].split(".")[1])
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = face_cascade.detectMultiScale(img_numpy)

            for (x, y, w, h) in faces:
                face_samples.append(img_numpy[y:y + h, x:x + w])
                ids.append(user_id)

        except Exception as e:
            print(f"⚠️ Skipping {path}: {e}")

    if not face_samples:
        messagebox.showwarning("No Data", "No valid face data found. Register first.")
        return

    recognizer.train(face_samples, np.array(ids))
    recognizer.save("trainer/trainer.yml")
    messagebox.showinfo("Success", "Model trained and saved to trainer.yml")

# --- Attendance Functions ---
def get_user_name(user_id):
    with sqlite3.connect("attendance.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM face_users WHERE id=?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else "Unknown"

def insert_or_skip(user_id, name):
    with sqlite3.connect("attendance.db") as conn:
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

# --- Attendance Capture ---
def start_attendance():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read('trainer/trainer.yml')
    except:
        messagebox.showerror("Model Missing", "Please train the model first.")
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cam = cv2.VideoCapture(0)

    while True:
        ret, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)

        for (x, y, w, h) in faces:
            face_id, confidence = recognizer.predict(gray[y:y + h, x:x + w])
            if confidence < 70:
                name = get_user_name(face_id)
                insert_or_skip(face_id, name)
                label = f"{name} ({round(100 - confidence)}%)"
            else:
                label = "Unknown"

            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, label, (x + 5, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow('Attendance System (Press Q to quit)', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

# --- Load and Export Attendance Data ---
def load_data():
    with sqlite3.connect("attendance.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attendance WHERE date = date('now')")
        rows = cursor.fetchall()

    for i in tree.get_children():
        tree.delete(i)
    for row in rows:
        tree.insert("", tk.END, values=row)

def export_to_excel():
    with sqlite3.connect("attendance.db") as conn:
        df = pd.read_sql_query("SELECT * FROM attendance", conn)
    df.to_excel("attendance_report.xlsx", index=False)
    messagebox.showinfo("Exported", "Attendance exported to attendance_report.xlsx")

# --- GUI Setup ---
root = tk.Tk()
root.title("Smart Attendance System - Faculty Dashboard")
root.geometry("800x600")

# Face Registration Section
reg_frame = tk.LabelFrame(root, text="Face Registration", padx=10, pady=10)
reg_frame.pack(pady=10, fill="x")

tk.Label(reg_frame, text="User ID:").grid(row=0, column=0, padx=10)
entry_id = tk.Entry(reg_frame)
entry_id.grid(row=0, column=1, padx=10)

tk.Label(reg_frame, text="Name:").grid(row=0, column=2, padx=10)
entry_name = tk.Entry(reg_frame)
entry_name.grid(row=0, column=3, padx=10)

tk.Button(reg_frame, text="Register Face", command=register_face, bg="green", fg="white").grid(row=0, column=4, padx=10)

# Control Buttons
control_frame = tk.Frame(root)
control_frame.pack(pady=10)

tk.Button(control_frame, text="Train Model", command=train_model).grid(row=0, column=0, padx=10)
tk.Button(control_frame, text="Start Attendance", command=start_attendance).grid(row=0, column=1, padx=10)
tk.Button(control_frame, text="Load Today's Records", command=load_data).grid(row=0, column=2, padx=10)
tk.Button(control_frame, text="Export to Excel", command=export_to_excel).grid(row=0, column=3, padx=10)

# Attendance Records Table
tree = ttk.Treeview(root, columns=("ID", "Name", "Date", "Time"), show="headings", height=15)
for col in ("ID", "Name", "Date", "Time"):
    tree.heading(col, text=col)
    tree.column(col, width=100)
tree.pack(pady=10)

root.mainloop()
