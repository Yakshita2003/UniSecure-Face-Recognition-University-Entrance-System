#🎓 UniSecure – Face Recognition University Entrance System
UniSecure is a smart and secure facial recognition-based access control system for universities. It provides seamless, role-based entrance and verification for students, faculty/staff, admins, and visitors through real-time webcam-based face recognition and centralized database logging.

##🌟 Key Features
🔐 Face Recognition-Based Authentication for all user types
📸 Live Webcam Capture using Streamlit’s st.camera_input
👤 Role-Based Interfaces for Admin, Student, Faculty/Staff & Visitor
🗃️ Secure Registration & Update with real-time image encoding
📊 Admin Dashboard for viewing user data and access logs
📁 Modular Page Navigation using st.switch_page
📈 Access Log System for every face match attempt
💾 Local SQLite3 Storage with BLOB image saving

##🛠️ Tech Stack
UI/Frontend: Streamlit
Backend	: Python
Database: SQLite3
Facial Recognition: face_recognition + OpenCV
Image Handling: PIL (Pillow)
UI Enhancements:	Lottie, Streamlit Option Menu

##🧩 Project Structure
├── Home.py               # Main entry UI with page navigation
├── Face_Utils.py         # Shared facial encoding and recognition logic
├── db.py                 # All database connection and operations
├── face_encodings.pkl    # Pickled encodings file
└── pages/
    ├── Admin.py          # Admin login, register, view users/logs
    ├── Student.py        # Student register, view, update, recognize
    ├── Faculty.py        # Faculty/staff portal: register, recognize, update
    └── Visitor.py        # Visitor face recognition (no registration UI)

##🧭 Navigation Flow
The project uses st.switch_page() to route users to respective role-specific pages:
🎓 Students can register, update details, and use face recognition.
👩‍🏫 Faculty/Staff have a similar experience with designations.
🧑‍💼 Admins can register, log in, and manage all user data + logs.
🚶 Visitors can directly verify via facial recognition (no registration UI).

##📝 How Face Recognition Works
Users capture live images using webcam (st.camera_input)
Faces are encoded using the face_recognition library
Matches are made against existing encodings stored in face_encodings.pkl
Access is either granted or denied
All events are logged in the Log table with timestamp and status

##📄 Database Overview
The SQLite database (UniSecure.db) includes:
Admin: Username, Gmail, Contact, Image, Password
Student: Name, Roll_No, Gmail, Course, Stream, Year, Photo, Password
Faculty: Name, Gmail, Designation, Photo, Password
Visitor: Name, Contact, ID_type, ID_no, Purpose, Photo
Log: Verification_Type, Usertype, Username, Status, Timestamp
