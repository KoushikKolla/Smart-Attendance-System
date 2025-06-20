import tkinter as tk
from tkinter import messagebox
import cv2
import os
import sqlite3

# Create dataset folder if not exists
os.makedirs("dataset", exist_ok=True)

# Save user info into SQLite users table
def save_user_to_db(user_id, name):
    conn = sqlite3.connect("attendance.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT NOT NULL)")
    c.execute("INSERT OR REPLACE INTO users (id, name) VALUES (?, ?)", (user_id, name))
    conn.commit()
    conn.close()

# Register face and collect images
def register_face():
    try:
        user_id = int(entry_id.get())
        name = entry_name.get().strip()

        if not name:
            messagebox.showwarning("Input Error", "Please enter a valid name.")
            return

        save_user_to_db(user_id, name)
        messagebox.showinfo("Saved", f"User {name} added to database. Starting camera...")

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        cam = cv2.VideoCapture(0)
        sample_count = 0

        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                sample_count += 1
                cv2.imwrite(f"dataset/User.{user_id}.{sample_count}.jpg", gray[y:y+h, x:x+w])
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.putText(img, f"Samples: {sample_count}/30", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2)

            cv2.imshow('Registering Face - Press Q to Quit', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            elif sample_count >= 30:
                break

        cam.release()
        cv2.destroyAllWindows()
        messagebox.showinfo("Done", f"Face registration completed for {name}.")

    except ValueError:
        messagebox.showerror("Input Error", "ID must be a number.")

# GUI Setup
root = tk.Tk()
root.title("Face Registration")
root.geometry("350x200")

tk.Label(root, text="Enter Numeric ID:").pack(pady=5)
entry_id = tk.Entry(root)
entry_id.pack()

tk.Label(root, text="Enter Name:").pack(pady=5)
entry_name = tk.Entry(root)
entry_name.pack()

tk.Button(root, text="Register Face", command=register_face, bg="green", fg="white").pack(pady=20)

root.mainloop()
