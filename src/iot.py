import os
import cv2
import socketio
import time

# open the video file 
video_path = os.path.join('camera_set', 'video1.avi')
video = cv2.VideoCapture(video_path)

if (video.isOpened() == False):
    print(f'Video file could not be opened on path {video_path}')

# wait for server to be set up
time.sleep(10)

# connect to the edge server 
sio = socketio.Client()
sio.connect('http://edge:5000')
  

def send_frames():
    i = 1
    while(video.isOpened()):
        # extract frame rate from the video file
        framerate = video.get(cv2.CAP_PROP_FPS)

        # parse the video into frames and send them to the server
        retval, frame = video.read()
        if retval == True:
            retval, jpg = cv2.imencode('.jpg', frame)
            data = jpg.tobytes()
            frame_name = f"frame{i}.jpg"
            sio.emit('frame_event', {'frame_name': frame_name, 'data': data})
            i += 1
            
            # simulate the real frame rate
            time.sleep(1/framerate)

send_frames()