from Home import st
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import av
import time
import redis
from utils import set_page_config

set_page_config()

# --- Streamlit Page Structure ---
st.title("Registerd Data Management")

# --- Function to Retrieve Redis Data ---
def get_redis_data():
    all_data = face_rec.r.hgetall('contact1:register')
    return all_data

# --- Retrieve and Display ---
data = get_redis_data()
st.dataframe(data)  # Display as a DataFrame for easy viewing

# --- Deletion Logic ---
selected_names = st.multiselect("Select names to delete:", options=data.keys())
if st.button("Delete Selected"):
    for name in selected_names:
        face_rec.r.hdel('contact1:register', name)
    st.success("Selected names deleted!")
    st.experimental_rerun()  # Refresh the page after deletion

