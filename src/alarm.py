import socketio
import time

from config import * 


sio = socketio.Client()

@sio.event
def alarm_event():
    print('Intruder detected, alarm turned on... ', flush=True)

def main():
    time.sleep(INITIAL_DELAY)  # wait for the server to be set up
    sio.connect(EDGE_URL)
    print('connected to server', flush=True)

    sio.wait()  # wait for events 


if __name__ == '__main__':
    main()