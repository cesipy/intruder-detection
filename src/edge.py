import cv2
import numpy as np
import socketio
import os
import uvicorn
from pathlib import Path
import requests

from yolo_detection import YoloDetection
from config import DEBUGGING, CLOUD_CREDENTIALS_PATH, CLOUD_URL, DETECT_INTRUDER_PATH

class EdgeServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self._setup_events()
        
        weights_path = Path("res/weights")
        weights_path.mkdir(parents=True, exist_ok=True)
        self.person_detection = YoloDetection()
        
    def _setup_events(self):
        @self.sio.event
        async def frame_event(sid, data):
            await self._handle_frame_event(sid, data)
        
    async def trigger_alarm(self, ):
        await self.sio.emit('alarm_event')

    # TODO send further to cloud
    async def process_frame(self, frame_data, frame_name):
        np_arr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        print(f"type of frame in process_frame: {type(frame)}")
        
        files = {
            "img": ("frame.jpg", frame_data, "image/jpeg")  # Match the cloud's expected 'img' key
        }
        data = {
            "device_id": 1      # TODO: fill in device id, but dont think this is really necessary
        }
        
        print(f"trying to connect to {CLOUD_URL}/{DETECT_INTRUDER_PATH}")
        ret = requests.post(
            f"{CLOUD_URL}/{DETECT_INTRUDER_PATH}",        # how to setup ip in docker for this
            files=files, 
            data=data,
            timeout=10,
        )
        if ret.status_code == 200: 
            resonse = ret.json()
            is_intruder_detected = resonse.get("result")
            if is_intruder_detected: 
                print("Intruder detected, sending notification to alarm")
                await self.trigger_alarm()
            
        print(f"response from cloud: {ret}")
        
        
        
        
        
        return
        
    def detect_intruder_test(self, frame_name: str, test_detection_freq: int=100): 
        frame_name = frame_name.split("_")
        frame_name = frame_name[1]
        frame_name = frame_name.replace("frame", "")
        frame_name = frame_name.replace(".jpg", "")
        frame_number = int(frame_name)
        
        if frame_number % test_detection_freq == 0:
            return True

    # TODO use sid to keep track of clients (to notify alarm what camera caught the intruder?)
    async def _handle_frame_event(self, sid, data):
        name = data['frame_name']
        frame = data['data']
        if DEBUGGING:
            print(f'recieved frame {name}')
            # alarm trigger (TESTING)
            # if self.detect_intruder_test(name):
            #     print(f"Intruder detected on video frame: {name}")
            #     await self.trigger_alarm()
                
        
        # save frame to dir ./test-data
        # with open(f"test-data/{name}", 'wb') as f:
        #    f.write(frame)
        
        np_arr = np.frombuffer(frame, np.uint8)
        frame_dec = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        if frame_dec is None:
            print(f"Failed to decode frame: {name}")
            #return
        
        if self.person_detection.analyze_image(frame_dec):
            print("Person detected")
            await self.process_frame(frame, name)       # send to cloud
        else:
            print("Nothing detected")
        
# dir_path = os.path.join('camera_set', 'frames') # (TESTING)
# os.makedirs("test-data", exist_ok=True)



def main():
    edge = EdgeServer()
    
    # wrap the server in asgi server and run it
    app = socketio.ASGIApp(edge.sio)
    uvicorn.run(app, host="0.0.0.0", port=5000)

    # create folder for saving the frames (TESTING)
    #os.makedirs(dir_path, exist_ok=True)


if __name__ == '__main__':
    main()
