import socketio
import sys


sio = socketio.Client()
sio.connect('http://localhost:5000')

@sio.event
def alarm_event():
    print('Intruder detected, alarm turned on... ')
    sys.stdout.flush()


sio.wait()