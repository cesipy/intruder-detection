import os
import pandas as pd
import cv2
from config import *

from ultralytics import YOLO

# model = torch.hub.load("ultralytics/yolov5", "yolov5s", pretrained=True)
# model = YOLO("res/weights/yolov5su.pt")
class YoloDetection:
    def __init__(self, model_type="s"):
    
    #different model types with suffix: 
    # n - nano
    # s - small
    # m - medium
    # l - large
    # x - xlarge
    
        if model_type not in ["n", "s", "m", "l", "x"]:
            raise ValueError("Invalid model type")

        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["MKL_NUM_THREADS"] = "1"
        
        yolo_name = f"yolov8{model_type}"
        self.model = YOLO(yolo_name, verbose=False)
        self.model.cpu()
        
    def _detect_persons(self, image, confidence_threshold=0.5): 

        results = self.model(image, verbose=False)
        #img = cv2.imread(image,)
        
        #can have string or real numpy arr
        if isinstance(image, str):
            img = cv2.imread(image)
            if img is None:
                print(f"Error: Could not load image from path")
                return False, []
        else:
            img = image
    
        persons = []
        # should be only one result, but is wrapped in list
        for result in results: 

            predicted_persons = result.boxes.data[              # stores all persons
                (result.boxes.cls == 0)  &                      #cls == 0 => person has index 0 in cls
                (result.boxes.conf >= confidence_threshold)
                                                ]
            return_val: bool = False
            for i, box in enumerate(predicted_persons): 
                box = box[:4]
                box = [int(elem) for elem in box]
                x,y,w,h = box       # extract positions
                
                # extract the person in the image
                person = img[y:h, x:w]
                hash_str = f"{x}{y}{w}{h}"

                filename = f"{hash_str}-person{i}.jpg"
                
                # save the person, for debug
                cv2.imwrite(filename, person)
                
                person_bytes =  person.tobytes()
                persons.append(person_bytes)

            if len(predicted_persons) > 1: 
                return_val = True
            
            return return_val, persons
                
    #TODO: make confidence_threshold customizable in config
    def analyze_image(self, image, confidence_threshold=0.5) -> bool:
        """
        analyzes an image and returns a boolen value indicating whether a person is detected.
        
        Args:
            image: image to analyze
            
        Returns:
            bool: True if person is detected, False otherwise
        """
        try:
                
            person_detected, persons = self._detect_persons(image, confidence_threshold=confidence_threshold)
            #print(f"person_detected in analyze_image: {person_detected}")
            return person_detected, persons
        except Exception as e:
            print(f"Error in analyze_image: {e}")
            return False, []
       

def get_imgs(dir_name: str): 
    imgs = []
    for img in os.listdir(dir_name): 
        img_path = os.path.join(dir_name, img)
        if img.endswith(".jpg") or img.endswith(".png"):
            imgs.append(img_path)
    return imgs


        
def main(): 
    #imgs = get_imgs("local-test-data")
    imgs = get_imgs("res/iot_resources/evaluation_images")
    yolo = YoloDetection()
    
    preds = []
    
    for img in imgs:
        pred = yolo.analyze_image(img)
        print(f"Image: {img} - Prediction: {pred}")
        preds.append(pred)
        
    print(f"Predictions: {preds}")
    


    
    
if __name__ =='__main__':
    main()
    