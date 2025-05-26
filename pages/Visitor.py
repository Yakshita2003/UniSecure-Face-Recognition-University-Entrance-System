import io
import streamlit as st
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
import requests as r
import db
from PIL import Image
from Face_Utils import recognize,del_encodings
from Gmail import main

st.set_page_config("Visitor Portal",layout="wide")  # Use wide layout for better spacing

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

if st.button("Go To Home Page ",type="primary"):
    del_encodings()
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("Home.py")

st.title("Visitor Page")

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
    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Welcome to the Visitor Portal!")
        st.write(
            "This portal allows you to register, view visitor records, and perform face recognition for security."
        )
    with col2:
        lottie_url1 = "https://lottie.host/a5071e3a-b4f1-4ec5-a243-91b942e3bcf7/00jpxR0yuK.json"
        lottie_json1 = load_lottie_url(lottie_url1)
        if lottie_json1:
            st_lottie(lottie_json1, speed=1, height=250, quality="high", key="lottie1")
        else:
            c,c1,c2=st.columns(3)
            with c:
                pass
            with c1:
                st.image("pages/istockphoto-1483562317-612x612.jpg",width=200)
            with c2:
                pass
            
# Function for Visitor registration
def register():
    st.header("Registration Page")
    with st.form("Registration Form"):
        c1,c2=st.columns(2)
        with c1:
            Name = st.text_input("Name")
            Gmail=st.text_input("Gmail")
            Contact = st.number_input("Contact No. (10-digits number)", format="%d", step=1)
            ID_type = st.selectbox("ID Type", ["Aadhar Card", "Driving Licence", "Pan Card", "Other"])
            ID_no = st.text_input("ID Number")
            Purpose = st.text_input("Visiting Purpose")
        with c2:
            Image_file = st.camera_input("Capture Image")
        submit = st.form_submit_button("Register",type="primary")
    
    if submit:
        if not Name or not Contact or not ID_type or not ID_no or not Purpose or not Image_file or not Gmail:
            st.error("Please fill all fields correctly")
        elif not len(ID_no)>=10:
            st.error("ID No should be of standard length depending on the Id type")
        else:
            image = Image.open(Image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()
            data = (Name,str.lower(Gmail),Contact, ID_type, ID_no, Purpose, img_data)
            db.V_reg(data)

def verify_id(visitor):
    if visitor:
        id_type = visitor[4] if visitor[4] else "ID"
        id_no = st.text_input(f"Enter {id_type}:")

        id_submit = st.button("Verify ID", type="primary")

        if id_submit:
            if not id_no:
                st.warning("Please enter the ID number.")
            elif id_no == visitor[5]:
                st.success("Visitor Found!")
                st.subheader("Visitor Details")
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Name**: {visitor[1]}")
                    st.write(f"**Gmail**: {visitor[2]}")
                    st.write(f"**Contact**: {visitor[3]}")
                    st.write(f"**ID Type**: {visitor[4]}")
                    st.write(f"**ID Number**: {visitor[5]}")
                    st.write(f"**Purpose**: {visitor[6]}")
                with col2:
                    st.image(Image.open(io.BytesIO(visitor[7])), caption="Visitor Photo", use_container_width=True)
            else:
                st.error("ID Number does not match.")

# Function to view Visitor data
def view():
    st.header("View Visitor Details")

    contact = st.text_input("Contact")

    # Load visitor data if stored previously
    visitor = st.session_state.get("visitor_data", None)

    if st.button("View", type="primary"):
        if not contact:
            st.error("Please fill all fields correctly.")
        else:
            result = db.V_view(contact)
            if result:
                st.session_state["visitor_data"] = result
                visitor = result
            else:
                st.error("Invalid details provided.")

    if visitor:
        verify_id(visitor)

def update():
    st.header("Update Visitor Details")

    contact = st.text_input("Contact")

    # Load visitor data if stored previously
    visitor = st.session_state.get("visitor_data", None)

    if st.button("Fetch Visitor", type="primary"):
        if not contact:
            st.error("Please enter contact.")
        else:
            result = db.V_view(contact)
            if result:
                st.session_state["visitor_data"] = result
                visitor = result
            else:
                st.error("Visitor not found.")

    # After loading visitor data
    if visitor:
        id_type = visitor[4] if visitor[4] else "ID"
        id_no = st.text_input(f"Enter {id_type} for verification:")

        if st.button("Verify ID", type="primary", key="verify_id"):
            if not id_no:
                st.warning("Please enter the ID number.")
            elif id_no == visitor[5]:
                st.success("✅ Verified! You can now update details.")

                with st.form("update_form", clear_on_submit=False):
                    c1,c2=st.columns(2)
                    with c1:
                        name = st.text_input("Name", value=visitor[1])
                        gmail = st.text_input("Gmail", value=visitor[2])
                        contact = st.text_input("Contact", value=visitor[3])
                        id_type = st.selectbox("ID Type", ["Aadhar", "PAN", "Driving License", "Passport"], index=0)
                        id_number = st.text_input("ID Number", value=visitor[5])
                        purpose = st.text_area("Purpose", value=visitor[6])
                    with c2:
                        if visitor[7]:
                            st.image(Image.open(io.BytesIO(visitor[7])), caption="Visitor Photo", use_container_width=True)
                        photo = st.camera_input("Capture Image")

                    submitted = st.form_submit_button("Update Visitor", type="primary")
                
                if submitted:
                    photo_bytes = photo.read() if photo else visitor[7]

                    updated = db.V_update(
                        visitor[0], name, str.lower(gmail), contact,
                        id_type, id_number, purpose, photo_bytes
                    )
                    if updated:
                        st.success("✅ Visitor details updated successfully.")
                        st.session_state["visitor_data"] = db.V_view(contact)
                    else:
                        st.error("❌ Failed to update visitor details.")
            else:
                st.error("❌ ID Number does not match.")

Utype="Visitor"
# Horizontal navigation menu
selected = option_menu(
    menu_title=None,
    options=["Home", "Register", "User Verification", "View Data","Update Data"],
    icons=["house", "person-plus", "camera", "table","person"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

# Routing to respective pages
if selected == "Home":
    home()
elif selected == "Register":
    register()
elif selected=="User Verification":
    st.header("Visitor Verification")
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

