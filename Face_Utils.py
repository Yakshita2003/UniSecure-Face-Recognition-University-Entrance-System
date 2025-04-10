import sqlite3
import numpy as np
import io
from PIL import Image
import face_recognition
import pickle 
import os
import cv2
import streamlit as st
import db

# Delete encodings
def del_encodings():
    with open('face_encodings.pkl', 'wb') as f:
        pickle.dump(([], []), f)

# Save & Load encodings
def save_encodings(encodings, names):
    with open("face_encodings.pkl", "wb") as f:
        pickle.dump((encodings, names), f)

def load_encodings():
    if os.path.exists("face_encodings.pkl"):
        with open("face_encodings.pkl", "rb") as f:
            data = pickle.load(f)
            if isinstance(data, tuple) and len(data) == 2:
                return data
    return [], []

registered_face_encodings, registered_face_names = load_encodings()

# Recognition page
def recognize(Utype):
    with st.container():
        c1, c2 = st.columns([1.5,2])
        with c1:
            image_file = st.camera_input(f"{Utype} face")
        with c2:
            if image_file:
                image = Image.open(image_file)
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                recognize_frame(opencv_image, Utype)

# Recognize single image frame
def recognize_frame(frame, Utype):
    load_face_encodings_from_db(Utype)
    registered_face_encodings, registered_face_names = load_encodings()

    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    detected_faces = []

    name = "No Face Detected"
    status = "No Access Attempt"

    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        face_distances = face_recognition.face_distance(registered_face_encodings, face_encoding)
        if len(face_distances) == 0:
            continue

        best_match_index = np.argmin(face_distances)
        match_score = face_distances[best_match_index]

        if match_score < 0.5:
            matched_person = registered_face_names[best_match_index]
            name = matched_person['name']
            status = "Access Granted"
            color = (0, 255, 0)
        else:
            name = "Unknown"
            status = "Access Denied"
            color = (0, 0, 255)

        cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), color, 2)
        cv2.putText(frame, name, (left*2, top*2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        detected_faces.append(f"**{name} ({status})**")
    # ⬇️ Split into two columns
    col1, col2 = st.columns([1.8,1])

    with col1:
        st.write("Result")
        st.image(frame, channels="BGR")

    with col2:
        if detected_faces:
            st.markdown("### Detected:")
            st.markdown("\n\n".join(detected_faces))
        else:
            st.warning("⚠️ No recognizable face found.")

        res = db.save_log((Utype, name, status))
        if res:
            st.success("Log Saved Successfully")
        else:
            st.error("Something went wrong")

def load_face_encodings_from_db(Utype):
    conn = sqlite3.connect("UniSecure.db", check_same_thread=False)
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT name, photo FROM {Utype}")
        rows = cursor.fetchall()

        encodings = []
        names = []

        for name, photo_blob in rows:
            photo_bytes = io.BytesIO(photo_blob)
            image = face_recognition.load_image_file(photo_bytes)
            encoding = face_recognition.face_encodings(image)

            if encoding:
                encodings.append(encoding[0])
                names.append({'name': name})
            else:
                print(f"⚠️ No face found in photo for {name}")

        save_encodings(encodings, names)
        return True

    except Exception as e:
        print(f"❌ Error loading encodings from DB: {e}")
        return False