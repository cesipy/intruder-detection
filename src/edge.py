import cv2
import numpy as np
import socketio
import os
import sys
import eventlet

# create folder for saving the frames (TESTING)
dir_path = os.path.join('camera_set', 'video1')
os.makedirs(dir_path, exist_ok=True)

# create server and wrap it in wsgi server
sio = socketio.Server()
app = socketio.WSGIApp(sio)

def trigger_alarm():
    sio.emit('alarm_event')

@sio.event
def frame_event(sid, data):
    frame_name = data['frame_name']
    frame_data = data['data']
    print(f'recieved {frame_name}')
    sys.stdout.flush()

    # alarm test (TESTING: TODO fix this)
    if detect_intruder(frame_name=frame_name):
        trigger_alarm()

    # convert back to jpg
    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # save the frames (TESTING)
    #output_path = os.path.join(dir_path, frame_name)
    #cv2.imwrite(output_path, frame)
    
    
def detect_intruder(frame_name: str, test_detection_freq=100): 
    frame_name = frame_name.replace("frame", "")
    frame_name = frame_name.replace(".jpg", "")
    frame_number = int(frame_name)
    
    if frame_number % test_detection_freq == 0:
        return True
    


if __name__ == '__main__':
    # start server with its own loop to handle asynchronous connections
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)