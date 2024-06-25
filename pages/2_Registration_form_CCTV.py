import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
from Home import Registration_Fom_CCTV,face_rec
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av
import re 
from utils import set_page_config

set_page_config()

## init registration form
registration_form = Registration_Fom_CCTV.RegistrationForm



# Import the RegistrationForm class from registration_form.py 

# Get RTSP URL from user input in Streamlit app
rtsp_url = "rtsp://admin:ab@123456@122.160.10.254/Streaming/Channels/101"


# ... rest of the code is same as before

# Step-1: Collect person name and role (with validation)
# form
person_name = st.text_input(label='Name',placeholder='First & Last Name')
person_name = person_name.title()  # Automatically convert to proper case
role = st.selectbox(label='Select your Role',options=('Staff', 'Member'))
mobile = st.text_input(label='Mobile',placeholder='Give your Mobile')

email = st.text_input(label='Email', placeholder='Put Email for Registration')
def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_mobile(mobile):
    pattern = r"^\d{10}$"  # Assuming 10-digit mobile number
    return bool(re.match(pattern, mobile))
# step-2: Collect facial embedding of that person
def video_frame_callback(frame):
    """Processes the frame for capturing face embeddings during registration."""
    img = frame.to_ndarray(format='bgr24') # 3d array bgr

    # Create an instance of RegistrationForm
    registration_form = Registration_Fom_CCTV.RegistrationForm(rtsp_url)
    
    reg_img, embedding = registration_form.get_embedding()

    # two step process
    # 1st step save data into local computer txt
    if embedding is not None:
        with open('face_embedding.txt',mode='ab') as f:
            np.savetxt(f,embedding)
    
    return av.VideoFrame.from_ndarray(reg_img,format='bgr24')

webrtc_streamer(key="registration",video_frame_callback=video_frame_callback,
    rtc_configuration={
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
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

    
    return_val = registration_form.save_data_in_redis_db(person_name,role,mobile,email)
    if return_val == True:
        st.success(f"{person_name} registered sucessfully")
    elif return_val == 'name_false':
        st.error('Please enter the name: Name cannot be empty or spaces')
       
    elif return_val == 'file_false':
        st.error('face_embedding.txt is not found. Please refresh the page and execute again.')
    
