import torch
from torch import nn
from torchvision.models import vgg19


class EntireModel(nn.Module):
    def __init__(self):
        super().__init__()
        vgg = vgg19()
        n_feature = 512
        class_num = 2
        self.backbone = vgg.features
        self.pooling_layer = nn.AdaptiveAvgPool2d(output_size=(1, 1))
        self.classifier = nn.Sequential(nn.Linear(n_feature, class_num), nn.Softmax())

    def forward(self, x):
        feature = self.backbone(x)
        feature = self.pooling_layer(feature).view(feature.shape[0:2])
        output = self.classifier(feature)
        return output


model_path = r"D:\NutSync\核心数据\Models\Classification\pancreat_tumor_classification_2.0_v4_512.pth"
model = EntireModel()
# model.load_state_dict(torch.load(model_path))  # if use GPU
model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))  # if use CPU

