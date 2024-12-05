import cv2
import numpy as np
import socketio
import os
import sys
import eventlet

sio = socketio.Server()

dir_path = os.path.join('camera_set', 'video1')

def trigger_alarm():
    sio.emit('alarm_event')

@sio.event
def frame_event(sid, data):
    frame_name = data['frame_name']
    frame_data = data['data']
    print(f'recieved {frame_name}')
    sys.stdout.flush()

    # alarm test
    if (frame_name == 'frame100.jpg'):
        trigger_alarm()

    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # TESTING
    #output_path = os.path.join(dir_path, frame_name)
    #cv2.imwrite(output_path, frame)

app = socketio.WSGIApp(sio)

os.makedirs(dir_path, exist_ok=True)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)