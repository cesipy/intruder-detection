import socketio
import time
from logger import Logger

from config import * 

logger = Logger()



class Alarm:
    def __init__(self, ):
        self.sio = socketio.Client()
        self._setup_events()
        self._safe_connect()
        
        
    def _setup_events(self,):
        @self.sio.event
        def alarm_event():
            print('Intruder detected, alarm turned on... ', flush=True)
            
        

    def _safe_connect(self,):
            """
            established connection to sio client with exponential backoff.
            """
            # dont need to connct if already connected!
            if self.sio.connected: 
                logger.info("already connected!")
                return
            init_timer = 1
            
            count = 1
            max_count = CONNECTION_RETRY
            
            while count <= max_count: 
                try: 
                    self.sio.connect(EDGE_URL)
                    logger.info("successfully connected to edge")
                    return
                except socketio.exceptions.BadNamespaceError as e: 
                    logger.error(f"Couldn't connect, namespace is bad. Error: {e}")
                    print(f"Error: {e}")
                    time.sleep(init_timer)
                    init_timer = init_timer ** 2
                    
                #TODO: maybe add other specific exceptions here, there could be other informations
                # TODO: is it only bad namesspace error??
                except Exception as e: 
                    logger.error(f"Couldn't connect. Error: {e}")
                    print(f"Error: {e}")
                    time.sleep(init_timer)
                    init_timer = init_timer
                finally:
                    count+= 1

def main():
    time.sleep(INITIAL_DELAY)  # wait for the server to be set up
    alarm = Alarm()
    print('connected to server', flush=True)

    alarm.sio.wait()  # wait for events 


if __name__ == '__main__':
    main()