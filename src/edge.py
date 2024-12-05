import cv2
import numpy as np
import socketio
import os
import uvicorn

sio = socketio.AsyncServer(async_mode="asgi")
# dir_path = os.path.join('camera_set', 'frames') # (TESTING)

async def trigger_alarm():
    await sio.emit('alarm_event')

# TODO send further to cloud
async def process_frame(frame_data, frame_name):

    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # save the frames (TESTING)
    #output_path = os.path.join(dir_path, frame_name)
    #cv2.imwrite(output_path, frame)

# TODO use sid to keep track of clients (to notify alarm what camera caught the intruder?)
@sio.event
async def frame_event(sid, data):
    name = data['frame_name']
    frame = data['data']
    #print(f'recieved frame {name}')

    # alarm trigger (TESTING)
    if (name == 'video3_frame100.jpg'):
        await trigger_alarm()
    
    await process_frame(frame, name)

def main():
    # wrap the server in asgi server and run it
    app = socketio.ASGIApp(sio)
    uvicorn.run(app, host="0.0.0.0", port=5000)

    # create folder for saving the frames (TESTING)
    #os.makedirs(dir_path, exist_ok=True)


if __name__ == '__main__':
    main()
