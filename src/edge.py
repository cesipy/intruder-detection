import cv2
import numpy as np
import socketio
import os
import uvicorn

sio = socketio.AsyncServer(async_mode="asgi")
# dir_path = os.path.join('camera_set', 'frames') # (TESTING)

# os.makedirs("test-data", exist_ok=True)


async def trigger_alarm():
    await sio.emit('alarm_event')

# TODO send further to cloud
async def process_frame(frame_data, frame_name):

    np_arr = np.frombuffer(frame_data, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    return
    
def detect_intruder(frame_name: str, test_detection_freq: int=100): 
    frame_name = frame_name.split("_")
    frame_name = frame_name[1]
    frame_name = frame_name.replace("frame", "")
    frame_name = frame_name.replace(".jpg", "")
    frame_number = int(frame_name)
    
    if frame_number % test_detection_freq == 0:
        return True
    

# TODO use sid to keep track of clients (to notify alarm what camera caught the intruder?)
@sio.event
async def frame_event(sid, data):
    name = data['frame_name']
    frame = data['data']
    #print(f'recieved frame {name}')

    # alarm trigger (TESTING)
    if detect_intruder(name):
        print(f"Intruder detected on video frame: {name}")
        await trigger_alarm()
        
    # save frame to dir ./test-data
    # with open(f"test-data/{name}", 'wb') as f:
    #    f.write(frame)
    
    await process_frame(frame, name)

def main():
    # wrap the server in asgi server and run it
    app = socketio.ASGIApp(sio)
    uvicorn.run(app, host="0.0.0.0", port=5000)

    # create folder for saving the frames (TESTING)
    #os.makedirs(dir_path, exist_ok=True)


if __name__ == '__main__':
    main()
