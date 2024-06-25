import streamlit as st
from Home import face_rec,face_rec_old
import cv2
import numpy as np
from streamlit_webrtc import webrtc_streamer
import av
import re 
from utils import set_page_config

set_page_config()

## init registration form
registration_form = face_rec_old.RegistrationForm()

# Step-1: Collect person name and role (with validation)
person_name = st.text_input(label='Name', placeholder='First & Last Name', value="")
erson_name = person_name.title()  # Automatically convert to proper case
role = st.selectbox(label='Select Role', options=('Member', 'Staff'))
mobile = st.text_input(label='Mobile', placeholder='Give Mobile')

email = st.text_input(label='Email', placeholder='Put Email for Registration')

# Validation Functions
def validate_email(email):
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))

def validate_mobile(mobile):
    pattern = r"^\d{10}$"  # Assuming 10-digit mobile number
    return bool(re.match(pattern, mobile))

# step-2: Collect facial embedding of that person
def video_callback_func(frame):
    img = frame.to_ndarray(format='bgr24') # 3d array bgr
    reg_img, embedding = registration_form.get_embedding(img)
    # two step process
    # 1st step save data into local computer txt
    if embedding is not None:
        with open('face_embedding.txt',mode='ab') as f:
            np.savetxt(f,embedding)
    
    return av.VideoFrame.from_ndarray(reg_img,format='bgr24')

webrtc_streamer(key="registration",video_frame_callback=video_callback_func,
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
    
