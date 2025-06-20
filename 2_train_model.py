import cv2
import numpy as np
from PIL import Image
import os

# Initialize recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Path to face image dataset
path = 'dataset'

def get_images_and_labels(path):
    # List all image paths in dataset folder
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.jpg') or f.endswith('.png')]
    face_samples = []
    ids = []

    for image_path in image_paths:
        try:
            # Convert image to grayscale
            gray_img = Image.open(image_path).convert('L')
            img_numpy = np.array(gray_img, 'uint8')

            # Extract user ID from filename
            # Format expected: User.ID.Sample.jpg
            user_id = int(os.path.split(image_path)[-1].split(".")[1])

            # Detect face from image
            faces = cv2.CascadeClassifier(
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            ).detectMultiScale(img_numpy)

            # Crop and collect each face
            for (x, y, w, h) in faces:
                face_samples.append(img_numpy[y:y+h, x:x+w])
                ids.append(user_id)

        except Exception as e:
            print(f"❌ Skipping file {image_path} due to error: {e}")

    return face_samples, ids

# Get face samples and corresponding IDs
print("[INFO] Fetching face data from dataset...")
faces, ids = get_images_and_labels(path)

if not faces:
    print("❌ No valid face data found in dataset. Please register at least one face first.")
    exit()

# Train model
print("[INFO] Training model...")
recognizer.train(faces, np.array(ids))

# Save trained model
os.makedirs("trainer", exist_ok=True)
recognizer.write('trainer/trainer.yml')
print("✅ Model trained successfully and saved to trainer/trainer.yml")

