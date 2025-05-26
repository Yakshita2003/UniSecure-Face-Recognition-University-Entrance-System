import io
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import requests as r
import db
from PIL import Image
from Face_Utils import recognize,del_encodings
from Gmail import main

st.set_page_config("Faculty Portal",layout="wide")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Go To Home Page", type="primary"):
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
    except Exception:
        return None

# Function to display the Home Page
def home():
    with st.container():
        c1, c2 = st.columns([1, 2])
        with c1:
            lottie_url1 = "https://lottie.host/a932f1db-3351-46db-86ce-f1a2608859f8/sNianoQs1C.json"
            lottie_json1 = load_lottie_url(lottie_url1)
            if lottie_json1:
                st_lottie(lottie_json1, speed=1, height=200, quality="high", key="lottie1")
            else:
                st.image("pages/portrait-young-male-professor-education-day.png",use_container_width=True)
        with c2:
            st.subheader("Welcome to the Faculty Portal")
            st.write("This portal allows you to register, view visitor records, and perform face recognition for security.")

# Function for Faculty registration
def register():
    st.header("Registration Page")
    with st.form("Registration Form"):
        c1, c2 = st.columns(2)
        with c1:
            Name = st.text_input("Name")
            Gmail = st.text_input("Gmail")
            Designation = st.text_input("Designation")
            Password = st.text_input("Password", type="password")
        with c2:
            Image_file = st.camera_input("Image")
        submit = st.form_submit_button("Submit",type="primary")

    if submit:
        if not Name or not Gmail or not Designation or not Image_file or not Password:
            st.error("Please fill the form correctly")
        else:
            image = Image.open(Image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()
            data = (Name, str.lower(Gmail), Designation, img_data, Password)
            db.FS_reg(data)

# Function to view Faculty data
def view():
    st.header("View Faculty Details")
    with st.form("Login Form"):
        Gmail = st.text_input("Gmail")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("View",type="primary")
    
    if submit :
        if not Gmail or not password:
            st.error("Please fill the form correctly")
        else:
            data = (str.lower(Gmail), password)
            Faculty = db.FS_view(data)
            if Faculty:
                st.success("Faculty Found!")
                c1, c2 = st.columns(2)
                with c1:
                    st.write(f"Name: {Faculty[1]}")
                    st.write(f"Gmail: {Faculty[2]}")
                    st.write(f"Designation: {Faculty[3]}")
                    st.write(f"Password: {Faculty[5]}")
                with c2:
                    if Faculty[4]:
                        st.image(Image.open(io.BytesIO(Faculty[4])), caption="Faculty Photo", use_container_width=True)
                    else:
                        st.warning("No image available for this Faculty.")  
            else:
                st.error("Invalid login credentials.")

# ---------- Faculty Login Form ----------
def faculty_login_form():
    with st.form("Faculty Login Form"):
        G = st.text_input("Gmail")
        p = st.text_input("Password", type="password")
        submit = st.form_submit_button("Submit", type="primary")

    if submit:
        if not G or not p:
            st.error("Please fill the form correctly")
            return None
        res = db.f_readone((G, p))
        if res:
            st.success("Faculty Found Successfully.")
            return res
        else:
            st.error("Invalid Credentials!")
            return None
    return None

# ---------- Show Faculty Update Form ----------
def show_faculty_update_form(res):
    st.subheader("Update Faculty Details")

    with st.form("Faculty Update Form"):
        c1, c2,c3= st.columns([1, 1,1])
        with c1:
            Name = st.text_input("Name", value=res[1])
            Gmail = st.text_input("Gmail", value=res[2])
            Designation = st.text_input("Designation", value=res[3])
            Password = st.text_input("Password", type="password", value=res[5])
        with c2:
            if res[4]:
                st.image(res[4], caption="Current Image", use_container_width=True)
        with c3:
            Image_file = st.camera_input("Capture New Image")

        submit_update = st.form_submit_button("Update", type="primary")

    if submit_update:
        if not Name or not Gmail or not Designation or not Password:
            st.error("Please fill all fields before updating.")
        else:
            if Image_file:
                image = Image.open(Image_file)
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='PNG')
                img_data = img_byte_arr.getvalue()
            else:
                img_data = res[4]

            result = db.f_update((
            Name, str.lower(Gmail), Designation, img_data, Password,
            res[2], res[5]  # old Gmail, old Password
            ))  

            if result:
                st.success("Faculty details updated successfully!")
                st.session_state.faculty_authenticated = False
                st.session_state.faculty_data = None
            else:
                st.error("Something went wrong during update.")

# ---------- Main Faculty Update Controller ----------
def update():
    st.header("Update Faculty Details")

    if "faculty_authenticated" not in st.session_state:
        st.session_state.faculty_authenticated = False
    if "faculty_data" not in st.session_state:
        st.session_state.faculty_data = None

    # LOGIN
    if not st.session_state.faculty_authenticated:
        res = faculty_login_form()
        if res:
            st.session_state.faculty_authenticated = True
            st.session_state.faculty_data = res

    # UPDATE FORM
    if st.session_state.faculty_authenticated and st.session_state.faculty_data:
        if st.button("Logout", type="primary"):
            st.session_state.faculty_authenticated = False
            st.session_state.faculty_data = None
            st.rerun()
        show_faculty_update_form(st.session_state.faculty_data)

Utype="Faculty"
# Horizontal menu for navigation
selected = option_menu(None, ["Home", "Register", "User Verification","View Data", "Update Data"], 
                       icons=["house", "person-plus", "camera","table", "pencil"], 
                       menu_icon="cast", default_index=0, orientation="horizontal")

if selected == "Home":
    home()
elif selected == "Register":
    register()
elif selected=="User Verification":
    st.header("Faculty Verification")
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

