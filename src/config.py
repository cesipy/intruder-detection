import os

# debugging: print everything, verbose "logging"
DEBUGGING = False

EVALUATION = os.getenv("EVALUATION", False)
DEMO = os.getenv("IS_DEMO", False)

print(f"DEMO: {DEMO}")



# edge config
# --------------------------------------------------
UVICORN_PORT = 5001


# cloud config
# --------------------------------------------------
CLOUD_URL              = "http://cloud:5000"
# CLOUD_URL              = "http://18.232.173.114:5000"
CLOUD_CREDENTIALS_PATH = "res/credentials/creds.yaml"

# can be hard coded, is not expected to change in course fo this project
AWS_REGION_NAME        = "us-east-1"    

# flask stuff / webserver for rest api
FLASK_PORT = 5000           
DETECT_INTRUDER_PATH = "detect_intruder"

# what is the URL PATH on the flask rest api
KNOWN_FACES_PATH = "res/known_faces"

# Rekognition stuff
FACE_MATCH_THRESHOLD = 75   # threshold for face match in collection in percent
REKOGNITION_COLLECTION_NAME = "known_persons" # collection name


# iot config
# --------------------------------------------------
EDGE_URL = f"http://edge:{UVICORN_PORT}"
# EDGE_URL = f"http://34.204.51.85:{UVICORN_PORT}"
EMIT_FAILURE_DELAY = 1.0        # 1 sec
INITIAL_DELAY      = 20.0       # how long to wait after setup. Is due to overhead of edge provisioning.
EMIT_RETRY_NUMBER  = 3          # how often to try to reconnect when sending
CONNECTION_RETRY   = 10