import cv2
import numpy as np
import socketio
from datetime import datetime

import uvicorn
from pathlib import Path
import requests

from yolo_detection import YoloDetection
from config import *
from logger import Logger

logger = Logger()

class EdgeServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self._setup_events()
        
        weights_path = Path("res/weights")
        weights_path.mkdir(parents=True, exist_ok=True)
        self.person_detection = YoloDetection()
        
        self.total_cloud_requests = 0
        self.intruder_counter= 0
        
        # yolo
        self.yolo_request = 0
        self.yolo_person_detected = 0
        
        self.frames_received = 0
        
    def _setup_events(self):
        @self.sio.event
        async def frame_event(sid, data):
            await self._handle_frame_event(sid, data)
        
    async def trigger_alarm(self, ):
        await self.sio.emit('alarm_event')


    async def process_frame(self, frame_data: bytes, frame_name):
        self.total_cloud_requests +=1
        files = {
            "img": ("frame.jpg", frame_data, "image/jpeg")      # frame data is in bytes, so this is transfered in bytes to the cloud
        }
        data = {
            "device_id": 1      # TODO: fill in device id, but dont think this is really necessary
        }
        
        #print(f"trying to connect to {CLOUD_URL}/{DETECT_INTRUDER_PATH}")
        ret = requests.post(
            f"{CLOUD_URL}/{DETECT_INTRUDER_PATH}",        # how to setup ip in docker for this
            files=files, 
            data=data,
            timeout=10,
        )
        if ret.status_code == 200: 
            resonse = ret.json()
            is_intruder_detected = resonse.get("result")
            logger.info(f"response from cloud: {resonse}, is_intruder_detected: {is_intruder_detected}")

            if is_intruder_detected: 
        
                logger.info("Intruder detected, sending notification to alarm")
                
                # for debugging - are the frames correct?
                debug_dir = Path("debug_frames")
                debug_dir.mkdir(exist_ok=True)
                
                # Convert bytes to numpy array and decode
                np_arr = np.frombuffer(frame_data, np.uint8)
                frame_decoded = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                
  
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                frame_path = debug_dir / f"intruder_{timestamp}.jpg"
                
                #save as jpg
                cv2.imwrite(str(frame_path), frame_decoded, [cv2.IMWRITE_JPEG_QUALITY, 95])

                self.intruder_counter +=1

                logger.info(f"current ratio of intruders and requests: {self.intruder_counter/self.total_cloud_requests}")
                logger.info(f"total intruder detected: {self.intruder_counter}, total requests: {self.total_cloud_requests}")
                
                await self.trigger_alarm()
            
        #print(f"response from cloud: {ret}")
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
        self.frames_received += 1
        logger.info(f"frames received: {self.frames_received}")
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
            logger.error(f"Failed to decode frame: {name}")
            #return
        
        self.yolo_request +=1
        if self.person_detection.analyze_image(frame_dec):
            print("Person detected")
            logger.info("Person detected")
            self.yolo_person_detected += 1
            
            logger.info(f"Yolo detection ratio: {self.yolo_person_detected/self.yolo_request}")
            logger.info(f"yolo_person_detected: {self.yolo_person_detected}, yolo_request: {self.yolo_request}")
            
            await self.process_frame(frame, name)       # send to cloud
        else:
            print("Nothing detected")
            logger.info("Nothing detected")
        



def main():
    edge = EdgeServer()
    
    # wrap the server in asgi server and run it
    app = socketio.ASGIApp(edge.sio)
    uvicorn.run(app, host="0.0.0.0", port=UVICORN_PORT)

    # create folder for saving the frames (TESTING)
    #os.makedirs(dir_path, exist_ok=True)


if __name__ == '__main__':
    main()
