import cv2
import numpy as np
import socketio
from datetime import datetime
import time

import uvicorn
from pathlib import Path
import requests

from yolo_detection import YoloDetection
from config import *
from logger import Logger

import asyncio

from collections import deque

logger = Logger()

class EdgeServer:
    def __init__(self):
        self.sio = socketio.AsyncServer(async_mode="asgi")
        self._setup_events()
        
        weights_path = Path("res/weights")
        weights_path.mkdir(parents=True, exist_ok=True)
        self.person_detection = YoloDetection(model_type=YOLO_MODEL_SIZE)
        
        # deque for faster efficiency in comparision to list
        # we have a lot of frames in the buffer -> up to 10000 or even more in theoretical production lol
        self.frame_buffer = asyncio.Queue()
        
        self.total_cloud_requests = 0
        self.intruder_counter= 0
        
        # yolo
        self.yolo_request = 0
        self.yolo_person_detected = 0
        self.frames_received = 0
        self.worker_task = None
        
        if EVALUATION:
            # this package was created with major help from copilot to make metrics collection easier. 
            # not needed in the final code
            from metrics_collector import MetricsCollector
            self.metrics = MetricsCollector(n=5)
      
        
    def _setup_events(self):
        @self.sio.event
        async def connect(sid, environ):
            logger.info(f"Client connected: {sid}")
            if not hasattr(self, 'worker_task') or self.worker_task is None:
                self.worker_task = asyncio.create_task(self.process_frame_buffer())
            
    
        @self.sio.event
        async def frame_event(sid, data):
            await self._handle_frame_event(sid, data)
            
    async def trigger_alarm(self, ):
        await self.sio.emit('alarm_event')
        
    async def send_frame_to_cloud(self, frame_data: bytes, frame_name):
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

            if DEMO: 
                print(f"response from cloud: {resonse}, is_intruder_detected: {is_intruder_detected}")
            
            if is_intruder_detected: 
        
                logger.info("Intruder detected, sending notification to alarm")
                if not DEMO:
                    print("Rekognition response: Intruder detected, sending notification to alarm")
                
                # for debugging - are the frames correct?
                debug_dir = Path("debug_frames")
                debug_dir.mkdir(exist_ok=True)
                
                
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                frame_path = debug_dir / f"intruder_{timestamp}.jpg"
                
                # with open(str(frame_path), 'wb') as f:
                #     f.write(frame_data)
                self.intruder_counter +=1
                
                await self.trigger_alarm()
            logger.info(f"current ratio of intruders and requests: {self.intruder_counter/self.total_cloud_requests}")
            logger.info(f"total intruder detected: {self.intruder_counter}, total requests: {self.total_cloud_requests}")
        return
        
    def detect_intruder_test(self, frame_name: str, test_detection_freq: int=100): 
        frame_name = frame_name.split("_")
        frame_name = frame_name[1]
        frame_name = frame_name.replace("frame", "")
        frame_name = frame_name.replace(".jpg", "")
        frame_number = int(frame_name)
        
        if frame_number % test_detection_freq == 0:
            return True
        

    async def process_frame_buffer(self):
        while True: 
            if not  self.frame_buffer.empty(): 
                #async get the next element in the buffer
                data = await self.frame_buffer.get()
                name = data['frame_name']
                frame = data['data']
                process_start = time.time()
                
                try: 
                    np_arr = np.frombuffer(frame, np.uint8)
                    frame_dec = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    
                    if frame_dec is None:
                        print(f"Failed to decode frame: {name}")
                        logger.error(f"Failed to decode frame: {name}")
                    
                    self.yolo_request +=1
                    person_detected = False
                    
                    person_detected, persons_images = self.person_detection.analyze_image(
                        image=frame_dec,
                        confidence_threshold=YOLO_CONFIDENCE_THRESHOLD,
                    )
                    
                    # only for demo, cleaner printing
                    if DEMO: 
                        print(f"yolo preprocessing, person detected: {person_detected}")
                    if person_detected: 
                        if not DEMO:
                            print("yolo detected person, sending to cloud")
                        logger.info("Person detected")
                        self.yolo_person_detected += 1
                        
                        # TODO: check if this is working!
                        for i, img in enumerate(persons_images): 
                            print(f"sending person {i} to cloud")
                            cloud_start = time.time()
                            await self.send_frame_to_cloud(img, name)       # send to cloud
                            cloud_end = time.time()
                            
                            cloud_latency = (cloud_end - cloud_start) * 1000
                            if EVALUATION:
                                self.metrics.plot_cloud_latencies(cloud_latency)
                                logger.info(f"Cloud processing latency: {cloud_latency:.2f}ms")
                                
                    else:

                        logger.info("Nothing detected")
                    
                    if EVALUATION:
                        process_end = time.time()
                        edge_latency = (process_end - process_start)*1000
                        self.metrics.plot_edge_latencies(edge_latency)
                        self.metrics.plot_yolo_ratio(self.yolo_request, self.yolo_person_detected)
                        self.metrics.plot_intruder_ratio(self.total_cloud_requests, self.intruder_counter)
                        await self.sio.emit('frame_processed', {
                            'frame_name': name,
                        })
                        logger.info(f"Edge processing latency: {edge_latency:.2f}ms")
                            
                    
                    logger.info(f"Yolo detection ratio: {self.yolo_person_detected/self.yolo_request}")
                    
                except Exception as e:
                    logger.error(f"Error processing frame: {e}")
                    print(f"Error processing frame: {e}")
                finally:
                    # enqueueing task is complete, no need on lock anymore.
                    self.frame_buffer.task_done()

            await asyncio.sleep(0.01)  # problem with no rest in while loop
                
                

    # TODO use sid to keep track of clients (to notify alarm what camera caught the intruder?)
    async def _handle_frame_event(self, sid, data):
        self.frames_received += 1
        await self.frame_buffer.put(data)
        logger.info(f"frames received: {self.frames_received}")


     
def main():
    edge = EdgeServer()
    
    # wrap the server in asgi server and run it
    app = socketio.ASGIApp(
        edge.sio,
        socketio_path='socket.io',
        other_asgi_app=None,
        static_files=None
    )
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=UVICORN_PORT,
        log_level="info"
    )

    # create folder for saving the frames (TESTING)
    #os.makedirs(dir_path, exist_ok=True)
 
if __name__ == '__main__':
    main()