import yaml
import boto3
import os
import random

import flask
from typing import List

from config import *


# global vars feel very bad here, but didnt manage to get other non-global-var solutions running
app = flask.Flask(__name__)
cloud = None



class Cloud:
    
    def __init__(self,) -> None: 
        self.credentials_config = self._load_credentials_configuration()
        self.rekognition_client = self._init_rekognition_client()

        #upload faces to known faces on rekognition
        self.create_collection()
        self.add_known_faces(KNOWN_FACES_PATH)
        print("successfully initialized cloud")
        
    
    def _load_credentials_configuration(self) -> dict:
        if not  os.path.exists(CLOUD_CREDENTIALS_PATH):
            raise FileNotFoundError(f"File {CLOUD_CREDENTIALS_PATH} not found, please copy 'res/credentials/creds.yaml.sample' to 'res/credentials/creds.yaml' and fill in the credentials, refer to readme!")
        with open(CLOUD_CREDENTIALS_PATH) as file:
            return yaml.safe_load(file)
        
    def _init_rekognition_client(self):
        aws_access_key_id     = self.credentials_config['aws_access_key_id']
        aws_secret_access_key = self.credentials_config['aws_secret_access_key']
        aws_session_token     = self.credentials_config['aws_session_token']
        region_name = AWS_REGION_NAME
        
        return boto3.client(
            'rekognition', 
            region_name=region_name, 
            aws_access_key_id=aws_access_key_id, 
            aws_secret_access_key=aws_secret_access_key, 
            aws_session_token=aws_session_token,
        )
        
    def process_image(self, img: bytes) -> bool:
        try:
            if DEBUGGING:
                return random.random() <= 0.5

            response = self.rekognition_client.detect_labels(
                Image={'Bytes': img},
                MinConfidence=90
            )
            
            for label in response['Labels']:
                if label['Name'] in ['Person', 'Human'] and label['Confidence'] > 90:
                    print(f"Person detected with confidence: {label['Confidence']}%")
                    return True
            return False
            
        except Exception as e:
            print(f"Processing error: {e}")
            return False
        
    def is_face_in_collection(self, image: bytes) -> bool:
        # simulate face detection to avoid aws connection for testing
        if DEBUGGING: 
            return random.random() <= 0.5
        
        try:
            faces = self.rekognition_client.search_faces_by_image(
                CollectionId=REKOGNITION_COLLECTION_NAME,
                Image={'Bytes': image},
                MaxFaces=1,
                FaceMatchThreshold=FACE_MATCH_THRESHOLD,
            )
            print(f"faces: {faces}")
            
            return len(faces["FaceMatches"]) == 0
        
        except Exception as e:
            print(f"Error checking face in collection: {e}")
            return False
        
        
    def create_collection(self) -> bool:
        try:
            self.rekognition_client.create_collection(CollectionId=REKOGNITION_COLLECTION_NAME)
            print("successfully created collection 'REKOGNITION_COLLECTION_NAME'")
            return True

        except self.rekognition_client.exceptions.ResourceAlreadyExistsException:
            print("Collection 'REKOGNITION_COLLECTION_NAME' already exists")
            return False
        except Exception as e:
            print(f"Error creating collection: {e}")
            return False
        
    def add_known_face(self, image:bytes):
        try:
            response = self.rekognition_client.index_faces(
                CollectionId=REKOGNITION_COLLECTION_NAME,
                Image={'Bytes': image},
            )
            return response
        except Exception as e:
            print(f"Error adding face to known faces: {e}")
            return False
        
    def add_known_faces(self, path: str): 
        all_files = os.listdir(path)
        print(f"all files: {all_files}")
        all_imgs_paths: List[str] = []
        for img in all_files:
            if img.endswith(".png"): 
                all_imgs_paths.append(os.path.join(path, img))
                
        print(f"all imgs paths: {all_imgs_paths}")
        # convert all paths to bytes list
        all_imgs  = [self.read_image(img_path) for img_path in all_imgs_paths]
            
        for img in all_imgs: 
            self.add_known_face(img)
            
            
        
    def read_image(self, path: str) -> bytes: 
        with open(path, "rb") as file:
            return file.read()

@app.route(f"/{DETECT_INTRUDER_PATH}", methods=["POST"])
def detect_intruder():
    
    img = flask.request.files['img']        # this is in base65 (??)
    if not img: 
        return flask.jsonify({"error": "no image provided"}), 400
    
    img_bytes = img.read()      # convert to bytes, so we can send it to rekognition
    
    #result = cloud.process_image(img_bytes)
    result = cloud.is_face_in_collection(img_bytes)
    
    response = {"result": result}
    return flask.jsonify(response)
    
@app.route("/health", methods=["GET"])
def health_check():
    return flask.jsonify({"status": "healthy"})



def main():
    global cloud        # as the global var is not initialized, here we have to explicitly call the global var
    cloud = Cloud()

    app.run(host="0.0.0.0", port=FLASK_PORT)     
        
        
if __name__ == '__main__': 
    main()