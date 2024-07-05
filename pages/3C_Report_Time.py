from Home import st
import pandas  as pd    
from Home import face_rec
from PIL import Image
from utils import set_page_config

set_page_config()
st.subheader('Reporting')

#Retrive log data and show in Report.py 
#extraxt Data from redis list 
name = 'attendance:logs'
def load_logs(name,end=-1) :
    logs_list=face_rec.r.lrange(name,start=0,end=end) # extract all data from the database 
    return logs_list
#Tabs to show the Info 
tab1,tab2,tab3=st.tabs(['Registered Data','Logs','Attendence Report'])

with tab1:
        if st.button('Refresh Data'):
        # Retrive the data from Redis Database
            with st.spinner('Retriving Data from Redis DB ...'):    
                redis_face_db = face_rec.retrive_data2(name='contact1:register')
                st.dataframe(redis_face_db[['Name','Role','Mobile']])
with tab2:
    if st.button('Refresh Logs'):
        st.write(load_logs(name=name))

# ... other imports ...

with tab3:
    st.subheader('Attendance Report')
    #Load logs into attribute log_list 
    logs_list= load_logs(name=name)
    #step 1: convert the logs that in list of bytes into list of strings 
    convert_byte_to_string= lambda x: x.decode('utf-8')
    logs_list_string = list(map(convert_byte_to_string,logs_list))
    
    #step- 2: split  string by @ and create nested list 
    split_string = lambda x: x.split('@')
    logs_nested_list= list(map(split_string,logs_list_string))       
    # convert nested list info into dataframe 

    logs_df = pd.DataFrame(logs_nested_list,columns=['Name','Role','Timestamp'])       
    # Step -3 Time Based Analysis or Report 

    logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'], format='ISO8601')
    logs_df['Date']=logs_df['Timestamp'].dt.date
    
    # step -3.1 : Cal.InTime and Out Time
     
    report_df=logs_df.groupby(by=['Date','Name','Role']).agg(
        In_Time=pd.NamedAgg('Timestamp',min), #in Time
        Out_Time = pd.NamedAgg('Timestamp',max) #out Time
    ).reset_index()
    #Below - Future Code for aggigation for panda  
#     report_df = logs_df.groupby(by=['Date', 'Name', 'Role']).agg(
#     First_Time=('Time', 'min'),  # Changed to string 'min'
#     Last_Time=('Time', 'max')   # Changed to string 'max'
# )
    
    # Calculate duration before formatting
    report_df['Duration'] = report_df['Out_Time'] - report_df['In_Time']

    # Format In_time and Out_time immediately after aggregation
    report_df['In_Time'] = report_df['In_Time'].dt.strftime('%I:%M %p')
    report_df['Out_Time'] = report_df['Out_Time'].dt.strftime('%I:%M %p')

    #Step 4: Marking Person is present or absent
    all_dates=report_df['Date'].unique()
    name_role= report_df[['Name','Role']].drop_duplicates().values.tolist()

    date_name_role_zip=[]
    for dt in all_dates:
        for name,role in name_role:
            date_name_role_zip.append([dt,name,role])
                
    
    date_name_role_zip_df =pd.DataFrame(date_name_role_zip,columns=['Date','Name','Role'])
    #left join  with report_df
    date_name_role_zip_df= pd.merge(date_name_role_zip_df,report_df,how='left',on=['Date','Name','Role'])
    
    
    #Duration_seconds and Duration_hours Calculation
    date_name_role_zip_df['Duration_seconds'] = date_name_role_zip_df['Duration'].dt.seconds 
    date_name_role_zip_df['Duration_hours'] = date_name_role_zip_df['Duration_seconds'] / (60*60)

    # Fill NaN values in Duration to avoid error while formatting in the next step.
    date_name_role_zip_df['Duration'] = date_name_role_zip_df['Duration'].fillna(pd.Timedelta(seconds=0))

    # Format Duration to HH:MM:SS
    date_name_role_zip_df['Duration'] = date_name_role_zip_df['Duration'].apply(lambda x: f"{x.components.hours:02d}:{x.components.minutes:02d}:{x.components.seconds:02d}")  

    # Function to mark attendance status
    def status_marker(x):
        """Assigns an attendance status based on the duration in hours."""
        if pd.isnull(x):
            return 'Absent'
        elif x>= 0 and x< 1 :
            return "Absent(Less than 1 hr)"
        elif x >= 1 and x< 4:
            return 'Half Day(les than 4 Hr)'
        elif x>= 4 and x < 8:  
            return 'Half Day'
        else: 
            return 'Present'

    date_name_role_zip_df['Status'] = date_name_role_zip_df['Duration_hours'].apply(status_marker)


    # Display Filtered Data
    if not date_name_role_zip_df.empty:
        # Format Date column (DD/MMM/YYYY)
        date_name_role_zip_df['Date'] = pd.to_datetime(date_name_role_zip_df['Date']).dt.strftime('%d/%b/%Y')

        st.dataframe(date_name_role_zip_df[['Name','Role','Date','In_Time','Out_Time','Duration','Status']]) #Corrected Line

        # --- Download Button ---
        csv = date_name_role_zip_df.to_csv(index=False)
        st.download_button(
            label="Download Data as CSV",
            data=csv,
            file_name=f"attendance_report.csv",
            mime="text/csv",
        )
    else:
        st.warning("No data found for the selected filter.")

