import os
import cv2
import socketio
import time

import socketio.exceptions

from utils import Frame

# TODO: place in config
EMIT_FAILURE_DELAY = 1.0        # 1 sec
INITIAL_DELAY      = 30.0

class Iot:
    def __init__(self):
        self.sio = socketio.Client()
        self.camera_name = os.getenv('CAMERA')
        self.emit_retry_number = 3      # TODO: put this in configuration
        
            
    def _send_frame(self, frame: Frame) -> bool:
        # if not self.sio.connected:      # sometimes this var is false even if the connection is established -> leads to ValueError
        #                                 # ValueError: Client is not in a disconnected state
        #     print('Not connected, reconnecting...')
        #     self.sio.connect('http://edge:5000')
            
        for retry in range(self.emit_retry_number):
            try:
                self.sio.emit('frame_event', {'frame_name': frame.frame_name, 'data': frame.frame_data})
                return True
            
            # TODO: maybe implement exponetial backoff
            except socketio.exceptions.ConnectionError:
                print('Connection error, reconnecting...')
                time.sleep(EMIT_FAILURE_DELAY)
                
                try: 
                    self.sio.connect('http://edge:5000')
                except Exception as e:
                    print(f'Error: {e}')
                
            except socketio.exceptions.BadNamespaceError: 
                print('Bad namespace error, reconnecting...')
                time.sleep(EMIT_FAILURE_DELAY)
                
                try: 
                    self.sio.connect('http://edge:5000')
                except Exception as e:
                    print(f'Error: {e}')
        # was not successful
        return False

    def process_frames(self, video):
        i = 1   # frame number
        while(video.isOpened()):
            framerate = video.get(cv2.CAP_PROP_FPS)     # extract frame rate

            retval, frame = video.read()   # parse the video
            if retval == True:
                retval, jpg = cv2.imencode('.jpg', frame)
                data = jpg.tobytes()
                frame_name = f"{self.camera_name.split('.')[0]}_frame{i}.jpg"
                
                frame_obj = Frame(frame_name, data)
                self._send_frame(frame_obj)
                i += 1
                
                time.sleep(1/framerate)  # simulate the real frame rate


def open_video(name):
    print(f'opening video {name}')
    video_path = os.path.join('camera_set', name)
    video = cv2.VideoCapture(video_path)
    if (video.isOpened() == False):
        print(f'Video file could not be opened on path {video_path}')
    
    return video

def main():
    # TODO: exception handling here
    
    time.sleep(INITIAL_DELAY)      # wait for server, maybe put in init function of Iot
    iot = Iot()
    video = open_video(iot.camera_name)
    iot.sio.connect('http://edge:5000')

    iot.process_frames(video)

if __name__ == '__main__':
    main()