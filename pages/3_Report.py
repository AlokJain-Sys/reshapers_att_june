from Home import st
import pandas  as pd    
from Home import face_rec
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

with tab3:
    st.subheader('Attendence Report')
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

    logs_df['Timestamp'] = pd.to_datetime(logs_df['Timestamp'])
    logs_df['Date']=logs_df['Timestamp'].dt.date
    
    # step -3.1 : Cal.InTime and Out Time
    #In time: At which person is first deducted in that day (min Timestamp of the Date) 
    #Out time: At which person is last deducted in that day (max Timestamp of the Date) 

    report_df=logs_df.groupby(by=['Date','Name','Role']).agg(
        In_time=pd.NamedAgg('Timestamp',min), #in Time
        Out_time = pd.NamedAgg('Timestamp',max) #out Time
    ).reset_index()

    report_df['In_time'] = pd.to_datetime(report_df['In_time'])
    report_df['Out_time'] = pd.to_datetime(report_df['Out_time'])
    report_df['Duration'] = report_df['Out_time']-report_df['In_time']
        
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
    
    #Duration
    #Hours
date_name_role_zip_df['Duration_seconds'] = date_name_role_zip_df['Duration'].dt.seconds 
date_name_role_zip_df['Duration_hours'] = date_name_role_zip_df['Duration_seconds'] / (60*60)
date_name_role_zip_df['Duration'] = date_name_role_zip_df['Duration'].apply(lambda x: str(x) if pd.notnull(x) else "")  

def status_marker(x):
    if pd.Series(x).isnull().all():
        return 'Absent'
    elif x>= 0 and x< 1 :
        return "Absent(Less than 1 hr)"
    elif x >= 1 and x< 4:
        return 'Half Day(les than 4 Hr)'
    elif x>= 4 and x < 6:  
        return 'Half Day'
    elif x>= 6 and x < 6:  
        return 'Present'
date_name_role_zip_df['Status'] = date_name_role_zip_df['Duration_hours'].apply(status_marker)
    
st.dataframe(date_name_role_zip_df)


#...your import statement

#...your previous tab code
# with tab4:
#     with st.spinner('Retrieving Data From DB..'):
#         redis_face_db = face_rec.retrive_data2(name='contact1:register')

#         st.dataframe(redis_face_db[['Name','Role','Mobile']])