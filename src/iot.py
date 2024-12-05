import os
import cv2
import socketio
import time

sio = socketio.Client()

def send_frames(video):
    i = 1   # frame number
    while(video.isOpened()):
        framerate = video.get(cv2.CAP_PROP_FPS)     # extract frame rate

        retval, frame = video.read()   # parse the video
        if retval == True:
            retval, jpg = cv2.imencode('.jpg', frame)
            data = jpg.tobytes()
            frame_name = f"frame{i}.jpg"
            sio.emit('frame_event', {'frame_name': frame_name, 'data': data})
            i += 1
            
            time.sleep(1/framerate)  # simulate the real frame rate

def open_video(name):
    video_path = os.path.join('camera_set', name)
    video = cv2.VideoCapture(video_path)
    if (video.isOpened() == False):
        print(f'Video file could not be opened on path {video_path}')
    
    return video

def main():
    time.sleep(10)      # wait for server
    sio.connect('http://edge:5000')

    video = open_video('video1.avi')
    send_frames(video)
  

if __name__ == '__main__':
    main()