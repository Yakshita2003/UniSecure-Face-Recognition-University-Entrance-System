import sqlite3 #Provides an interface to work with SQLite databases.
import streamlit as st
import pytz  #Full Form "Python Time Zone" and use is facilitates working with time zones, especially those in the Olson database (also known as the IANA time zone database).
import datetime # provides classes for working with dates and times.

def create_connect():
    """
    Establishes a connection to the SQLite database.
    """
    conn = sqlite3.connect("UniSecure.db", check_same_thread=False)
    return conn

# Create database connection and cursor
conn = create_connect()
cursor = conn.cursor()

def stu_reg(data):
    """
    Registers a new student into the database.
    """
    try:
        cursor.execute('''INSERT INTO Student (Name, Roll_No, Gmail, Course, Stream, Year, Photo, Password) 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        st.success("Student Registered Successfully!")
    except sqlite3.IntegrityError as e:
        st.error("Duplicate entry detected: Roll_No or Photo must be unique.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def stu_view(data):
    """
    Retrieves a student's information from the database based on provided credentials.
    """
    try:
        cursor.execute("SELECT * FROM Student WHERE Gmail=? AND Roll_No=? AND Password=?", data)
        result = cursor.fetchone()
        if result:
            return result
        else:
            st.warning("No student found with the provided details.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def s_readone(data):
    """Fetch a single student record."""
    try:
        cursor.execute(
            "SELECT * FROM Student WHERE Roll_No=? AND Gmail=? AND Password=?", data
        )
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Error fetching student data: {e}")

def stu_update(data):
    """
    Update student details based on Roll_No, Gmail, and Password.

    Expected `data` format:
    (Name, Roll_No, Gmail, Course, Stream, Year, Photo, Password, Old_Roll, Old_Gmail, Old_Password)
    """
    try:
        query = '''
            UPDATE Student 
            SET Name=?, Roll_No=?, Gmail=?, Course=?, Stream=?, Year=?, Photo=?, Password=? 
            WHERE Roll_No=? AND Gmail=? AND Password=?
        '''
        cursor.execute(query, data)
        conn.commit()
        if cursor.rowcount == 0:
            print("⚠️ No rows updated. Invalid credentials or no changes.")
            return False
        return True
    except sqlite3.IntegrityError as ie:
        print("❌ Integrity error:", ie)
        return False
    except Exception as e:
        print("❌ General DB error:", e)
        return False

def FS_reg(data):
    """
    Registers Faculty in the database.
    """
    try:
        cursor.execute("INSERT INTO Faculty (Name, Gmail,Designation, Photo,Password) VALUES (?, ?, ?,?,?)", data)
        conn.commit()
        st.success("Faculty Registered Successfully!")
    except sqlite3.IntegrityError:
        st.error("Duplicate entry detected.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def FS_view(data):
    """
    Retrieves Faculty details from the database.
    """
    try:
        cursor.execute('''SELECT * FROM Faculty WHERE Gmail=? AND Password=?''', data)
        res=cursor.fetchone()
        if res:
            return res
        else:
            return False
    except Exception as e:
        st.error(f"Something went wrong: {e}")
        return False

def f_readone(data):
    """Fetch a single Faculty record."""
    try:
        cursor.execute(
            "SELECT * FROM Faculty WHERE Gmail=? AND Password=?", data
        )
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Error fetching Faculty data: {e}")

def f_update(data):
    """
    Update faculty details in the database.
    data: (Name, Gmail, Designation, Photo, Password, old_Gmail, old_Password)
    """
    try:
        query = '''UPDATE Faculty
                   SET Name=?, Gmail=?, Designation=?, Photo=?, Password=? 
                   WHERE Gmail=? AND Password=?'''
        
        # Ensure data is flat (not nested)
        cursor.execute(query, data)
        conn.commit()

        # Check if any row was actually updated
        return cursor.rowcount > 0
    except Exception as e:
        print(f"Something went wrong: {e}")
        return False

def V_reg(data):
    """
    Registers a visitor in the database.
    """
    try:
        cursor.execute("INSERT INTO Visitor (Name, Contact, ID_type, ID_no, Purpose, Photo) VALUES (?, ?, ?, ?, ?, ?)", data)
        conn.commit()
        st.success("Visitor Registered Successfully!")
    except sqlite3.IntegrityError:
        st.error("Duplicate entry detected.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def V_view(data):
    """
    Retrieves Visitor details from the database using Name, Contact.
    """
    try:
        cursor.execute("SELECT * FROM Visitor WHERE Contact=?", (data,))
        return cursor.fetchone()
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def V_update(id, name, gmail, contact, id_type, id_no, purpose, photo_bytes):
    try:
        query = """
        UPDATE visitors
        SET name = ?, gmail = ?, contact = ?, id_type = ?, id_no = ?, purpose = ?, photo = ?
        WHERE id = ?
        """
        cursor.execute(query, (name, gmail, contact, id_type, id_no, purpose, photo_bytes, id))
        conn.commit()
        return True
    except Exception as e:
        print("Update Error:", e)
        return False
    
def A_reg(data):
    """
    Registers Admin in the database.
    """
    try:
        cursor.execute("INSERT INTO Admin (Username,Gmail, Contact,Image,Password) VALUES (?, ?, ?,?,?)", data)
        conn.commit()
        st.success("Admin Registered Successfully!")
    except sqlite3.IntegrityError:
        st.error("Duplicate entry detected.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")

def A_readone(data):
    """Fetch a single Admin record."""
    try:
        cursor.execute(
            '''SELECT * FROM Admin WHERE Gmail=? AND Password=?''', data
        )
        return cursor.fetchone()
    except sqlite3.Error as e:  # Use specific exception
        st.error(f"Error fetching Admin data: {e}")
        return None  # Important to return None in case of error
    
def A_update(data):
    """Update admin details in the database."""
    try:
        query = '''
            UPDATE Admin
            SET Username=?, Gmail=?, Contact=?, Image=?, Password=?
            WHERE Gmail=? AND Password=?  
        '''
        cursor.execute(query,data)  # Corrected
        conn.commit()
        return True
    except sqlite3.Error as e:  # Use specific exception
        st.error(f"Something went wrong: {e}")
        conn.rollback()  # Rollback in case of error to maintain data integrity
        return False

def view(Utype):
    try:
        if Utype=="Admin":
            res=cursor.execute(F'''SELECT Id,Username,Gmail, Contact,Image FROM Admin''')
        elif Utype=="Student":
            res=cursor.execute(F'''SELECT Id,Name, Roll_No, Gmail, Course, Stream, Year, Photo FROM Student''')    
        elif Utype=="Faculty":
            res=cursor.execute(f'''SELECT Id,Name, Gmail, Designation, Photo FROM Faculty''')
        elif Utype=="Visitor":
            res=cursor.execute(f'''SELECT Id,Name, Gmail, Contact,Id_type, Id_no, Purpose, Photo FROM Visitor''')
        elif Utype=="Log":
            res=cursor.execute(f'''SELECT ID,Usertype,Username,Status,Timestamp,VerificationType FROM Access_Logs''')
        st.success(f"{Utype} Database Found Successfully")
        return res
    except Exception as e:
        st.error(e)

def get_admin(data):
    """Fetch admin details from the database based on name and email."""
    try:
        query = '''SELECT * FROM Admin WHERE Password=? AND Gmail = ?'''
        cursor.execute(query, data)
        res=cursor.fetchone()  # Fetch all matching records
        if res:
            return True
        else:
            return False
    except Exception as e:
        st.error(e)
        return False

def get_student_by_id(data):
    cursor.execute("SELECT * FROM Student WHERE Roll_No=?", (data,))
    result = cursor.fetchone()
    return result

def V_view_by_contact(contact):
    cursor.execute("SELECT * FROM visitor WHERE Contact=?", (contact,))
    result = cursor.fetchone()
    return result

def V_view_by_gmail(gmail):
    cursor.execute("SELECT * FROM visitor WHERE Gmail=?", (gmail,))
    result = cursor.fetchone()
    return result

def V_update(id, name, gmail, contact, id_type, id_number, purpose, photo):
    cursor.execute("""
        UPDATE visitor SET 
            Name=?, Gmail=?, Contact=?, ID_type=?, ID_no=?, Purpose=?, Photo=? 
        WHERE id=?
    """, (name, gmail, contact, id_type, id_number, purpose, photo, id))
    conn.commit()
    updated = cursor.rowcount > 0
    return updated

def save_log(data):
    try:
        # Get IST time
        ist_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')

        # Add timestamp to data tuple
        data_with_timestamp = data + (ist_time,)

        # Insert into table with manual IST timestamp
        cursor.execute('''
            INSERT INTO Access_Logs (Usertype, Username, Status, VerificationType, Timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', data_with_timestamp)

        conn.commit()
        return True
    except Exception as e:
        st.error(e)
        return False
    
# -------- Faculty --------
def get_faculty_by_gmail(gmail):
    cursor.execute("SELECT * FROM Faculty WHERE Gmail = ?", (gmail,))
    result= cursor.fetchone()
    return result

def delete_faculty_by_gmail(gmail):
    cursor.execute("DELETE FROM faculty WHERE Gmail = ?", (gmail,))
    conn.commit()

# -------- Student --------
def get_student_by_gmail(gmail):
    cursor.execute("SELECT Id,Name, Roll_No, Gmail, Course, Stream, Year FROM Student WHERE Gmail = ?", (gmail,))
    return cursor.fetchone()

def delete_student_by_gmail(gmail):
    cursor.execute("DELETE FROM Student WHERE Gmail = ?", (gmail,))
    conn.commit()
    
# -------- Visitor --------
def get_visitor_by_gmail(gmail):
    cursor.execute("SELECT * FROM visitor WHERE Gmail = ?", (gmail,))
    return cursor.fetchone()

def delete_visitor_by_gmail(gmail):
    cursor.execute("DELETE FROM visitor WHERE Gmail = ?", (gmail,))
    conn.commit()

def is_valid_Gmail(gmail,utype):
    gmail=str.lower(gmail)
    try:
        cursor.execute(f"Select Gmail from {utype} where Gmail=?",(gmail,))
        res=cursor.fetchone()
        if res:
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
