import os
import cv2

video_path = 'camera_set\\video1.avi'
video = cv2.VideoCapture(video_path)


if (video.isOpened() == False):
    print('Video file could not be opened')

os.makedirs('camera_set\\video1', exist_ok=True)
    
i = 0
while(video.isOpened()):
    retval, frame = video.read()
    if retval == True:
        output_path = 'camera_set\\video1\\'+ f'frame{i}.jpg'
        cv2.imwrite(output_path, frame)
        i += 1