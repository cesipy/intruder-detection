import yaml
import boto3
import os
import random

import flask

from config import *


# global vars feel very bad here, but didnt manage to get other non-global-var solutions running
app = flask.Flask(__name__)
cloud = None

class Cloud:
    
    def __init__(self,) -> None: 
        self.credentials_config = self._load_credentials_configuration()
        self.rekognition_client = self._init_rekognition_client()
        print("successfully initialized cloud")
        
    
    def _load_credentials_configuration(self) -> dict:
        if not  os.path.exists(CLOUD_CREDENTIALS_PATH):
            raise FileNotFoundError(f"File {CLOUD_CREDENTIALS_PATH} not found, please copy 'res/credentials/creds.yaml.sample' to 'res/credentials/creds.yaml' and fill in the credentials, refer to readme!")
        with open(CLOUD_CREDENTIALS_PATH) as file:
            return yaml.safe_load(file)
        
    def _init_rekognition_client(self):
        aws_access_key_id = self.credentials_config['aws_access_key_id']
        aws_secret_access_key = self.credentials_config['aws_secret_access_key']
        region_name = AWS_REGION_NAME
        
        return boto3.client(
            'rekognition', 
            region_name=region_name, 
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key
        )
        
    def process_image(self, img: bytearray) -> bool:
        try:
            if DEBUGGING:
                if random.random()<= 0.5:
                    print("simulation of rekognition returned intruder!")
                    return True
            else: 
                return False
            
            response = self.rekognition_client.detect_labels(
                Image={
                    'Bytes': img
                }
            )
            
            return True         # only temporary
        except Exception as e:
            print(f"processing image with rekognition did not work, probably credentials for aws are incorrect!")
            print(e)
            
        return False



@app.route(f"/{DETECT_INTRUDER_PATH}", methods=["POST"])
def detect_intruder():
    
    img = flask.request.files['img']        # this is in base65 (??)
    if not img: 
        return flask.jsonify({"error": "no image provided"}), 400
    
    img_bytes = img.read()
    
    result = cloud.process_image(img_bytes)
    
    response = {"result": result}
    return flask.jsonify(response)
    
    
    


@app.route("/health", methods=["GET"])
def health_check():
    return flask.jsonify({"status": "healthy"})

def main():
    global cloud        # as the global var is not initialized, here we have to explicitly call the global var
    cloud = Cloud()

    app.run(host="0.0.0.0", port=5000)
        
        
if __name__ == '__main__': 
    main()