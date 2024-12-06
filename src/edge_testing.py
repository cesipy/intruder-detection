import os
import torch 
import pandas as pd

#different model types with suffix: 
# n - nano
# s - small
# m - medium
# l - large
# x - xlarge
model = torch.hub.load("ultralytics/yolov5", "yolov5x", pretrained=True)

def get_imgs(dir_name: str): 
    imgs = []
    for img in os.listdir(dir_name): 
        img_path = os.path.join(dir_name, img)
        if img.endswith(".jpg"):
            imgs.append(img_path)
    return imgs

def analyze_data(detections): 
    imgs_with_persons = []
    # results.pandas().xyxy[i] gives DataFrame for i-th image
    for i in range(len(detections.pred)):
        df = detections.pandas().xyxy[i]  # Get DataFrame for image i
        
        person_detected = is_person_detected(df)
        print(f"\nDetections in image {i}:")
        for _, row in df.iterrows():
            print(f"- {row['name']} (confidence: {row['confidence']:.2f})")
        print(f"- person detected: {person_detected}")
        
        if person_detected: 
            imgs_with_persons.append(i)
    
    return imgs_with_persons
            
def is_person_detected(img, confidence=0.85):
    # TODO include confidence checking, can be defined in config file 
    return "person" in img["name"].values
    

def main(): 
    imgs = get_imgs("local-test-data")
    results = model(imgs)
    imgs_w_person = analyze_data(results)
    
    print(f"\nImages with persons detected: {imgs_w_person}")

    
    
main()