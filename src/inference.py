"""CPU model loading and prediction; no dependency on Streamlit or storage."""

import hashlib
import io
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from PIL import Image
from torch import nn
from torchvision import models

from src.config import DEFAULT_MODEL_PATH
from src.labels import CLASSES
from src.preprocessing import preprocess


@dataclass(frozen=True)
class LoadedModel:
    module: nn.Module
    checkpoint_sha256: str
    model_version: str


@dataclass(frozen=True)
class RankedPrediction:
    class_index: int
    label: str
    score: float


@dataclass(frozen=True)
class PredictionResult:
    class_index: int
    label: str
    confidence: float
    top3: tuple[RankedPrediction, ...]
    probabilities: tuple[float, ...]
    model_version: str
    checkpoint_sha256: str
    device: str = "cpu"

    def to_dict(self) -> dict:
        """JSON-serializable values; every score is in [0, 1], not percent."""
        return asdict(self)


def load_model(path: str | Path = DEFAULT_MODEL_PATH) -> LoadedModel:
    payload = Path(path).read_bytes()
    checksum = hashlib.sha256(payload).hexdigest()
    model = models.resnet18(weights=None)
    model.fc = nn.Linear(model.fc.in_features, len(CLASSES))
    state_dict = torch.load(io.BytesIO(payload), map_location=torch.device("cpu"), weights_only=True)
    model.load_state_dict(state_dict, strict=True)
    model.eval()
    return LoadedModel(model, checksum, f"resnet18-{checksum[:12]}")


def predict(loaded: LoadedModel, image: Image.Image) -> PredictionResult:
    with torch.no_grad():
        probabilities = torch.softmax(loaded.module(preprocess(image)), dim=1)[0]
    scores = tuple(float(value) for value in probabilities)
    # Stable ordering also preserves the original app's behavior for tied scores.
    ranking = sorted(range(len(CLASSES)), key=lambda index: scores[index], reverse=True)
    best = ranking[0]
    return PredictionResult(
        class_index=best, label=CLASSES[best], confidence=scores[best],
        top3=tuple(RankedPrediction(index, CLASSES[index], scores[index]) for index in ranking[:3]),
        probabilities=scores, model_version=loaded.model_version,
        checkpoint_sha256=loaded.checkpoint_sha256,
    )
