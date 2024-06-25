import streamlit as st
import  streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import cv2 
from PIL import Image
import time
# Loading Image using PIL
im = Image.open('./content/logo.png')
# Adding Image to web app
st.set_page_config(page_title="Reshapers Face Recognition Attendance System", page_icon = im)
hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)
    

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

authenticator.login(fields=['name', 'password'])


rtsp_url= st.text_input("rtsp://admin:ab@123456@122.160.10.254/Streaming/Channels/101")

# Create a toggle button for starting/stopping the CCTV feed
if 'running' not in st.session_state:  
    st.session_state['running'] = False

if st.button("Start/Stop CCTV"):
    st.session_state['running'] = not st.session_state['running']

# Create a placeholder for the video feed
video_placeholder = st.empty()

# Video capture object
cap = None


# --- Open CCTV Feed ---
if st.session_state['running']:
    try:
        # Initialize the video capture object
        cap = cv2.VideoCapture(rtsp_url)

        # Check if camera opened successfully
        if not cap.isOpened():
            st.error("Error opening video stream or file")

        # Read and display video frames until the user stops the CCTV
        while st.session_state['running']:
            ret, frame = cap.read()

            # Check if the 'stop' button was clicked
            if not st.session_state['running']:
                break

            if not ret:
                st.error("Can't receive frame (stream end?). Exiting ...")
                st.session_state['running'] = False
                break

            # Convert frame from BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Display the frame in the placeholder
            video_placeholder.image(frame, channels="RGB")
            time.sleep(0.01)  # Adjust as needed
    
    except Exception as e:
        st.error(f"Error connecting to CCTV: {e}")
    
    finally:
        # Release the video capture object and clean up resources
        if cap is not None and cap.isOpened():
            cap.release()
            video_placeholder.empty()

# Additional placeholder for messages
status_placeholder = st.empty()

if not st.session_state['running']:
    status_placeholder.write("CCTV is not running.")


if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Reshapers Systems Login')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')


with st.spinner("Loading Models and Conneting to db ..."):
    import face_rec
    import face_rec_old
    import Registration_Fom_CCTV
st.success('Model loaded sucesfully')
st.success('DB sucessfully connected')
