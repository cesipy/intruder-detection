import torch
from torch import nn


class CNN(nn.Module): 
    #def __init__(self, input_dim, hidden_dims: int, output_dim,):
    def __init__(self):
        super(CNN, self).__init__()
        
        # current input = 3,64,64
        self.conv1 = nn.Conv2d(3, 20, kernel_size=5)
        self.pool = nn.MaxPool2d(2, 2)
        self.conv2 = nn.Conv2d(20 , 8, kernel_size=5)
        
        self.relu = nn.ReLU()
        
        self.fc1 = nn.Linear(8 * 13 * 13, 120)
        self.fc2 = nn.Linear(120, 84)
        self.fc3 = nn.Linear(84, 2)
        
        self.softmax = nn.Softmax()
        
    def forward(self, x): 
        x = self.relu(self.conv1(x))
        x = self.pool(x)
        x = self.relu(self.conv2(x))
        x = self.pool(x)
        
        #flatten before passing to fc
        x = x.view(-1, 8 * 13 * 13)
        
        x = self.relu(self.fc1(x))
        x = self.relu(self.fc2(x))
        x = self.fc3(x)
        
        return x
    

        
        