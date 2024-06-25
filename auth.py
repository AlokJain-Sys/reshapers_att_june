import streamlit as st
import  streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

from PIL import Image
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


if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar', key='unique_key')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Reshapers Systems Login')
elif st.session_state["authentication_status"] is False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None:
    st.warning('Please enter your username and password')
    
class MultiPage: 
    def __init__(self) -> None:
        self.pages = []
    
    def add_page(self, title, func) -> None: 
        self.pages.append(
            {
                "title": title, 
                "function": func
            }
        )

    def run(self):
        page = st.sidebar.selectbox(
            'App Navigation', 
            self.pages, 
            format_func=lambda page: page['title']
        )

        
