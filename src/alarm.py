import socketio
import sys
import time

# wait for server to be set up
time.sleep(10)

sio = socketio.Client()
sio.connect('http://edge:5000')
print('connected to server',flush=True)

@sio.event
def alarm_event():
    print('Intruder detected, alarm turned on... ', flush=True)

sio.wait()