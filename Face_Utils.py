import sqlite3  # Used to connect to and interact with SQLite database
import numpy as np  # For numerical operations, especially arrays
import io  # To handle binary streams (like image BLOBs from DB)
from PIL import Image  # Python Imaging Library, used to load/process images
import face_recognition  # Face detection and recognition library
import pickle  # To save and load Python objects (encodings) to a file
import os  # To interact with the operating system, like checking if file exists
import cv2  # OpenCV for image processing (drawing boxes, color conversion, etc.)
import streamlit as st  # Web interface and UI rendering
import db  # Custom module to interact with the application's database

# Delete all stored face encodings from the .pkl file
def del_encodings():
    with open('face_encodings.pkl', 'wb') as f:  # Open in write-binary mode
        pickle.dump(([], []), f)  # Save empty lists (clears encodings and names)

# Save new face encodings and names into .pkl file
def save_encodings(encodings, names):
    with open("face_encodings.pkl", "wb") as f:  # Open in write-binary mode
        pickle.dump((encodings, names), f)  # Save both encodings and names as a tuple

# Load face encodings and names from the .pkl file
def load_encodings():
    if os.path.exists("face_encodings.pkl"):  # Check if the file exists
        with open("face_encodings.pkl", "rb") as f:  # Open in read-binary mode
            data = pickle.load(f)  # Load the saved tuple
            if isinstance(data, tuple) and len(data) == 2:  # Ensure it's valid
                return data  # Return encodings and names
    return [], []  # If file doesn't exist or is invalid, return empty lists

def recognize(Utype, Vtype):
    # Initialize step-based session state for face recognition
    if "face_step" not in st.session_state:
        st.session_state.face_step = 1
    if "face_verified" not in st.session_state:
        st.session_state.face_verified = False
    if "Face-recognition_logged_out" not in st.session_state:
        st.session_state["Face-recognition_logged_out"] = True

    # Logout button
    if st.button("Logout", type="primary"):
        for key in ["face_step", "face_verified", "Face-recognition_logged_out"]:
            if key in st.session_state:
                st.session_state[key] = False if "verified" in key else True
        st.info("ℹ️ You have been logged out.")
        st.rerun()

    st.subheader("🎥 Live Face Recognition")

    if st.session_state.face_step == 1:
        st.info("🔒 Please capture your image for verification.")
        c1,c2=st.columns(2)
        with c1:
            image_file = st.camera_input(f"{Utype} face")

            if image_file:
                st.session_state.face_image = image_file
                st.session_state.face_step = 2
                st.rerun()
        with c2: 
            print('')
        
    elif st.session_state.face_step == 2:
        if "face_image" in st.session_state:
            st.info("🔍 Verifying your face...")
            image = Image.open(st.session_state.face_image)
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            recognize_frame(opencv_image, Utype, Vtype)

            st.session_state.face_verified = True
            if st.session_state.face_verified:
                st.success("✅ Face verified successfully!")
            else:
                st.error("❌ Face verification failed.")
                st.session_state.face_step = 1  # Optionally loop back
                st.session_state.face_step = 3
                st.rerun()
        else:
            st.warning("⚠️ No image found. Please capture again.")
            st.session_state.face_step = 1
            st.rerun()

# Load all face encodings for a given user type from SQLite DB
def load_face_encodings_from_db(Utype):
    conn = sqlite3.connect("UniSecure.db", check_same_thread=False)  # Connect to DB
    cursor = conn.cursor()
    try:
        if Utype=="Admin":
            cursor.execute(f"SELECT Username, Image FROM Admin")  # Query name and photo blob
            rows=cursor.fetchall()
        else:
            cursor.execute(f"SELECT Name, Photo FROM {Utype}")  # Query name and photo blob
            rows = cursor.fetchall()  # Fetch all results

        encodings = []  # Store encodings
        names = []  # Store names

        for name, photo_blob in rows:
            photo_bytes = io.BytesIO(photo_blob)  # Convert BLOB to byte stream
            image = face_recognition.load_image_file(photo_bytes)  # Load image into numpy array
            encoding = face_recognition.face_encodings(image)  # Extract face encodings

            if encoding:  # If a face was found
                encodings.append(encoding[0])  # Save first (and only) face encoding
                names.append({'name': name})  # Save name in dict format
            else:
                print(f"⚠️ No face found in photo for {name}")  # Warn if image was invalid

        save_encodings(encodings, names)  # Save all encodings to local file
        return True

    except Exception as e:
        print(f"❌ Error loading encodings from DB: {e}")  # Log any error
        return False

# Perform recognition on a single image frame
def recognize_frame(frame, Utype, Vtype):
    load_face_encodings_from_db(Utype)  # Load encodings from DB for this user type
    registered_face_encodings, registered_face_names = load_encodings()  # Reload them after updating

    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)  # Resize for faster processing
    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB for face_recognition

    face_locations = face_recognition.face_locations(rgb_small_frame)  # Detect face locations
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)  # Get encodings of each face
    detected_faces = []  # Store detected face info

    name = "No Face Detected"  # Default name
    status = "No Access Attempt"  # Default access status

    # Compare each detected face to registered faces
    for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
        face_distances = face_recognition.face_distance(registered_face_encodings, face_encoding)  # Compare to known encodings
        if len(face_distances) == 0:
            continue  # Skip if no registered faces

        best_match_index = np.argmin(face_distances)  # Get the best match index
        match_score = face_distances[best_match_index]  # Get distance score

        if match_score < 0.5:  # If similarity is strong (low distance)
            matched_person = registered_face_names[best_match_index]  # Get matched name
            name = matched_person['name']
            status = "Access Granted"
            color = (0, 255, 0)  # Green box
        else:
            name = "Unknown"
            status = "Access Denied"
            color = (0, 0, 255)  # Red box

        # Draw rectangle and name label on image (scaled back up by 2x)
        cv2.rectangle(frame, (left*2, top*2), (right*2, bottom*2), color, 2)
        cv2.putText(frame, name, (left*2, top*2 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        detected_faces.append(f"**{name} ({status})**")  # Append results for display

    # Split screen into image and result column
    col1, col2 = st.columns([1.8,1])
    with col1:
        st.write("Result")
        st.image(frame, channels="BGR")  # Display annotated image

    with col2:
        if detected_faces:
            st.markdown("### Detected:")
            st.markdown("\n\n".join(detected_faces))  # Show who was detected
        else:
            st.warning("⚠️ No recognizable face found.")  # If no faces matched

        res = db.save_log((Utype, name, Vtype, status))  # Save log to DB
        if res:
            st.success("Log Saved Successfully")
        else:
            st.error("Something went wrong")  # Handle DB save error


def admin_recognize(image, Uname, Vtype="Face Recognition"):
    # Load encodings from database
    load_face_encodings_from_db("Admin")  # Only Admins
    registered_face_encodings, registered_face_names = load_encodings()

    # Detect and compare face
    try:
        img = Image.open(image)
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_encodings = face_recognition.face_encodings(rgb_small_frame)
        face_locations = face_recognition.face_locations(rgb_small_frame)

        name = "No Face Detected"
        status = "No Access Attempt"
        match_found = False

        for face_encoding, (top, right, bottom, left) in zip(face_encodings, face_locations):
            face_distances = face_recognition.face_distance(registered_face_encodings, face_encoding)
            if len(face_distances) == 0:
                continue

            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] < 0.5:
                matched_person = registered_face_names[best_match_index]
                if matched_person['name'].lower() == Uname.lower():
                    match_found = True
                    name = matched_person['name']
                    status = "Access Granted"
                    break  # Exit loop on successful match
            else:
                name = "Unknown"
                status = "Access Denied"

        result = db.save_log(("Admin", name, Vtype, status))
        if result:
            st.success("Log saved successfully.")
        else:
            st.error("⚠️ Failed to save log.")

        if match_found:
            st.session_state["admin_logged_in"] = True
            st.session_state["admin_name"] = Uname
            st.success(f"Welcome, {Uname}! You are now logged in.")
            st.rerun()
        else:
            st.error("Face not recognized or does not match username.")

    except Exception as e:
        st.error(f"An error occurred during face recognition: {e}")  
          
