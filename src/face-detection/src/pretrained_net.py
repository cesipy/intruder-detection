from torchvision import transforms
from torchvision.models import resnet18, ResNet18_Weights

from torch import nn

class ResNetWrapper(nn.Module):
    def __init__(self, dropout_prob, hidden_dim): 
        super().__init__()
        self.model = resnet18(weights=ResNet18_Weights.DEFAULT)
        
        # freeze layers that they are not finetuned: 
        for name, param in self.model.named_parameters():
            if "fc" not in name:  # fc is the final classifier layer
                param.requires_grad = False
        
            
        #if layer4 should be finetuned: 
        # for param in self.model.layer4.parameters():
        #     param.requires_grad = False
        
        # get dimension of input for previous classifier
        self.in_features = self.model.fc.in_features
        
        classifier = [
            nn.Linear(in_features=self.in_features, out_features=hidden_dim),
            nn.ReLU(inplace=False),
            nn.Dropout(dropout_prob, inplace=False),
            
            nn.Linear(in_features=hidden_dim, out_features=hidden_dim//2),
            nn.ReLU(inplace=False),
            nn.Dropout(dropout_prob, inplace=False),
            
            # final layer 
            nn.Linear(in_features=hidden_dim//2, out_features=2),
        ]
        
        # replace old classifier with new one
        self.model.fc = nn.Sequential(*classifier)
        
        
    def forward(self, x): 
        return self.model(x)