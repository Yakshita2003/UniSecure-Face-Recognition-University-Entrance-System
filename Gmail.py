import smtplib #handles the transmission of messages via SMTP
import random #offers functions for generating random integers, floating-point numbers, and selecting random elements from sequences like lists
import ssl #(Secure Sockets Layer) library is a software toolkit that provides the necessary functions and tools to implement Secure Sockets Layer (SSL) or Transport Layer Security (TLS) protocols for secure network communication
from email.message import EmailMessage #focuses on message structure 
import streamlit as st
import re #provides tools for pattern matching and manipulation in strings
import db

def generate_otp():
    return ''.join([str(random.randint(0, 9)) for _ in range(6)])

def send_otp(receiver_email, otp):
    sender_email = "Your Gmail"
    sender_password = "Your App Password"

    subject = "Your OTP for Verification"
    body = f"Your One Time Password (OTP) is: {otp}"

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.set_content(body)

    context = ssl.create_default_context() 
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, sender_password)
        server.send_message(message)

def verify_otp(user_input, otp):
    return user_input == otp

def is_valid_email(email):
    pattern = re.compile("[a-zA-Z0-9]+@[^@]+\.[a-z]{3,7}")
    return re.match(pattern, email)

def save(Utype, uname, Vtype, status):
    res = db.save_log((Utype, uname, Vtype, status))
    if res:
        st.success("Log Saved Successfully")
    else:
        st.error("Something went wrong")

# Initialize Gmail-related session states
if "gmail_logged_in" not in st.session_state:
    st.session_state["gmail_logged_in"] = False
if "gmail_user" not in st.session_state:
    st.session_state["gmail_user"] = ""
if "gmail_verified" not in st.session_state:
    st.session_state["gmail_verified"] = False

def main(Utype, Vtype="Email Verification"):
    if 'step' not in st.session_state:
        st.session_state.step = 1
    if 'otp' not in st.session_state:
        st.session_state.otp = ""
    if 'uname' not in st.session_state:
        st.session_state.uname = ""

    # LOGOUT button
    if st.button("Logout", type="primary"):
        for key in ["step", "otp", "uname", "email", "gmail_logged_in", "gmail_user", "gmail_verified"]:
            if key in st.session_state:
                del st.session_state[key]
        st.rerun()

    st.header("Email OTP Verification")

    if st.session_state.step == 1:
        with st.form("Form"):
            uname = st.text_input("Username")
            email = st.text_input("Email:")
            submit = st.form_submit_button("Verify Email 📧", type="primary")

        if submit:
            if is_valid_email(email):
                st.success("✅ Valid email")
                res=db.is_valid_Gmail(email,Utype)
                if res:
                    st.success("✅Registered Email.")
                    st.session_state.uname = uname
                    st.session_state.email = email
                    st.session_state.otp = generate_otp()
                    st.session_state.step = 2
                else:
                    st.error("❌Email is not registered.")
            else:
                st.error("❌ Invalid email")

    # Step 2: OTP Entry
    if st.session_state.step == 2:
        st.info("Generating OTP...")
        send_otp(st.session_state.email, st.session_state.otp)
        st.success(f"🔑OTP sent to {st.session_state.uname} on {st.session_state.email}")

        user_input = st.text_input("Enter the OTP sent to your email:")
               
        if st.button("Submit OTP", type="primary"):
            if verify_otp(user_input, st.session_state.otp):
                st.success("✅ Verification successful! Access Granted")
                st.session_state.gmail_logged_in = True
                st.session_state.gmail_user = st.session_state.email
                st.session_state.gmail_verified = True
                status = "Access Granted"
            else:
                st.error("❌ Invalid OTP. Try again!")
                status = "Access Denied"

            save(Utype, st.session_state.uname, Vtype, status)
