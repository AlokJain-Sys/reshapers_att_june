from itertools import islice
import numpy as np
import pandas as pd
import cv2
import redis
# insight face
from insightface.app import FaceAnalysis
from sklearn.metrics import pairwise
# time
import time
from datetime import datetime,date 
import os




# Connect to Redis Client
hostname = 'redis-15743.c93.us-east-1-3.ec2.redns.redis-cloud.com'
portnumber = 15743
password = 'Y2VYMrmEUDMFuugSbtEIbLQ5s4wzATII'

r = redis.StrictRedis(host=hostname,
                      port=portnumber,
                      password=password)

# Retrive Data from database
def retrive_data(name):
    retrive_dict= r.hgetall(name)
    retrive_series = pd.Series(retrive_dict)
    retrive_series = retrive_series.apply(lambda x: np.frombuffer(x,dtype=np.float32))
    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))
    retrive_series.index = index
    retrive_df =  retrive_series.to_frame().reset_index()
    retrive_df.columns = ['name_role','facial_features']
    retrive_df[['Name','Role']] = retrive_df['name_role'].apply(lambda x: x.split('@')).apply(pd.Series)
    return retrive_df[['Name','Role','facial_features']]
## Retrive Data with Mobile,email Hashkey contact
def retrive_data2(name):
    retrive_dict= r.hgetall(name)
    retrive_series = pd.Series(retrive_dict)
    retrive_series = retrive_series.apply(lambda x: np.frombuffer(x,dtype=np.float32))
    index = retrive_series.index
    index = list(map(lambda x: x.decode(), index))
    retrive_series.index = index
    retrive_df =  retrive_series.to_frame().reset_index()
    retrive_df.columns = ['name_role','facial_features']
    retrive_df[['Name','Role','Mobile']] = retrive_df['name_role'].apply(lambda x: x.split('@')).apply(pd.Series)
    return retrive_df[['Name','Role','Mobile','facial_features']]



def retrive_data3(name, *, person_name=None, role=None):  # Make person_name keyword-only
    """
    Retrieves data from the specified Redis hash and formats it into a DataFrame,
    optionally filtered by person_name and/or role.

    Args:
        name (str): The name of the Redis hash.
        person_name (str, optional): The name of the person to filter by. Defaults to None.
        role (str, optional): The role to filter by. Defaults to None.

    Returns:
        pandas.DataFrame: A DataFrame containing the retrieved data with columns 'Name', 'Role', 'Mobile', and 'Email'.
    """
    
    retrive_dict = r.hgetall(name)

    decoded_dict = {}
    for k, v in retrive_dict.items():
        try:
            decoded_key = k.decode('utf-8')
            decoded_value = v.decode('utf-8') if isinstance(v, bytes) else v
            decoded_dict[decoded_key] = decoded_value
        except UnicodeDecodeError:
            print(f"Error decoding key {k} or value {v}. Skipping this entry.")
            continue 

    retrive_df = pd.DataFrame.from_dict(decoded_dict, orient='index').reset_index()
    retrive_df.columns = ['combined_key', 'value']

    # Extract Name and Role from the first two columns of split_values
    retrive_df[['Name', 'Role']] = retrive_df['combined_key'].str.split('@', n=1, expand=True)

    # Extract Mobile and Email from the value, handle cases where they might be missing
    retrive_df[['Mobile','Email']] = retrive_df['value'].astype(str).str.split('@', n=1, expand=True).fillna('') 

    # Filter based on name and role
    if person_name and role:
        retrive_df = retrive_df[(retrive_df['Name'] == person_name) & (retrive_df['Role'] == role)]
    elif person_name:
        retrive_df = retrive_df[retrive_df['Name'] == person_name]
    elif role:
        retrive_df = retrive_df[retrive_df['Role'] == role]

    return retrive_df[['Name', 'Role', 'Mobile','Email']].dropna() 



def retrive_data4(name='contact1:register', *, person_name=None, role=None):
    retrive_dict = r.hgetall(name)

    decoded_dict = {}
    for k, v in retrive_dict.items():
        try:
            decoded_key = k.decode('utf-8')
            decoded_value = v.decode('utf-8') if isinstance(v, bytes) else str(v)
            decoded_dict[decoded_key] = decoded_value
        except UnicodeDecodeError:
            print(f"Error decoding key {k} or value {v}. Skipping this entry.")
            continue 

    retrive_df = pd.DataFrame.from_dict(decoded_dict, orient='index').reset_index()
    retrive_df.columns = ['combined_key', 'value']

    # Splitting combined_key and handling missing values
    split_values = retrive_df['combined_key'].str.split('@', expand=True, n=2)
    # Ensure the DataFrame has at least 2 columns for name and role.
    split_values = split_values.reindex(columns=range(2), fill_value='')

    # Rename columns to appropriate names
    split_values.columns = ['Name', 'Role']
    # Combine the original DataFrame with the extracted columns
    retrive_df = pd.concat([retrive_df, split_values[['Name', 'Role']]], axis=1)

    # Extract Mobile from the value column
    retrive_df['Mobile'] = retrive_df['value'].apply(lambda x: x.split('@')[2] if len(x.split('@')) >= 3 else '') 

    # Filter based on name and role (if provided)
    if person_name and role:
        retrive_df = retrive_df[(retrive_df['Name'] == person_name) & (retrive_df['Role'] == role)]
    elif person_name:
        retrive_df = retrive_df[retrive_df['Name'] == person_name]
    elif role:
        retrive_df = retrive_df[retrive_df['Role'] == role]

    return retrive_df[['Name', 'Role', 'Mobile']].dropna() 
def retrive_data5(name='contact1:register', *, person_name=None, role=None):
    try:
        retrive_dict = r.hgetall(name)
    except redis.exceptions.RedisError as e:
        print(f"Error retrieving data from Redis: {e}")
        return pd.DataFrame(columns=['Name', 'Role', 'Mobile', 'Email'])  # Return empty DataFrame on error
    
    decoded_dict = {}
    for k, v in retrive_dict.items():
        try:
            decoded_key = k.decode('utf-8')
            decoded_value = v.decode('utf-8') if isinstance(v, bytes) else str(v)
            decoded_dict[decoded_key] = decoded_value
        except UnicodeDecodeError:
            print(f"Error decoding key {k} or value {v}. Skipping this entry.")
            continue

    # If the dictionary is empty, create a blank DataFrame with the required columns
    if not decoded_dict:
        retrive_df = pd.DataFrame(columns=['combined_key', 'value'])
    else:
        # Otherwise, create DataFrame from dictionary as before.
        retrive_df = pd.DataFrame.from_dict(decoded_dict, orient='index').reset_index()
        retrive_df.columns = ['combined_key', 'value']
    
    # Extract name, role, mobile from the combined key and value
    retrive_df[['Name', 'Role', 'Mobile', 'Email']] = retrive_df['combined_key'].str.split('@', expand=True, n=3).fillna('')

    # Filter based on name and role (if provided)
    if person_name and role:
        retrive_df = retrive_df[(retrive_df['Name'] == person_name) & (retrive_df['Role'] == role)]
    elif person_name:
        retrive_df = retrive_df[retrive_df['Name'] == person_name]
    elif role:
        retrive_df = retrive_df[retrive_df['Role'] == role]

    return retrive_df[['Name', 'Role', 'Mobile', 'Email']].dropna()


def check_duplicates2(name, role, mobile):
        
        existing_keys = r.hkeys('contact1:register')
        for key in existing_keys:
            key_str = key.decode('utf-8')
            existing_name, existing_role, existing_mobile = key_str.split('@')
            if name == existing_name and role == existing_role and mobile == existing_mobile:
                return True  # Duplicate found
        return False  # No duplicate found




def rename_hash_key(old_key, new_key, hash_name='contact1:register'):
    """
    Renames a hash key in Redis, keeping the values unchanged.

    Args:
        old_key (str): The existing key to rename.
        new_key (str): The new name for the key.
        hash_name (str): The name of the Redis hash to operate on (defaults to 'contact1:register').
    """
    try:
        # 1. Check if the old_key belongs to the specified hash
        if not old_key.startswith(hash_name):
            raise ValueError(f"Key '{old_key}' does not belong to hash '{hash_name}'")

        # 2. Get the value associated with the old key
        value = r.hget(old_key)

        # 3. If the key exists, delete it and set the value with the new key
        if value is not None:
            r.delete(old_key)
            r.hset(new_key, value)
            print(f"Key '{old_key}' renamed to '{new_key}' successfully.")
            # update attendance log
            for i, log in enumerate(r.lrange('attendance:logs', 0, -1)):
                log_str = log.decode('utf-8')
                if log_str.startswith(old_key):
                    new_log = log_str.replace(old_key, new_key)
                    r.lset('attendance:logs', i, new_log)
        else:
            print(f"Key '{old_key}' not found.")

    except redis.exceptions.RedisError as e:
        print(f"An error occurred: {e}")











# configure face analysis
faceapp = FaceAnalysis(name='buffalo_sc',root='insightface_model', providers = ['CPUExecutionProvider'])
faceapp.prepare(ctx_id = 0, det_size=(640,640), det_thresh = 0.5)

# ML Search Algorithm
def ml_search_algorithm(dataframe,feature_column,test_vector,
                        name_role=['Name','Role'],thresh=0.5):
    """
    cosine similarity base search algorithm
    """


    # step-1: take the dataframe (collection of data)
    dataframe = dataframe.copy()
    # step-2: Index face embeding from the dataframe and convert into array
    X_list = dataframe[feature_column].tolist()
    x = np.asarray(X_list)
    
    # step-3: Cal. cosine similarity
    similar = pairwise.cosine_similarity(x,test_vector.reshape(1,-1))
    similar_arr = np.array(similar).flatten()
    dataframe['cosine'] = similar_arr

    # step-4: filter the data
    data_filter = dataframe.query(f'cosine >= {thresh}')
    if len(data_filter) > 0:
        # step-5: get the person name
        data_filter.reset_index(drop=True,inplace=True)
        argmax = data_filter['cosine'].argmax()
        person_name, person_role = data_filter.loc[argmax][name_role]
        
    else:
        person_name = 'Unknown'
        person_role = 'Unknown'
        
    return person_name, person_role


## Real Time Prediction
#we need to save logs for every 1 mins
class RealTimePred:
    
    def __init__(self, rtsp_url="rtsp://admin:ab@123456@122.160.10.254/Streaming/Channels/101"):
        self.logs = dict(name=[], role=[], current_time=[])
        self.rtsp_url = rtsp_url  # Store the RTSP URL
        self.cap = cv2.VideoCapture(rtsp_url) # Get video feed from the RTSP URL
        self.cap.set(cv2.CAP_PROP_BITRATE, 1500000)
    
    def reset_dict(self):
        self.logs = dict(name=[],role=[],current_time=[])
    def __init__(self):
        self.logs = dict(name=[],role=[],current_time=[])
        
    def reset_dict(self):
        self.logs = dict(name=[],role=[],current_time=[])
        
    def saveLogs_redis(self):
        # step-1: create a logs dataframe
        dataframe = pd.DataFrame(self.logs)        
        # step-2: drop the duplicate information (distinct name)
        dataframe.drop_duplicates('name',inplace=True) 
        # step-3: push data to redis database (list)
        # encode the data
        name_list = dataframe['name'].tolist()
        role_list = dataframe['role'].tolist()
        ctime_list = dataframe['current_time'].tolist()
        encoded_data = []
        for name, role, ctime in zip(name_list, role_list, ctime_list):
            if name != 'Unknown':
                concat_string = f"{name}@{role}@{ctime}"
                encoded_data.append(concat_string)
                
        if len(encoded_data) >0:
            r.lpush('attendance:logs',*encoded_data)
        
                    
        self.reset_dict()     


    
    def face_prediction(self,test_image, dataframe,feature_column,
                            name_role=['Name','Role'],thresh=0.5):
        # step-1: find the time
        current_time = str(datetime.now())
        
        # step-1: take the test image and apply to insight face
        results = faceapp.get(test_image)
        test_copy = test_image.copy()
        #Seen_today for SMS
        today = date.today()
        seen_today = set()  # Track who has been seen today

        # step-2: use for loop and extract each embedding and pass to ml_search_algorithm

        for res in results:
            x1, y1, x2, y2 = res['bbox'].astype(int)
            embeddings = res['embedding']
            if res['det_score']< 0.7 : continue
            person_name, person_role = ml_search_algorithm(dataframe,
                                                        feature_column,
                                                        test_vector=embeddings,
                                                        name_role=name_role,
                                                        thresh=thresh)
            
                        #Send SMS only if this is the first time the person is detected today
        

            
            if person_name not in seen_today:
                #self.send_sms(person_name, person_role,current_time)
                #seen_today.add(person_name)
                pass
            if person_name == 'Unknown':
                color =(0,0,255) # bgr
            else:
                color = (0,255,0)

            cv2.rectangle(test_copy,(x1,y1),(x2,y2),color)

            text_gen = person_name
            cv2.putText(test_copy,text_gen,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
            cv2.putText(test_copy,current_time,(x1,y2+10),cv2.FONT_HERSHEY_DUPLEX,0.7,color,2)
            # save info in logs dict
            self.logs['name'].append(person_name)
            self.logs['role'].append(person_role)
            self.logs['current_time'].append(current_time)
            

        return test_copy



    



#### Registration Form
class RegistrationForm:
    def __init__(self):
        self.sample = 0
    def reset(self):
        self.sample = 0
        
    def get_embedding(self,frame):
        # get results from insightface model
        results = faceapp.get(frame,max_num=1)
        embeddings = None
        for res in results:
            self.sample += 1
            x1, y1, x2, y2 = res['bbox'].astype(int)
            cv2.rectangle(frame, (x1,y1),(x2,y2),(0,255,0),1)
            # put text samples info
            text = f"samples = {self.sample}"
            cv2.putText(frame,text,(x1,y1),cv2.FONT_HERSHEY_DUPLEX,0.6,(255,255,0),2)
            
            # facial features
            embeddings = res['embedding']
            
        return frame, embeddings
    
    
    def save_data_in_redis_db(self,name,role,mobile,email):
        # validation name
        if name is not None:
            if name.strip() != '':
                key = f'{name}@{role}@{mobile}'
            else:
                return 'name_false'
        else:
            return 'name_false'
        
        # if face_embedding.txt exists
        if 'face_embedding.txt' not in os.listdir():
            return 'file_false'
        
        
        # step-1: load "face_embedding.txt"
        x_array = np.loadtxt('face_embedding.txt',dtype=np.float32) # flatten array            
        
        # step-2: convert into array (proper shape)
        received_samples = int(x_array.size/512)
        x_array = x_array.reshape(received_samples,512)
        x_array = np.asarray(x_array)       
        
        # step-3: cal. mean embeddings
        x_mean = x_array.mean(axis=0)
        x_mean = x_mean.astype(np.float32)
        x_mean_bytes = x_mean.tobytes()
        
        # step-4: save this into redis database
        # redis hashes
        r.hset(name='contact1:register',key=key,value=x_mean_bytes)
        #r.hset('contact:register', key=key, value=mobile)
        #r.hset('contact:register', key=key, value=email)



        # 
        os.remove('face_embedding.txt')
        self.reset()
        
        return True
    def check_duplicates(self, name, role, mobile):
        existing_keys = r.hkeys('contact1:register')
        for key in existing_keys:
            key_str = key.decode('utf-8')
            existing_name, existing_role, existing_mobile = key_str.split('@')
            if name == existing_name and role == existing_role and mobile == existing_mobile:
                return True  # Duplicate found
        return False  # No duplicate found

