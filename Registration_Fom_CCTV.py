# registration_form.py
import cv2
from insightface.app import FaceAnalysis
import numpy as np
import redis
import os
from face_rec import r as rcctv
#from dotenv import load_dotenv

#load_dotenv()

# Connect to Redis Client
# hostname = os.getenv("REDIS_HOSTNAME")  
# portnumber = int(os.getenv("REDIS_PORT")) 
# password = os.getenv("REDIS_PASSWORD") 

# r = redis.StrictRedis(host=hostname,
#                       port=portnumber,
#                       password=password,
#                       decode_responses=True)

# Configure face analysis
faceapp = FaceAnalysis(name='buffalo_sc', root='insightface_model', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
faceapp.prepare(ctx_id=0, det_size=(640, 640), det_thresh=0.5)

class RegistrationForm:
    def __init__(self, rtsp_url="rtsp://admin:ab@123456@122.160.10.254/Streaming/Channels/101"):
        self.sample = 0
        self.rtsp_url = rtsp_url
        self.cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)  
        if not self.cap.isOpened():
            raise RuntimeError(f"Error opening RTSP stream from {rtsp_url}")

        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 3)

    def reset(self):
        self.sample = 0

    def get_embedding(self):
        """Captures frames from the RTSP stream, detects blinks, and gets embeddings."""

        blink_frames_required = 3  # You can adjust this value
        blink_count = 0

        while blink_count < blink_frames_required:
            ret, frame = self.cap.read()
            # print(f"ret is: {ret}")
            # print(f"frame is {frame}")
            if not ret:
                print("Error: Failed to capture frame from camera.")
                continue  # Skip to the next iteration if frame reading fails

            results = faceapp.get(frame, max_num=1)  # Get face analysis results
            embeddings = None

            if results:  # Check if any faces were detected
                for res in results:
                    if self.is_blinking(res):
                        blink_count += 1
                        # Visual feedback (optional)
                        cv2.putText(frame, f"Blink detected: {blink_count}/{blink_frames_required}", 
                                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                    if blink_count >= blink_frames_required:
                        self.sample += 1
                        x1, y1, x2, y2 = res['bbox'].astype(int)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)

                        # Put text (sample info)
                        text = f"samples = {self.sample}"
                        cv2.putText(frame, text, (x1, y1), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 0), 2)
                        embeddings = res['embedding']
                        return frame, embeddings

            cv2.imshow('Registration', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        return None, None  # No blinks detected within the limit

    def save_data_in_redis_db(self, name, role, mobile, email):
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
        x_array = np.loadtxt('face_embedding.txt', dtype=np.float32)  # flatten array

        # step-2: convert into array (proper shape)
        received_samples = int(x_array.size / 512)
        x_array = x_array.reshape(received_samples, 512)
        x_array = np.asarray(x_array)

        # step-3: cal. mean embeddings
        x_mean = x_array.mean(axis=0)
        x_mean = x_mean.astype(np.float32)
        x_mean_bytes = x_mean.tobytes()

        # step-4: save this into redis database
        rcctv.hset(name='contact1:register', key=key, value=x_mean_bytes)

        # Store additional details (role and mobile)
        rcctv.hset('contact1:register', f'{key}:role', role)
        rcctv.hset('contact1:register', f'{key}:mobile', mobile)
        rcctv.hset('contact1:register', f'{key}:email', email)  # Store email as well
        
        # Cleanup
        os.remove('face_embedding.txt')
        self.reset()

        return True

    def check_duplicates(self, name, role, mobile):
        existing_keys = rcctv.hkeys('contact1:register')
        for key in existing_keys:
            key_str = key.decode('utf-8')
            existing_name, existing_role, existing_mobile = key_str.split('@')
            if name == existing_name and role == existing_role and mobile == existing_mobile:
                return True  # Duplicate found
        return False  # No duplicate found
