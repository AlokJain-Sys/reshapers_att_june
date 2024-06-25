from Home import face_rec ,st
import re
from utils import set_page_config

set_page_config()



def validate_mobile(mobile):
    pattern = r"^\d{10}$"  # Assuming 10-digit mobile number
    return bool(re.match(pattern, mobile))

def update_mobile_number():
    st.title("Update Mobile Number")
    
    # Retrieve all data from Redis
    all_data = face_rec.retrive_data2(name='contact1:register')

    if all_data.empty:
        st.error("No registered users found. Please register users first.")
        return

    # Combine Name and Role into a display string for the selectbox
    all_data['Combined Name'] = all_data['Name'] + ' (' + all_data['Role'] + ')' + ' (' + all_data['Mobile'] + ')'
    all_names_roles = all_data['Combined Name'].tolist()
    selected_person = st.selectbox("Select Person:", all_names_roles)

    if selected_person:
        # Extract the Name and Role from the selected string
        selected_name = selected_person.split(' (')[0]
        selected_role = selected_person.split(' (')[1][:-1]
        selected_mobile = selected_person.split(' (')[2][:-1]  # Remove the closing parenthesis
        role=selected_role
        name=selected_name
        mobile=selected_mobile
        # Fetch existing data for the selected person
        #selected_person_data = face_rec.retrive_data2(name)

        # Handle case where no matching user is found
        

        current_mobile = mobile  # Get as string

        new_mobile = st.text_input("Enter New Mobile Number:", value=current_mobile)

        if not validate_mobile(new_mobile):
            st.error("Please enter a valid 10-digit mobile number.")
        else:
            if st.button("Update Mobile Number"):
                        dup_chk=face_rec.check_duplicates2(selected_name, role, new_mobile)
        
                        if  dup_chk == False:
                                    
                                    old_key = f"{selected_name}@{role}@{current_mobile}"
                                    new_key = f"{selected_name}@{role}@{new_mobile}"

                                    # Rename the hash key, specifying the hash name
                                    face_rec.rename_hash_key(old_key, new_key, hash_name='contact1:register')
                                    st.success("Mobile number updated successfully!")    
                                    
                                    # Update the keys in the attendance logs
                                    for i, log in enumerate(face_rec.r.lrange('attendance:logs', 0, -1)):
                                        log_str = log.decode('utf-8')
                                        if log_str.startswith(old_key):
                                            new_log = log_str.replace(old_key, new_key)
                                            face_rec.r.lset('attendance:logs', i, new_log)
                                    st.success("Logs updated successfully!")
                                        # Refresh all_data to reflect changes
                                        #all_data = face_rec.retrive_data2(name)
                        else: st.error("Mobile number already exists for another person.")

            
            
            
    else:
        st.write("Select a person to update their mobile number.")



def main():
    update_mobile_number()

if __name__ == "__main__":
    main()




# def validate_mobile(mobile):
#     pattern = r"^\d{10}$"  # Assuming 10-digit mobile number
#     return bool(re.match(pattern, mobile))



# # ... (your existing update_mobile_number function)

# if st.button("Update Mobile Number"):
#     if face_rec.check_mobile_exists(new_mobile, selected_name):
#         st.error("Mobile number already exists for another person.")
#     else:
#         old_key = f"{selected_name}@{current_role}@{current_mobile}"
#         new_key = f"{selected_name}@{current_role}@{new_mobile}"  
        
#         # Rename the hash key in Redis
#         face_rec.rename_hash_key(old_key, new_key)
        
#         # Also update the keys in logs list for consistent log management
#         for i, log in enumerate(face_rec.r.lrange('attendance:logs', 0, -1)):
#             log_str = log.decode('utf-8')
#             if log_str.startswith(old_key):
#                 new_log = log_str.replace(old_key, new_key)
#                 face_rec.r.lset('attendance:logs', i, new_log)

#         # Refresh all_data to reflect changes
#         all_data = face_rec.retrive_data4()
#         st.success("Mobile number updated successfully!")



# # def update_mobile_number():
# #     st.title("Update Mobile Number")

# #     all_data = face_rec.retrive_data4()
# #     if all_data.empty:
# #         st.error("No registered users found. Please register users first.")
# #         return

# #     # Create a list of names to display in the selectbox
# #     all_names = all_data['Name'].unique().tolist()
# #     selected_name = st.selectbox("Select Person:", all_names)

# #     if selected_person:
# #         # Fetch existing data for the selected person
# #         selected_person_data = face_rec.retrive_data4(person_name=selected_name)
# #         current_role = selected_person_data['Role'].iloc[0]
# #         current_mobile = selected_person_data['Mobile'].iloc[0]
        
# #         # Input for new mobile number with validation
# #         new_mobile = st.text_input("Enter New Mobile Number:", value=current_mobile)
# #         if not validate_mobile(new_mobile):
# #             st.error("Please enter a valid 10-digit mobile number.")
# #         else:
# #             if st.button("Update Mobile Number"):
# #                 # Check for duplicates
# #                 if face_rec.check_mobile_exists(new_mobile, selected_name):
# #                     st.error("Mobile number already exists for another person.")
# #                 else:
# #                     # Update the Redis key and value
# #                     old_key = f"{selected_name}@{current_role}@{current_mobile}"
# #                     new_key = f"{selected_name}@{current_role}@{new_mobile}"  
# #                     old_value = face_rec.r.hget('contact1:register', old_key)
# #                     if old_value is not None:
# #                         face_rec.r.hdel('contact1:register', old_key)  # Delete the old key
# #                         face_rec.r.hset('contact1:register', new_key, old_value)  # Set the new key
# #                         st.success("Mobile number updated successfully!")
# #                     else:
# #                         st.error("An unexpected error occurred while updating the mobile number.")
# #     else:
# #         st.write("Select a person to update their mobile number.")

# # def main():
# #     update_mobile_number()

# # if __name__ == "__main__":
# #     main()