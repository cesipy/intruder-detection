import cv2
import numpy as np
import socketio
import os
import sys
import eventlet
import asyncio
import uvicorn

# create folder for saving the frames (TESTING)
dir_path = os.path.join('camera_set', 'video1')
os.makedirs(dir_path, exist_ok=True)

# create server and wrap it in wsgi server
sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)

async def trigger_alarm():
    print('alarm about to be triggered', flush=True)
    await sio.emit('alarm_event')

async def process_frame(frame_data, frame_name):
    # convert back to jpg
    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # save the frames (TESTING)
    #output_path = os.path.join(dir_path, frame_name)
    #cv2.imwrite(output_path, frame)

@sio.event
async def frame_event(sid, data):
    frame_name = data['frame_name']
    frame_data = data['data']
    #print(f'recieved {frame_name}')

    # alarm test (TESTING)
    if (frame_name == 'frame100.jpg'):
        await trigger_alarm()
    
    await process_frame(frame_data, frame_name)


if __name__ == '__main__':
    # start server with its own loop to handle asynchronous connections
    uvicorn.run(app, host="0.0.0.0", port=5000)