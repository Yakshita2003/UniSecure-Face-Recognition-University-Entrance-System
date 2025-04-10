# Import required libraries
import streamlit as st
import db
import requests as r
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from PIL import Image
import io
import pandas as pd

st.set_page_config(page_title="Admin Portal", layout="wide")

button = st.button("Go to Home Page",type="primary")
if button:
    st.switch_page("Home.py")

st.title("Admin Page")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Ensure session state is initialized
if "admin_logged_in" not in st.session_state:
    st.session_state["admin_logged_in"] = False
if "admin_name" not in st.session_state:
    st.session_state["admin_name"] = ""

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

# Admin Login Function
def login():
    st.subheader("Admin Login")

    with st.form("Login Form"):
        Uname = st.text_input("Username")  # Admin's name
        Gmail = st.text_input("Gmail")  # Admin's Gmail
        Password = st.text_input("Password", type="password")  # Password
        submit = st.form_submit_button("Login",type="primary")  # Submit button

    if submit:
        if not Uname or not Gmail or not Password:
            st.error("Please fill the form correctly")
        else:
            # Fetch user details from database
            data=(Uname,Gmail,Password)
            admin_data = db.get_admin(data)  # Function to get admin details

            if admin_data:
                st.session_state["admin_logged_in"] = True
                st.session_state["admin_name"] = Uname  # Store admin name
                st.success(f"Welcome, {Uname}! You are now logged in.")
                st.rerun()  # Refresh page after login
            else:
                st.error("Invalid credentials")

# Function to display the Home Page
def home():
    st.subheader("Admin Dashboard")

    # Create a two-column layout
    col1, col2 = st.columns([1, 1])  # Adjust ratio if needed

    with col1:
        # Display Welcome Message
        st.markdown(
        """
        <div style="padding:20px; background-color:#f0f2f6; border-radius:10px;">
            <h2 style="color:#333;">Welcome, {}</h2>
            <p style="font-size:18px; color:#555;">
                You are now logged in as an Admin. Manage users, view records, 
                and access all system functionalities from here.
            </p>
        </div>
        """.format(st.session_state['admin_name']), unsafe_allow_html=True)

    with col2:
        # Displaying Lottie animation
        lottie_url1 = "https://lottie.host/7651f757-a336-4cfe-9863-b38ae1739f80/dokgtnmCa9.json"
        lottie_json1 = load_lottie_url(lottie_url1)
        
        if lottie_json1:
            st_lottie(lottie_json1, speed=1, height=200, quality="high", key="lottie1")
        else:
            st.error("Failed to load Lottie animation.")

# Function for Admin registration
def register():
    st.header("Admin Registration")

    with st.form("Registration Form"):
        c1,c2=st.columns(2)
        with c1:
            Uname = st.text_input("Name")  # Admin's name
            Gmail = st.text_input("Gmail")  # Admin's Gmail
            Contact = st.text_input("Contact (10-digit Number)")  # Admin's Phone
            Password = st.text_input("Password", type="password")  # Password
        with c2:
            Image_file = st.camera_input("Image")  # Capture Admin's image
        submit = st.form_submit_button("Submit")  # Submit button

    if submit:
        # Check if any field is empty
        if len(Contact) != 10 or not Contact.isdigit():
            st.error("Please enter a valid 10-digit contact number.")
        elif not Uname or not Gmail or not Contact or not Image_file or not Password:
            st.error("Please fill the form correctly")
        else:
            # Convert the captured image into binary format for database storage
            image = Image.open(Image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()

            # Prepare data tuple for database insertion
            data = (Uname, Gmail, Contact, img_data, Password)
            
            # Call database function to store Admin information
            db.A_reg(data)
            st.success("Admin registered successfully!")

# Function to view database records
def view():
    st.header("View Databases")

    # **User Type Selection in Form Format**
    with st.container(border=True):
        Utype = st.selectbox("User Type", options=["Student", "Faculty", "Visitor", "Admin","Log"])
    
    res = db.view(Utype)  # Fetch records from DB

    # Define column names based on user type
    if Utype == "Student":
        column = ["ID", "Name", "Roll_No", "Gmail", "Course", "Stream", "Year", "Photo", "Password"]
    elif Utype == "Faculty":
        column = ["ID", "Name", "Gmail", "Designation", "Photo", "Password"]
    elif Utype == "Visitor":
        column = ["ID", "Name", "Contact", "ID_type", "ID_no", "Purpose", "Photo"]
    elif Utype == "Admin":
        column = ["ID", "Username", "Gmail", "Contact", "Photo", "Password"]
    elif Utype=="Log":
        column= ["ID","Usertype", "Username", "Status", "Timestamp"]
    df = pd.DataFrame(res, columns=column)

    photos=[]
    # Separate image column
    if "Photo" in df.columns:
        photos = df["Photo"].tolist()
        df.drop(columns=["Photo"], inplace=True)  # Remove from displayed dataframe

    # **Filter Section**
    search_name = st.text_input("Search by Name or ID (Leave blank to see all):")
    submit = st.button("view",type="primary")
    if submit:
        if search_name:
            filtered_df = df[df.apply(lambda row: search_name.lower() in row.astype(str).str.lower().to_list(), axis=1)]
            filtered_photos = [photos[i] for i in filtered_df.index]  # Filter images too
        else:
            filtered_df = df  # Show full dataset
            filtered_photos = photos

        # **Display Data in Table Format**
        st.subheader("User Details")
        st.dataframe(filtered_df)

        # **Display Images**
        st.subheader("User Photos")
        cols = st.columns(3)  # Arrange images in columns
        for i, photo in enumerate(filtered_photos):
            if isinstance(photo, bytes):  # If stored as binary (BLOB)
                image = Image.open(io.BytesIO(photo))
            else:  # If stored as a file path
                image = Image.open(photo)

            cols[i % 3].image(image, caption=filtered_df.iloc[i, 1], width=100)  # Show image with name

# ✅ Create Horizontal Navigation Bar
selected_option = option_menu(
    menu_title=None,
    options=["Login"] if not st.session_state["admin_logged_in"] else ["Home", "Register", "View Databases", "Logout"],
    icons=["key"] if not st.session_state["admin_logged_in"] else ["house", "person-plus", "table", "box-arrow-right"],
    default_index=0,
    orientation="horizontal"
)

# ✅ Redirect based on selection
if selected_option == "Login":
    login()
elif st.session_state["admin_logged_in"]:
    if selected_option == "Home":
        home()
    elif selected_option == "Register":
        register()
    elif selected_option=="View Databases":
        view()
    elif selected_option == "Logout":
        st.session_state["admin_logged_in"] = False
        st.session_state["admin_name"] = ""
        st.rerun()
else:
    st.warning("Please log in as Admin to access this section.")
