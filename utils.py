from PIL import Image
import streamlit as st
def set_page_config():
    # Loading Image using PIL
    im = Image.open('./content/logo.png')  # Replace with your logo path

    # Adding Image to web app
    st.set_page_config(
        page_title="Reshapers Face Recognition Attendance System", 
        page_icon=im
    )

    # Hide Streamlit's default formatting
    hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
    st.markdown(hide_default_format, unsafe_allow_html=True)