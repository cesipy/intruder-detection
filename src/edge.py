import cv2
import numpy as np
import socketio
import eventlet

sio = socketio.Server()

@sio.event
def frame_event(sid, data):
    frame_name = data['frame_name']
    frame_data = data['data']
    print(f'recieved {frame_name}')

    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    output_path = f'camera_set\\video1\\{frame_name}'
    cv2.imwrite(output_path, frame)

app = socketio.WSGIApp(sio)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)