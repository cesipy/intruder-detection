import os
import pandas as pd

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
        
        yolo_name = f"yolo5v{model_type}"
        self.model = YOLO("yolov8m.pt", verbose=False)
        self.model.cpu()

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
            results = self.model(image, verbose=False)

            # should be only one result, but is wrapped in list
            for result in results: 

                predicted_persons = result.boxes.data[              # stores all persons
                    (result.boxes.cls == 0)  &                      #cls == 0 => person has index 0 in cls
                    (result.boxes.conf >= confidence_threshold)
                                                    ]
                if len(predicted_persons) >= 1:
                    return True
            
            return False
        except Exception as e:
            print(f"Error in analyze_image: {e}")
            return False

def get_imgs(dir_name: str): 
    imgs = []
    for img in os.listdir(dir_name): 
        img_path = os.path.join(dir_name, img)
        if img.endswith(".jpg"):
            imgs.append(img_path)
    return imgs


        
def main(): 
    imgs = get_imgs("local-test-data")
    yolo = YoloDetection()
    
    preds = []
    
    for img in imgs:
        pred = yolo.analyze_image(img)
        print(f"Image: {img} - Prediction: {pred}")
        preds.append(pred)
        
    print(f"Predictions: {preds}")
    
    # print(results)
    # counter = 0
    # for result in results: 
    #     print(f"-----------------------result-{counter}----------------------")
    #     prediction =result.boxes.data[(result.boxes.cls == 0)]
    #     if len(prediction) >= 1: 
    #         print("true")
    #     print(result.boxes.data[(result.boxes.cls == 0)])
    #     counter+=1

    #     result.show()

    
    
if __name__ =='__main__':
    main()