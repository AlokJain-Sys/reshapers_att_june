from Home import st
from Home import face_rec
from streamlit_webrtc import webrtc_streamer
import pandas as pd
import time
import datetime
import redis
import json

st.title("Registerd Data Management")

#set_page_config()

tab1,tab2=st.tabs(['Registered Data','Logs'])
# --- Streamlit Page Structure ---
def get_redis_data():
        all_data = face_rec.r.hgetall('contact1:register')
        return all_data
with tab1:
    
    # --- Function to Retrieve Redis Data ---
    

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

with tab2:
    def load_logs(name, end=-1):
        logs_list = face_rec.r.lrange(name, start=0, end=end)
        return [item.decode("utf-8") for item in logs_list] 
    
   
    def tab2():
        name = 'attendance:logs'
        
        logs_list = load_logs(name)
        logs_data = [json.loads(log) for log in logs_list] 
        logs_df = pd.DataFrame(logs_data)
        st.dataframe(logs_df) 
        
        try:
            logs_df = pd.DataFrame(logs_list)

            # Advanced Filtering 
            all_names = sorted(logs_df["Name"].unique())
            all_roles = sorted(logs_df["Role"].unique())

            # Name and Role Filters
            selected_name = st.selectbox("Select Name", all_names)
            selected_role = st.selectbox("Select Role", all_roles)

            # Date Range Filter
            start_date = st.date_input("Start Date", datetime.today().date())
            end_date = st.date_input("End Date", datetime.today().date())

            # Apply Filters
            filtered_df = logs_df[
                (logs_df['Name'] == selected_name) &
                (logs_df['Role'] == selected_role) &
                (logs_df['timestamp'] >= pd.Timestamp(start_date)) &
                (logs_df['timestamp'] <= pd.Timestamp(end_date))
            ]

            st.write("Filtered Logs:")
            st.write(filtered_df)

            if st.button('Delete Logs for Selected User and Role'):
                # Log Confirmation Dialog
                if st.checkbox("I confirm that I want to delete these logs."):
                    keys_to_delete = face_rec.r.keys(f"attendance:logs:{selected_role}:{selected_name}:*")
                    filtered_keys = [key for key in keys_to_delete]

                    if filtered_keys:
                        face_rec.r.delete(*filtered_keys)  
                        st.success("Logs for the selected user and role deleted successfully!")
                    else:
                        st.warning("No logs found for the selected user and role.")
                else:
                    st.warning("Please confirm deletion by checking the box.")

        except Exception as e:
            st.warning(f"Error processing logs: {e}")  # More general error message
            
            
'''
 Approach: Combining HSCAN and HSET

HSCAN:  Use the HSCAN command to iterate through the fields 
and values within your hash. This allows you to search for the 
entry that matches your criteria.

Conditional Update:  Inside the HSCAN loop, check if the current 
entry matches the provided name and role. If it does, use the 
HSET command to update the phone field.
 
 '''           
# import redis

# def update_phone_by_name_and_role(redis_conn, hash_key, target_name, target_role, new_phone):
#     cursor = 0
#     while True:
#         cursor, data = redis_conn.hscan(hash_key, cursor)
#         for field, value in data.items():
#             if field == b'name' and value.decode() == target_name and redis_conn.hget(hash_key, b'role').decode() == target_role:
#                 redis_conn.hset(hash_key, "phone", new_phone)
#                 return True  # Indicate successful update
#         if cursor == 0:
#             break
#     return False  # No matching entry found


# # Example Usage
# r = redis.Redis()  # Connect to Redis
# hash_key = "contact1:register"
# target_name = "Alice"
# target_role = "admin"
# new_phone = "987-654-3210"

# if update_phone_by_name_and_role(r, hash_key, target_name, target_role, new_phone):
#     print("Phone number updated successfully!")
# else:
#     print("No matching contact found for the given name and role.")
