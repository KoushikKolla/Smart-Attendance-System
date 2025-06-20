import tkinter as tk
from tkinter import messagebox
import cv2
import sqlite3
from datetime import datetime

def get_user_name(user_id):
    conn = sqlite3.connect("attendance.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE id=?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else "Unknown"

def insert_or_skip(user_id, name):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER, name TEXT, date TEXT, time TEXT)''')
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")
    c.execute("SELECT * FROM attendance WHERE id=? AND date=?", (user_id, date))
    if c.fetchone() is None:
        c.execute("INSERT INTO attendance VALUES (?, ?, ?, ?)", (user_id, name, date, time))
        conn.commit()
    conn.close()

def mark_attendance():
    try:
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trainer/trainer.yml")
    except:
        messagebox.showerror("Model Missing", "Trainer model not found.")
        return

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

            cv2.rectangle(img, (x, y), (x+w, y+h), (0,255,0), 2)
            cv2.putText(img, label, (x+5, y-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)

        cv2.imshow("Student Attendance - Press Q to quit", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

# GUI for students
root = tk.Tk()
root.title("Student Dashboard")
tk.Label(root, text="Welcome Student!").pack(pady=10)
tk.Button(root, text="Mark Attendance", command=mark_attendance, bg="green", fg="white").pack(pady=20)
root.mainloop()
