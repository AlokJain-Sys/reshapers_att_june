import streamlit as st
import pandas as pd
from Home import face_rec
import numpy as np
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
st.title("Attendance Report")

# --- Filtering Options ---
filter_type = st.radio("Filter by:", ["Date", "Name"])
all_user_data = face_rec.retrive_data2(name='contact1:register')[['Name']] #get the user data 

filtered_df = logs_df.copy()

if filter_type == "Date":
    selected_date = st.date_input("Select Date")
    filtered_df = filtered_df[filtered_df['Timestamp'].dt.date == selected_date]
elif filter_type == "Name":
    all_names = logs_df['Name'].unique()
    selected_name = st.selectbox("Select Name", all_names)
    filtered_df = filtered_df[filtered_df['Name'] == selected_name]
    
    
# Calculate duration and attendance status 
def calculate_attendance(df):
    df_agg = df.groupby(['Name',pd.Grouper(key='Timestamp', freq='D')])['Timestamp'].agg(['min','max']).reset_index()
    df_agg.columns = ['Name', 'Date', 'In_Time', 'Out_Time']
    df_agg['Duration'] = df_agg['Out_Time'] - df_agg['In_Time']
    
    def mark_attendance(duration):
        if duration.total_seconds() < 4*3600 :
            return "Half Day"
        elif duration.total_seconds() > 6*3600 :
            return 'Present'
    df_agg['Status']= df_agg['Duration'].apply(mark_attendance)    
    return df_agg[['Name', 'Date', 'In_Time','Out_Time','Duration','Status']]

# Filter and Transform the data

if filter_type == 'Name':
    filter_df=calculate_attendance(filtered_df)
    filtered_df = filter_df.fillna('Absent') 
    
elif filter_type == 'Date':
    filter_df=calculate_attendance(filtered_df)

    # Mark missing entries as 'Absent' without filling NaT in Duration column
    filtered_df = filter_df.merge(all_user_data, on='Name', how='left')
    filtered_df['Status'] = filtered_df['Status'].fillna('Absent')
 
# --- Display Filtered Data ---
if not filtered_df.empty:
    filtered_df['Duration'] = filtered_df['Duration'].astype(str)
    #filtered_df.drop(columns=['facial_features'], inplace=True)

    st.dataframe(filtered_df)


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
