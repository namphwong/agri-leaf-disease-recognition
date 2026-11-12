"""Match the inherited notebook's evaluation preprocessing exactly."""

from PIL import Image
from torchvision import transforms
import torch


def build_transform() -> transforms.Compose:
    return transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])


def preprocess(image: Image.Image) -> torch.Tensor:
    """RGB float tensor [1, 3, 224, 224]; no normalization or EXIF rotation."""
    return build_transform()(image.convert("RGB")).unsqueeze(0)
