import io
import streamlit as st
import db
from PIL import Image
import cv2

'''Student Utils to admin'''
# Function for student registration
def s_register():
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

#Student Updation Form
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
def s_update():
    st.header("Update Student Details")

    student_id = st.number_input("Enter Student Roll No / ID", min_value=1, step=1)
    
    if st.button("Fetch Student",type="primary"):
        res = db.get_student_by_id(student_id)
        if res:
            st.session_state.student_data = res
        else:
            st.error("Student not found.")

    if "student_data" in st.session_state and st.session_state.student_data:
        show_update_form(st.session_state.student_data)

def s_delete():
    gmail = st.text_input("Enter Student Gmail to delete:")

    if st.button("Delete Student", type="primary"):
        res = db.get_student_by_gmail(gmail)
        if res:
            st.session_state.student_to_delete = gmail
            st.session_state.student_found = res
        else:
            st.error("No student found with this Gmail.")

    # If student was found and stored in session_state
    if "student_to_delete" in st.session_state:
        confirm = st.checkbox("Are you sure you want to delete this student?")
        button=st.button("Confirm Delete", type="primary")
        st.write("Student Found:", st.session_state.student_found)
        if button and confirm:
            db.delete_student_by_gmail(st.session_state.student_to_delete)
            st.success("Student deleted successfully.")
            # Clean up session state
            del st.session_state.student_to_delete
            del st.session_state.student_found


'''Faculty utils to admin'''
# Function for Faculty registration
def f_register():
    st.header("Faculty Registration Page")
    with st.form("Registration Form"):
        c1, c2 = st.columns(2)
        with c1:
            Name = st.text_input("Name")
            Gmail = st.text_input("Gmail")
            Designation = st.text_input("Designation")
            Password = st.text_input("Password", type="password")
        with c2:
            Image_file = st.camera_input("Image")
        submit = st.form_submit_button("Register",type="primary")

    if submit:
        if not Name or not Gmail or not Designation or not Image_file or not Password:
            st.error("Please fill the form correctly")
        else:
            image = Image.open(Image_file)
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format='PNG')
            img_data = img_byte_arr.getvalue()
            data = (Name, Gmail, Designation, img_data, Password)
            db.FS_reg(data)

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
            Name, Gmail, Designation, img_data, Password,
            res[2], res[5]  # old Gmail, old Password
            ))  

            if result:
                st.success("Faculty details updated successfully!")
                st.session_state.faculty_authenticated = False
                st.session_state.faculty_data = None
            else:
                st.error("Something went wrong during update.")

# ---------- Main Faculty Update Controller ----------
def f_update():
    st.header("Update Faculty Details")

    gmail = st.text_input("Enter Faculty Gmail")
    
    if st.button("Fetch Faculty",type="primary"):
        res = db.get_faculty_by_gmail(gmail)
        if res:
            st.session_state.faculty_data = res
        else:
            st.error("Faculty not found.")

    if "faculty_data" in st.session_state and st.session_state.faculty_data:
        show_faculty_update_form(st.session_state.faculty_data)

def f_delete():
    gmail = st.text_input("Enter Faculty Gmail to delete:")

    if st.button("Delete Faculty", type="primary"):
        res = db.get_faculty_by_gmail(gmail)
        if res:
            st.session_state.faculty_to_delete = gmail
            st.session_state.faculty_found = res
        else:
            st.error("No faculty found with this Gmail.")

    if "faculty_to_delete" in st.session_state:
        confirm = st.checkbox("Are you sure you want to delete this faculty?")
        button=st.button("Confirm Delete", type="primary")
        st.write("Faculty Found:", st.session_state.faculty_found)
        if button and confirm:
            db.delete_faculty_by_gmail(st.session_state.faculty_to_delete)
            st.success("Faculty deleted successfully.")
            # Clean up session state
            del st.session_state.faculty_to_delete
            del st.session_state.faculty_found

'''Visitor Utils to admin'''   
# Function for Visitor registration
def v_register():
    st.header("Visitor Registration Page")
    with st.form("Visitor Registration Form"):
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
            data = (Name,Gmail,Contact, ID_type, ID_no, Purpose, img_data)
            db.V_reg(data)

def v_update():
    st.header("Update Visitor Details")

    method = st.radio("Search by:", ["Contact", "Gmail"])
    input_val = st.text_input(f"Enter {method}")

    if st.button("Fetch Visitor",type="primary"):
        if not input_val:
            st.error(f"Please enter the {method}.")
        else:
            if method == "Contact":
                visitor = db.V_view_by_contact(input_val)
            else:
                visitor = db.V_view_by_gmail(input_val)

            if visitor:
                st.session_state.visitor_data = visitor
            else:
                st.error("Visitor not found.")

    if "visitor_data" in st.session_state:
        visitor = st.session_state.visitor_data

        with st.form("Visitor Update Form", clear_on_submit=True):
            c1,c2=st.columns(2)
            with c1:
                name = st.text_input("Name", value=visitor[1])
                gmail = st.text_input("Gmail", value=visitor[2])
                contact = st.text_input("Contact", value=visitor[3])
                id_type = st.selectbox("ID Type", ["Aadhar Card", "Driving Licence", "Pan Card", "Other"], index=0)
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
                visitor[0], name, gmail, contact,
                id_type, id_number, purpose, photo_bytes
            )
            if updated:
                st.success("✅ Visitor details updated successfully.")
                st.session_state.visitor_data = db.V_view_by_contact(contact)
            else:
                st.error("❌ Failed to update visitor details.")

def v_delete():
    gmail = st.text_input("Enter Visitor Gmail to delete:")

    if st.button("Delete Visitor", type="primary"):
        res = db.get_visitor_by_gmail(gmail)
        if res:
            st.session_state.visitor_to_delete = gmail
            st.session_state.visitor_found = res
        else:
            # Clear old data if no visitor found
            st.error("No visitor found with this Gmail.")
            st.session_state.pop("visitor_to_delete", None)
            st.session_state.pop("visitor_found", None)

    if "visitor_to_delete" in st.session_state:
        confirm = st.checkbox("Are you sure you want to delete this visitor?")
        button = st.button("Confirm Delete", type="primary")
        st.write("Visitor Found:", st.session_state.visitor_found)
        if confirm and button:
            db.delete_visitor_by_gmail(st.session_state.visitor_to_delete)
            st.success("Visitor deleted successfully.")
            # Clean up session state after deletion
            del st.session_state.visitor_to_delete
            del st.session_state.visitor_found
