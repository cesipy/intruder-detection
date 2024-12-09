import os
from PIL import Image
import torch
from torchvision import transforms
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, random_split

from sklearn.metrics import precision_score, accuracy_score, classification_report


import matplotlib.pyplot as plt
import numpy as np

from cnn import CNN


BATCH_SIZE = 10
LEARNING_RATE = 0.001
EPOCHS = 10

class FaceDataset(Dataset):
    def __init__(self, face_tensors, non_face_tensors):
        # Combine face and non-face tensors
        self.images = torch.cat([face_tensors, non_face_tensors], dim=0)
        
        # Create labels (1 for faces, 0 for non-faces)
        self.labels = torch.cat([
            torch.ones(face_tensors.shape[0]),
            torch.zeros(non_face_tensors.shape[0])
        ])
    
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, idx):
        return self.images[idx], self.labels[idx]


def load_all_face_images():
    dirname = "src/face-detection/res/faces_dataset"
    
    # Define the transform
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    face_images = []
    
    for img in os.listdir(dirname):
        if img.endswith(".jpg"):
            img_path = os.path.join(dirname, img)
            image = Image.open(img_path).convert('RGB')
            tensor_image = transform(image)
            face_images.append(tensor_image)
            
    face_tensors = torch.stack(face_images)
    return face_tensors

def load_all_non_face_images():
    dirname = "src/face-detection/res/no_face_dataset"
    
    # Define the transform
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    non_face_images = []
    
    for img in os.listdir(dirname):
        if img.endswith(".jpg"):
            img_path = os.path.join(dirname, img)
            image = Image.open(img_path).convert('RGB')
            tensor_image = transform(image)
            non_face_images.append(tensor_image)
            
    non_face_tensors = torch.stack(non_face_images)
    return non_face_tensors


# helper functions from chatgpt to inspect if everything is working as expected
def denormalize_image(tensor):
    """Denormalize image from ImageNet stats back to [0,1] range"""
    mean = torch.tensor([0.485, 0.456, 0.406]).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225]).view(3, 1, 1)
    return tensor * std + mean

def inspect_dataset(dataset, num_images=16):
    """Display a grid of images from the dataset with their labels"""
    # Create a figure
    plt.figure(figsize=(15, 15))
    
    # Get random indices
    indices = np.random.choice(len(dataset), num_images, replace=False)
    
    # Create a grid of images
    for idx, i in enumerate(indices):
        img, label = dataset[i]
        
        # Denormalize the image
        img = denormalize_image(img)
        
        # Convert to numpy and transpose for plotting
        img = img.numpy().transpose(1, 2, 0)
        
        # Clip values to [0, 1] range
        img = np.clip(img, 0, 1)
        
        # Add subplot
        plt.subplot(4, 4, idx + 1)
        plt.imshow(img)
        plt.title(f'Label: {"Face" if label == 1 else "Non-face"}')
        plt.axis('off')
    
    plt.tight_layout()
    plt.show()

def dataset_statistics(dataset):
    """Print statistics about the dataset"""
    face_count = sum(1 for _, label in dataset if label == 1)
    non_face_count = sum(1 for _, label in dataset if label == 0)
    
    print("\nDataset Statistics:")
    print(f"Total images: {len(dataset)}")
    print(f"Face images: {face_count}")
    print(f"Non-face images: {non_face_count}")
    print(f"Face/Non-face ratio: {face_count/non_face_count:.2f}")
    
    # Check some random samples
    sample_indices = np.random.choice(len(dataset), 5)
    print("\nRandom sample shapes:")
    for idx in sample_indices:
        img, label = dataset[idx]
        print(f"Image {idx}: Shape {img.shape}, Label {label}, Value range: [{img.min():.2f}, {img.max():.2f}]")


def train_one_epoch(model, train_loader, test_loader, criterion, optimizer):
    model.train()
    train_loss = 0.0
    correct = 0
    total = 0
    
    for i, batch in enumerate(train_loader):
       
        inputs, labels = batch
        labels = labels.long()
        optimizer.zero_grad()
        
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
        
        _, predicted = outputs.max(1)
        total += labels.size(0)
        correct += predicted.eq(labels).sum().item()
        
        
    train_loss /= len(train_loader)
    train_accuracy = 100. * correct / total
    
    return train_loss, train_accuracy

def train_model(model, train_loader, val_loader, criterion, optimizer, num_epochs=10):
    for epoch in range(num_epochs):
        train_loss, train_accuracy = train_one_epoch(model, train_loader, val_loader, criterion, optimizer)
        
        val_accuracy, val_precision = validate_model(model, val_loader,)
        
        print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {train_loss:.4f}, Train acc: {train_accuracy:.2f}%, val acc {val_accuracy:.2f}% val prec {val_precision:.2f}%")
        
    print("Finished Training")
    
    return model

def validate_model(model, val_loader, report=False):
    model.eval()
    all_predictions = []
    all_labels = []
    
    with torch.no_grad():
        for batch in val_loader:
            inputs, labels = batch
            labels = labels.long()
            
            outputs = model(inputs)
            _, predicted = outputs.max(1)
            
            # Convert tensors to numpy for sklearn metrics
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics using sklearn
        accuracy = accuracy_score(all_labels, all_predictions) * 100
        precision = precision_score(all_labels, all_predictions) * 100
        
        if report: 
            # Print detailed classification report
            print("\nValidation Metrics:")
            print(classification_report(all_labels, all_predictions, 
                                    target_names=['Non-Face', 'Face']))
        
        return accuracy, precision

def test_single_image(model, image_path):
    transform = transforms.Compose([
        transforms.Resize((64, 64)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    image = Image.open(image_path).convert('RGB')
    tensor_image = transform(image)
    tensor_image = tensor_image.unsqueeze(0)
    
    model.eval()
    with torch.no_grad():
        output = model(tensor_image)
        probabilities = torch.softmax(output, dim=1)
        prediction = output.max(1)[1].item()
        confidence = probabilities[0][prediction].item()
        
    return prediction, confidence



def main():
    # load imgs
    face_imgs = load_all_face_images()
    print(f"Face images shape: {face_imgs.shape}")
    non_face_imgs = load_all_non_face_images()
    print(f"Non-face images shape: {non_face_imgs.shape}")
    
    dataset = FaceDataset(face_imgs, non_face_imgs)
    print(f"Dataset size: {len(dataset)}")
    
    # Inspect
    # inspect_dataset(dataset)
    # dataset_statistics(dataset)
    
    # on the dataset do train-test-split 
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(dataset, [train_size, val_size])
    
    print(f"Train size: {len(train_dataset)}")
    print(f"Validation size: {len(val_dataset)}")
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)
    
    model = CNN()
    criterion = nn.CrossEntropyLoss()
    optim = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    
    
    model = train_model(model, train_loader, val_loader, criterion, optim, num_epochs=EPOCHS)
    validate_model(model, val_loader, report=True)
    
    new_img_no_face1_path = "src/face-detection/res/own-test-images/no_face1.jpg"
    new_img_face1_path    = "src/face-detection/res/own-test-images/face1.jpg"
    new_img_no_face2_path = "src/face-detection/res/own-test-images/no_face2.jpg"
    new_img_face2_path    = "src/face-detection/res/own-test-images/face2.jpg"
    test_list = [new_img_no_face1_path, new_img_face1_path, new_img_no_face2_path, new_img_face2_path]

    for img_path in test_list:
        prediction, confidence = test_single_image(model, img_path)
        result = "Face" if prediction == 1 else "Non-face"
        print(f"\nImage: {img_path}")
        print(f"Prediction: {result}")
        print(f"Confidence: {confidence:.2%}")
    
main()