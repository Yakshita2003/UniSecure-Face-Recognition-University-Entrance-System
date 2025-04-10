import streamlit as st
import db

# Page Configuration setup
st.set_page_config("UniSecure", page_icon=":shield:", layout="wide")
st.title("🔒 Welcome to UniSecure!")

st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {display: none;}
    </style>
    """,
    unsafe_allow_html=True
)

# Image and intro content setup on top
with st.container():
    c1, c2 = st.columns([2,0.8])
    with c1:
        st.subheader("About UniSecure")
        st.markdown(
            """
            **UniSecure** is a cutting-edge smart university system designed to redefine access control and security in educational institutions. With increasing concerns over campus safety and administrative efficiency, UniSecure provides a robust, software-driven solution that simplifies access management while maintaining strict security protocols. 
            
            🔹 **Features:**
            - 🎓 Secure authentication for students, faculty, and staff
            - 🏫 Campus-wide access control management
            - 📊 Real-time monitoring and user role management
            
            Built with a focus on **efficiency, reliability, and ease of use**, UniSecure helps institutions create a safe and well-regulated environment for everyone.
            """,
            unsafe_allow_html=True
        )
    with c2:
        st.image("Uni3.png", use_container_width=True)

st.subheader("Select the User Type")
c1, c2, c3, c4 = st.columns(4)

if c1.button("Admin", use_container_width=True,type="primary"):
    st.switch_page("pages/Admin.py")  # Navigates to pages/Admin.py

if c2.button("Student", use_container_width=True,type="primary"):
    st.switch_page("pages/Student.py")  # Navigates to pages/Student.py

if c3.button("Faculty/Staff", use_container_width=True,type="primary"):
    st.switch_page("pages/Faculty.py")  # Navigates to pages/Faculty.py

if c4.button("Visitor", use_container_width=True,type="primary"):
    st.switch_page("pages/Visitor.py")  # Navigates to pages/Visitor.py


