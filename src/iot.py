import os
import cv2
import socketio
import time

import socketio.exceptions
from glob import glob

from config import *
from utils import Frame
from logger import Logger

logger = Logger()



class Iot:
    def __init__(self):
        self.sio = socketio.Client()
        self.camera_name = os.getenv('CAMERA')
        self.emit_retry_number = EMIT_RETRY_NUMBER
        
        # established connection to edge with exponential backoff
        self._safe_connect()
        
        
        
    def _safe_connect(self,):
        """
        established connection to sio client with exponential backoff.
        """
        init_timer = 1
        
        count = 1
        max_count = CONNECTION_RETRY
        
        while count <= max_count: 
            try: 
                self.sio.connect(EDGE_URL)
                logger.info("successfully connected to edge")
                return
            except socketio.exceptions.BadNamespaceError as e: 
                logger.error(f"Couldn't connect, namespace is bad. Error: {e}")
                print(f"Error: {e}")
                time.sleep(init_timer)
                init_timer = init_timer ** 2
                
            #TODO: maybe add other specific exceptions here, there could be other informations
            # TODO: is it only bad namesspace error??
            except Exception as e: 
                logger.error(f"Couldn't connect. Error: {e}")
                print(f"Error: {e}")
                time.sleep(init_timer)
                init_timer = init_timer
            finally:
                count+= 1
                
            
    def _send_frame(self, frame: Frame) -> bool:
        # if not self.sio.connected:      # sometimes this var is false even if the connection is established -> leads to ValueError
        #                                 # ValueError: Client is not in a disconnected state
            # print('Not connected, reconnecting...')
            # self.sio.connect('http://edge:5000')
            
        for retry in range(self.emit_retry_number):
            try:
                self.sio.emit('frame_event', {'frame_name': frame.frame_name, 'data': frame.frame_data})
                return True
            
            except socketio.exceptions.ConnectionError:
                print('Connection error, reconnecting...')
                logger.error(f"Connection error, reconnecting...")
                time.sleep(EMIT_FAILURE_DELAY)
                
                self._safe_connect()
                
            except socketio.exceptions.BadNamespaceError: 
                logger.error(f"Bad namespace error, reconnecting...")
                print('Bad namespace error, reconnecting...')
                time.sleep(EMIT_FAILURE_DELAY)
                
                self._safe_connect()
                
                
        # was not successful
        return False

    def process_frames(self, video, frame_skip=30):
        i = 1   # frame number
        while(video.isOpened()):
            framerate = video.get(cv2.CAP_PROP_FPS)     # extract frame rate

            retval, frame = video.read()   # parse the video
            
            if retval == True:
                condition: bool = i % frame_skip == 0
                if condition:
                    retval, jpg = cv2.imencode('.jpg', frame)
                    data = jpg.tobytes()
                    frame_name = f"{self.camera_name.split('.')[0]}_frame{i}.jpg"
                    
                    frame_obj = Frame(frame_name, data)
                    succ = self._send_frame(frame_obj)
                    logger.info(f"Frame {i} sent successfully: {succ}")
                i += 1
                
                time.sleep(1/framerate)  # simulate the real frame rate


    def evaluation(self, image_folder: str):
        
        image_files = sorted(glob(os.path.join(image_folder, '*.png')))
        
        if not image_files: 
            logger.error(f"No images found in folder {image_folder}")
            print(f"No images found in folder {image_folder}")
            return
        
        for image in image_files: 
            retval, jpg = cv2.imencode('.jpg', cv2.imread(image))
            data = jpg.tobytes()
            
            frame_name = os.path.basename(image)
            frame_obj = Frame(frame_name, data)
            succ = self._send_frame(frame_obj)
            logger.info(f"Frame {frame_name} sent successfully: {succ}")
        
            
        

def open_video(name):
    print(f'opening video {name}')
    logger.info(f'opening video {name}')
    video_path = os.path.join('camera_set', name)
    print(video_path)
    video = cv2.VideoCapture(video_path)
    if (video.isOpened() == False):
        logger.error(f'Video file could not be opened on path {video_path}')
        print(f'Video file could not be opened on path {video_path}')
    
    return video

def main():
    # TODO: exception handling here
    
    time.sleep(INITIAL_DELAY)      # wait for server, maybe put in init function of Iot
    iot = Iot()                     # initial connection is established here
    
    if EVALUATION: 
        iot.evaluation("evaluation_images")
        print("Evaluation finished")
        logger.info("Evaluation finished")
    
    else: 
        video = open_video(iot.camera_name)
        
        iot.process_frames(video)

if __name__ == '__main__':
    main()