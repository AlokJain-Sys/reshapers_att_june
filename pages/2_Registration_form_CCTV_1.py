import streamlit as st
from streamlit_webrtc import webrtc_streamer
from Home import face_rec, face_rec_old, Registration_Fom_CCTV
import cv2
import numpy as np
import av
import re
from utils import set_page_config

# Configuration for RTSP Camera
RTSP_URL = "rtsp://admin:ab@123456@122.160.10.254/Streaming/Channels/101"  # Replace with your actual RTSP URL



## init registration form
registration_formcc = face_rec_old.RegistrationForm()

# Input Fields
st.subheader('Registration Form')
person_name = st.text_input("Name (First & Last)", value="")
person_name = person_name.title()  # Automatically convert to proper case
role = st.selectbox("Select Role", ('Member', 'Staff'))
mobile = st.text_input("Mobile Number", value="")
email = st.text_input("Email Address", value="")

# Form Validation
def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_mobile(mobile):
    pattern = r"^\d{10}$"  # Assuming 10-digit mobile number
    return bool(re.match(pattern, mobile))

# Video Capture and Face Embedding
def video_frame_callback(frame):
    img = frame.to_ndarray(format='bgr24')

    # Use OpenCV to read from the RTSP stream
    cap = cv2.VideoCapture(RTSP_URL)
    ret, img = cap.read()

    if not ret:
        st.error("Error reading from RTSP stream. Please check the URL and connectivity.")
        return  # Or return a default image to prevent errors in the rest of the code
    reg_img, embedding = registration_formcc.get_embedding(img)

    if embedding is not None:
        with open('face_embedding.txt', mode='ab') as f:
            np.savetxt(f, embedding)

    return av.VideoFrame.from_ndarray(reg_img, format='bgr24')

# Streamlit WebRTC Component
# webrtc_streamer(
#     key="registration", 
#     video_frame_callback=video_callback_func,
#     rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
# )
webrtc_streamer(key="realtimePrediction", video_frame_callback=video_frame_callback,
    rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        },
        media_stream_constraints={
        "video": {"width": 640, "height": 480, "frameRate": {"ideal": 15, "max": 20}},"timeout": 6000,  # Reduce resolution and frame rate
    }
    )


# step-3: save the data in redis database


if st.button('Submit'):
    if person_name and role and validate_mobile(mobile) and validate_email(email):
        pass
    else:
        if not person_name:
            st.error("Please enter a name.")
        if not validate_mobile(mobile):
            st.error("Please enter a valid 10-digit mobile number.")
            mobile=str(mobile)
        if not validate_email(email):
            st.error("Please enter a valid email address.")
        
        dup_chk=face_rec.check_duplicates(person_name, role, mobile)
        
        if   dup_chk == False:
            pass
        else: st.error("Duplicate Name or mobile No")

    
    return_val = registration_formcc.save_data_in_redis_db(person_name,role,mobile,email)
    if return_val == True:
        st.success(f"{person_name} registered sucessfully")
    elif return_val == 'name_false':
        st.error('Please enter the name: Name cannot be empty or spaces')
       
    elif return_val == 'file_false':
        st.error('face_embedding.txt is not found. Please refresh the page and execute again.')
    
