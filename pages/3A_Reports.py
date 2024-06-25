import streamlit as st
import pandas as pd
from Home import face_rec  # Assuming you have face_rec.py
from utils import set_page_config

set_page_config()


# --- Retrieve attendance data from Redis ---
attendance_logs = face_rec.r.lrange('attendance:logs', 0, -1)
attendance_logs = [log.decode('utf-8') for log in attendance_logs]

# --- Convert logs to DataFrame ---
logs_df = pd.DataFrame([log.split('@') for log in attendance_logs], 
                      columns=['Name', 'Role', 'Timestamp'])
logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])

# --- Streamlit UI ---
st.title("Attendance Report ")

# --- Filtering Options ---
#filter_type = st.radio("Filter by:", ["Date", "Name", "Mobile No"])
filter_type = st.radio("Filter by:", ["Date", "Name"])

filtered_df = logs_df.copy()  # Start with a copy of the entire DataFrame

if filter_type == "Date":
    selected_date = st.date_input("Select Date")
    filtered_df = filtered_df[filtered_df['Timestamp'].dt.date == selected_date]
elif filter_type == "Name":
    all_names = logs_df['Name'].unique()
    selected_name = st.selectbox("Select Name", all_names)
    filtered_df = filtered_df[filtered_df['Name'] == selected_name]
# elif filter_type == "Mobile No":
#     all_mobile_numbers = face_rec.retrive_data2(name='contact1:register')['Mobile'].unique()  # Get unique mobile numbers from registered users
#     selected_mobile = st.selectbox("Select Mobile No", all_mobile_numbers)
#     filtered_df = filtered_df[filtered_df['Name'].isin(
#         face_rec.retrive_data2(name='contact1:register')['Name']
#     )]  # Filter by names associated with the selected mobile number

# --- Display Filtered Data ---
if not filtered_df.empty:
    st.write(filtered_df)

    # --- Download Button ---
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download Data as CSV",
        data=csv,
        file_name=f"attendance_report_{filter_type.lower()}.csv",
        mime="text/csv",
    )
else:
    st.warning("No data found for the selected filter.")
