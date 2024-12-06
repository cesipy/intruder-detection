import socketio
import time

sio = socketio.Client()

@sio.event
def alarm_event():
    print('Intruder detected, alarm turned on... ', flush=True)

def main():
    time.sleep(10)  # wait for the server to be set up
    sio.connect('http://edge:5000')
    print('connected to server', flush=True)

    sio.wait()  # wait for events 


if __name__ == '__main__':
    main()