import io
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import requests as r
import db
from PIL import Image
import cv2
from Face_Utils import recognize,del_encodings
from Gmail import main

st.set_page_config(page_title="Student Portal", layout="wide")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Go To Home Page",type="primary"):
    del_encodings()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("Home.py")

# Function to load a Lottie animation from a URL
def load_lottie_url(url):
    try:
        r1 = r.get(url)        
        if r1.status_code != 200:
            return None
        return r1.json()  
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
        return None

# Function to display the Home Page
def home():
    # Displaying Lottie animation and Welcome text in columns
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            lottie_url1 = "https://lottie.host/fcc9ddd4-e8fd-411e-ae84-a2329d2a7018/7fKNQdFyKu.json"
            lottie_json1 = load_lottie_url(lottie_url1)
            if lottie_json1:
                st_lottie(lottie_json1, speed=1, height=200, quality="high", key="lottie1")
            else:
                st.error("Failed to load Lottie animation.")
        with c2:
            st.markdown("""
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 10px; text-align: center;">
                <h2 style="color: #333;">Welcome to the Student Portal of UniSecure!</h2>
            </div>
            """, unsafe_allow_html=True)

# Function for student registration
def register():
    st.header("Registration Page")
    with st.form("Student Registration Form"):
        c1,c2=st.columns(2)
        with c1:
            Name = st.text_input("Name")
            Roll = st.number_input("StuID/R_No", min_value=1, step=1)
            Gmail = st.text_input("Gmail")
            Course = st.selectbox("Course", options=["B.Tech", "M.Tech"])
            Stream = st.selectbox("Stream", options=["ENC", "ECE", "CSE"])
            Year = st.selectbox("Year", options=[1, 2, 3, 4])
        with c2:
            Image_file = st.camera_input("Image")
            password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Register",type="primary")

    if submit:
        if not Name or not Roll or not Gmail or not Course or not Stream or not Year or not Image_file or not password:
            st.error("Please fill the form correctly")
        else:
            image = Image.open(Image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()
            data = (Name, Roll, Gmail, Course, Stream, Year, img_data, password)
            db.stu_reg(data)
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            if ret:
                image = frame
            else:
                image = None

# Function to view student data
def view():
    st.header("View Student Details")
    with st.form("Login Form"):
        Gmail = st.text_input("Gmail")
        Roll = st.number_input("StuID/R_No", min_value=1, step=1)
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("View",type="primary")

    if submit:
        if not Gmail or not Roll or not password:
            st.error("Please fill the form correctly")
        else:
            data = (str.lower(Gmail), Roll, password)
            student = db.stu_view(data)
            if student:
                st.success("Student Found!")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"**Name**: {student[1]}")
                    st.write(f"**Roll No**: {student[2]}")
                    st.write(f"**Email**: {student[3]}")
                    st.write(f"**Course**: {student[4]}")
                    st.write(f"**Stream**: {student[5]}")
                    st.write(f"**Year**: {student[6]}")
                with c2:
                    if student[7]:
                        st.image(Image.open(io.BytesIO(student[7])), caption="Student Photo", use_container_width=True)
                    else:
                        st.warning("No image available for this student.")  
            else:
                st.error("Invalid login credentials.")

def login_form():
        with st.form("Login Form"):
            G = st.text_input("Gmail")
            R = st.number_input("StudentID(13 Digit)/Roll_No(11 Digit)", min_value=1, step=1)
            p = st.text_input("Password", type="password")
            submit = st.form_submit_button("Submit", type="primary")

        if submit:
            if not G or not R or not p:
                st.error("Please fill the form correctly")
                return None
            data = (R, str.lower(G), p)
            res = db.s_readone(data)
            if res:
                st.success("Student Found Successfully.")
                return res
            else:
                st.error("Invalid Credentials!")
                return None
        return None

def show_update_form(res):
        st.subheader("Update Student Details")

        with st.form("Updation Form"):
            c1, c2 = st.columns([1.5, 1])
            with c1:
                Name = st.text_input("Name", value=res[1])
                Roll = st.number_input("StudentID(13 Digit)/Roll_No(11 Digit)", min_value=1, step=1, value=res[2])
                Gmail = st.text_input("Gmail", value=res[3])
                Course = st.selectbox("Course", ["B.Tech", "M.Tech"], index=["B.Tech", "M.Tech"].index(res[4]))
                Stream = st.selectbox("Stream", ["ENC", "ECE", "CSE"], index=["ENC", "ECE", "CSE"].index(res[5]))
                Year = st.selectbox("Year", [1, 2, 3, 4], index=[1, 2, 3, 4].index(res[6]))
                password_input = st.text_input("Password", type="password", value=res[8])
            with c2:
                if res[7]:
                    st.image(res[7], caption="Current Image", use_container_width=True)
                Image_file = st.camera_input("Capture New Image")

            submit_update = st.form_submit_button("Update", type="primary")

        if submit_update:
            if not Name or not Roll or not Gmail or not Course or not Stream or not Year or not password_input:
                st.error("Please fill all fields before updating.")
            else:
                if Image_file:
                    image = Image.open(Image_file)
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_data = img_byte_arr.getvalue()
                else:
                    img_data = res[7]

                result = db.stu_update((
                    Name, Roll, Gmail, Course, Stream, Year, img_data, password_input,
                    res[2], res[3], res[8]  # old Roll, Gmail, Password
                ))

                if result:
                    st.success("Student details updated successfully!")
                    st.session_state.authenticated = False
                    st.session_state.student_data = None
                else:
                    st.error("Something went wrong during update.")

# Function to update student data
def update():
        st.header("Update Student Details")

        # Initialize session
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "student_data" not in st.session_state:
            st.session_state.student_data = None

        # LOGIN
        if not st.session_state.authenticated:
            res = login_form()
            if res:
                st.session_state.authenticated = True
                st.session_state.student_data = res
        
        # UPDATE FORM
        if st.session_state.authenticated and st.session_state.student_data:
            if st.button("Logout",type="primary"):
                st.session_state.authenticated = False
                st.session_state.student_data = None
                st.experimental_rerun()
            show_update_form(st.session_state.student_data)
 
Utype="Student"
# Sidebar menu for navigation
selected = option_menu(None, ["Home", "Register", "User Verification","View Data", "Update Data"], 
                       icons=["house", "person-plus","camera","table", "pencil"], 
                       menu_icon="cast", default_index=0, orientation="horizontal")

if selected == "Home":
    home()
elif selected == "Register":
    register()
elif selected=="User Verification":
    st.header("User Verification")
    Vtype=st.selectbox("Verification type",options=["Face recognition","Email OTP"])
    if Vtype=="Email OTP":
        Vtype="Email OTP"
        main(Utype,Vtype)
    if Vtype=="Face recognition":
        Vtype="Face Recognition"
        recognize(Utype,Vtype)
elif selected == "View Data":
    view()
elif selected == "Update Data":
    update()

