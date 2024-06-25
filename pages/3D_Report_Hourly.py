# from Home import st
# import pandas  as pd    
# from Home import face_rec
# from PIL import Image
# from utils import set_page_config

# set_page_config()
# #tab1=st.tabs('Hourly Attendence Report')
# (tab1,) = st.tabs(['Hourly Attendance Report'])

# #Retrive log data and show in Report.py 
# #extraxt Data from redis list 
# name = 'attendance:logs'
# def load_logs(name,end=-1) :
#     logs_list=face_rec.r.lrange(name,start=0,end=end) # extract all data from the database 
#     return logs_list
# #Tabs to show the Info 

# with tab1:
#     st.subheader('Attendance Report Hourly')
#     #Load logs into attribute log_list 
#     logs_list= load_logs(name=name)
#     #step 1: convert the logs that in list of bytes into list of strings 
#     convert_byte_to_string= lambda x: x.decode('utf-8')
#     logs_list_string = list(map(convert_byte_to_string,logs_list))
    
#     #step- 2: split  string by @ and create nested list 
#     split_string = lambda x: x.split('@')
#     logs_nested_list= list(map(split_string,logs_list_string))       
#     # convert nested list info into dataframe 

#     logs_df = pd.DataFrame(logs_nested_list,columns=['Name','Role','Timestamp'])       
#     # Step -3 Time Based Analysis or Report 

#     logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
#     logs_df['Date']=logs_df['Timestamp'].dt.date
    

   
#     # Calculate duration before formatting
#     # Define hours for filtering
#    # ... (your other imports and code)


# with tab1:
#     # ... (load and preprocess logs_df as before) ...

#     start_hour = 5
#     end_hour = 22
#     filtered_logs_df = logs_df[
#         (logs_df['Timestamp'].dt.hour >= start_hour) & (logs_df['Timestamp'].dt.hour <= end_hour)
#     ]


#     def process_hourly_logs(group):
#         # Create In_Time and Out_Time columns
#         group['In_Time'] = group['Timestamp'].dt.strftime('%I:%M %p')
#         group['Out_Time'] = group['In_Time'].shift(-1)
        
#         # Reset Index
#         group = group.reset_index()

#         # Create a new column to keep track of entry/exit pairs within the hour
#         group['PairIndex'] = group.groupby(['Date', 'Name', 'Role', 'Hour']).cumcount() // 2
        
#         # Pivot to get multiple In_Time and Out_Time columns
#         pivoted = group.pivot(index=['Date', 'Name', 'Role', 'Hour'], columns='PairIndex', values=['In_Time', 'Out_Time'])
        
#         # Flatten column MultiIndex
#         pivoted.columns = [f'{col[0]}_{col[1]+1}' for col in pivoted.columns]

#         return pivoted.reset_index()


#     # Group by date, name, role, and hour, then apply the processing function
#     hourly_report_df = (
#         filtered_logs_df.groupby(['Date', 'Name', 'Role', pd.Grouper(key='Timestamp', freq='H')])
#         .apply(process_hourly_logs)
#         .reset_index(drop=True)
#     )


#     # Display and download
#     if not hourly_report_df.empty:
#         hourly_report_df['Date'] = pd.to_datetime(hourly_report_df['Date']).dt.strftime('%d/%b/%Y')
#         st.dataframe(hourly_report_df)
#     else:
#         st.warning("No hourly data found for the selected filter.")
