# Import required libraries
import streamlit as st
import db
import requests as r
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from PIL import Image
import io
import pandas as pd
import utils as u
from Face_Utils import admin_recognize,del_encodings

st.set_page_config(page_title="Admin Portal", layout="wide")

button = st.button("Go To Home Page",type="primary")
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
    Method = st.selectbox("Login Type", options=["Face Recognition", "Login Form"])
    if Method == "Login Form":
        with st.form("Login Form"):
            Uname = st.text_input("Username") # Admin's name
            Gmail = st.text_input("Gmail")  # Admin's Gmail
            Password = st.text_input("Password", type="password")  # Password
            submit = st.form_submit_button("Login", type="primary")  # Submit button

        if submit:
            if not Uname or not Gmail or not Password:
                st.error("Please fill the form correctly")
            else:
                # Fetch user details from database
                data = (Password, str.lower(Gmail))
                admin_data = db.get_admin(data)  # Function to get admin details

                Usertype = "Admin"
                Vtype = "Login Form"
                Status = ""
                if admin_data:
                    Status = "Access Granted"
                    st.session_state["admin_logged_in"] = True
                    st.session_state["admin_name"] = Uname  # Store admin name
                    st.success(f"Welcome, {Uname}! You are now logged in.")
                    st.rerun()  # Refresh page after login
                else:
                    Status = "Access Denied"
                    st.error("Invalid credentials")

                result = db.save_log((Usertype, str.lower(Uname), Vtype, Status))
                if result:
                    st.success("Log saved successfully.")
                else:
                    st.error("⚠️ Failed to save log.")

    elif Method == "Face Recognition":
        with st.form("Login Credentials"):
            Uname = st.text_input("Username")
            c1, c2 = st.columns([1, 2])
            with c1:
                image = st.camera_input("Face Scan")
            with c2:
                print("")
            submit = st.form_submit_button("Login", type="primary")

        if submit:
            if not Uname or not image:
                st.error("Please fill the form correctly")
            else:
                admin_recognize(image, Uname.lower())

    del_encodings()

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
    st.subheader("Admin Registration")

    with st.form("Registration Form"):
        c1,c2=st.columns(2)
        with c1:
            Uname = st.text_input("Name")  # Admin's name
            Gmail = st.text_input("Gmail")  # Admin's Gmail
            Contact = st.text_input("Contact (10-digit Number)")  # Admin's Phone
            Password = st.text_input("Password", type="password")  # Password
        with c2:
            Image_file = st.camera_input("Image",)  # Capture Admin's image
        submit = st.form_submit_button("Register",type="primary")  # Submit button

    if submit:
        # Check if any field is empty
        if not Uname or not Gmail or not Contact or not Image_file or not Password:
            st.error("Please fill the all the form fields correctly")
        elif len(Contact) != 10 or not Contact.isdigit():
            st.error("Please enter a valid 10-digit contact number.")
        else:
            # Convert the captured image into binary format for database storage
            image = Image.open(Image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()

            # Prepare data tuple for database insertion
            data = (Uname.lower(), str.lower(Gmail), Contact, img_data, Password)
            
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
        column = ["ID", "Name", "Roll_No", "Gmail", "Course", "Stream", "Year", "Photo"]
    elif Utype == "Faculty":
        column = ["ID", "Name", "Gmail", "Designation", "Photo"]
    elif Utype == "Visitor":
        column = ["ID", "Name","Gmail", "Contact", "ID_type", "ID_no", "Purpose", "Photo"]
    elif Utype == "Admin":
        column = ["ID", "Username", "Gmail", "Contact", "Photo"]
    elif Utype=="Log":
        column= ["ID","Usertype", "Username","Verification Type", "Status", "Timestamp"]
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
            if Utype!="Log":
                filtered_photos = [photos[i] for i in filtered_df.index]  # Filter images too
        else:
            if Utype!="Log":
                filtered_df = df  # Show full dataset
                filtered_photos = photos
            else:
                filtered_df=df

        # **Display Data in Table Format**
        st.subheader("User Details")
        st.dataframe(filtered_df)

        # **Display Images**
        if Utype!="Log":
            st.subheader("User Photos")
            cols = st.columns(3)  # Arrange images in columns
            for i, photo in enumerate(filtered_photos):
                if isinstance(photo, bytes):  # If stored as binary (BLOB)
                    image = Image.open(io.BytesIO(photo))
                else:  # If stored as a file path
                    image = Image.open(photo)

                cols[i % 3].image(image, caption=filtered_df.iloc[i, 1], width=100)  # Show image with name

# --- Helper Functions ---
def admin_login_form():
    """Displays the admin login form."""
    with st.form("Admin Login Form"):
        Gmail = st.text_input("Gmail")  # Admin's Gmail
        Password = st.text_input("Password", type="password")  # Password
        submit = st.form_submit_button("Login", type="primary")  # Submit button

    if submit:
        if not Gmail or not Password:
            st.error("Please fill the form correctly")
            return None
        else:
            # Fetch user details from database
            data = (str.lower(Gmail), Password)
            admin_data = db.A_readone(data)  # Function to get admin details

            if admin_data:
                st.success(f"Welcome, {admin_data[1]}! You are now logged in.")  # Assuming admin name is at index 1
                return admin_data
            else:
                st.error("Invalid credentials")
                return None
    return None

def show_admin_update_form(admin_data):
    """Displays the admin update form."""
    st.subheader("Update Your Details")

    with st.form("Admin Update Form", clear_on_submit=True):
        c1, c2,c3 = st.columns(3)
        with c1:
            # Use get() method for safe access
            Uname = st.text_input("Name", value=admin_data[1] if isinstance(admin_data, tuple) else admin_data.get('Username', ''))
            Gmail = st.text_input("Gmail", value=admin_data[2] if isinstance(admin_data, tuple) else admin_data.get('Gmail', ''))
            Contact = st.text_input("Contact", value=admin_data[3] if isinstance(admin_data, tuple) else admin_data.get('Contact', ''))
            Password = st.text_input("New Password", type="password",value=admin_data[5] if isinstance(admin_data, tuple) else admin_data.get('Password', ''))  # Removed value=admin_data[5]
        with c2:
            if admin_data[4]:
                st.write("Current Photo")
                st.image(admin_data[4], use_container_width=True)  # Assuming image is at index 4
        with c3:
            Image_file = st.camera_input("Update Image")

        update_btn = st.form_submit_button("Update", type="primary")

    if update_btn:
        if not Uname or not Gmail or not Contact or not Password:
            st.warning("Please fill all fields.")
        else:
            # Prepare image bytes
            if Image_file:
                try:
                    image = Image.open(Image_file)
                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format='PNG')
                    img_data = img_byte_arr.getvalue()
                except Exception as e:
                    st.error(f"Error processing image: {e}")
                    return
            else:
                img_data = admin_data[4] if isinstance(admin_data, tuple) else admin_data.get('Image', None)  # keep existing image

            # Prepare update data
            update_result = db.A_update((
                Uname, str.lower(Gmail), Contact, img_data, Password,
                admin_data[2] if isinstance(admin_data, tuple) else admin_data.get('Gmail', ''),  # old Gmail
                admin_data[5] if isinstance(admin_data, tuple) else admin_data.get('Password', '')  # old password
            ))

            if update_result:
                st.success("Admin details updated successfully!")
            else:
                st.error("Something went wrong during update.")          

# --- Main admin_update Function ---
def admin_update():
    st.header("Admin Update")

    # Initialize session_state attributes
    if "admin_log_in" not in st.session_state:
        st.session_state.admin_log_in = False
    if "admin_data" not in st.session_state:
        st.session_state.admin_data = None

    # LOGIN
    if not st.session_state.admin_log_in:
        admin_data = admin_login_form()
        if admin_data:
            st.session_state.admin_log_in = True
            st.session_state.admin_data = admin_data

    # UPDATE FORM
    if st.session_state.admin_log_in and st.session_state.admin_data:
        if st.button("Logout", type="primary"):
            st.session_state.admin_log_in = False
            st.session_state.admin_data = None
            st.rerun()

        show_admin_update_form(st.session_state.admin_data)

def admin_delete():
    st.header("Admin Delete")

    # Initialize session_state attributes
    if "admin_log_in" not in st.session_state:
        st.session_state.admin_log_in = False
    if "admin_data" not in st.session_state:
        st.session_state.admin_data = None

    # LOGIN
    if not st.session_state.admin_log_in:
        admin_data = admin_login_form()
        if admin_data:
            st.session_state.admin_log_in = True
            st.session_state.admin_data = admin_data

    # DELETE FORM
    if st.session_state.admin_log_in and st.session_state.admin_data:
        if st.button("Logout", type="primary"):
            st.session_state.admin_log_in = False
            st.session_state.admin_data = None
            st.rerun()

        st.subheader("⚠️ Delete Your Admin Account")
        st.warning("This action cannot be undone. All your admin data will be permanently deleted.")

        confirm = st.checkbox("Yes, I want to delete my account.")
        if confirm and st.button("Confirm Delete", type="primary"):
            email = st.session_state.admin_data[2]  # Gmail
            password = st.session_state.admin_data[5]  # Password

            success = db.A_delete((email, password))
            if success:
                st.success("Your account has been deleted successfully.")
                st.session_state.admin_log_in = False
                st.session_state.admin_data = None
            else:
                st.error("Account could not be deleted. Please try again.")

# Function to Add new database records
def Add():
    st.header("Register Data")

    # **User Type Selection in Form Format**
    with st.container(border=True):
        Utype = st.selectbox("User Type", options=["Admin", "Faculty", "Visitor", "Student"])
    if Utype == "Student":
        u.s_register()
    elif Utype == "Faculty":
        u.f_register()
    elif Utype == "Visitor":
        u.v_register()
    elif Utype=="Admin":
        register()

#Function to update database records
def Update_database():
    st.header("Update Databases")

    # **User Type Selection in Form Format**
    with st.container(border=True):
        Utype = st.selectbox("User Type", options=["Admin", "Faculty", "Visitor", "Student"])
        
    if Utype == "Student":
        u.s_update()
    elif Utype == "Faculty":
        u.f_update()
    elif Utype == "Visitor":
        u.v_update()
    elif Utype == "Admin":
        admin_update()   

# Function to delete database records
def Delete_database():
    st.header("Delete from Databases")

    with st.container(border=True):
        Utype = st.selectbox("User Type", options=["Admin", "Faculty", "Visitor","Student"])

    if Utype == "Student":
        u.s_delete()
    elif Utype == "Faculty":
        u.f_delete()
    elif Utype == "Visitor":
        u.v_delete()
    elif Utype == "Admin":
        admin_delete()

# ✅ Create Horizontal Navigation Bar
selected_option = option_menu(
    menu_title=None,
    options=["Login"] if not st.session_state["admin_logged_in"] else ["Home", "Register", "View Data","Update Data","Delete Data","Logout"],
    icons=["key"] if not st.session_state["admin_logged_in"] else ["house", "person-plus", "table","person","trash","box-arrow-right"],
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
        Add()
    elif selected_option=="View Data":
        view()
    elif selected_option=="Update Data":
        Update_database()
    elif selected_option=="Delete Data":
        Delete_database()
    elif selected_option == "Logout":
        st.session_state["admin_logged_in"] = False
        st.session_state["admin_name"] = ""
        st.rerun()
else:
    st.warning("Please log in as Admin to access this section.")
