"""Service contracts and upload errors that must survive UI changes."""

import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import torch
from src.config import DEFAULT_MODEL_PATH, PROJECT_ROOT
from src.inference import LoadedModel, load_model, predict
from src.labels import CLASSES
from src.preprocessing import preprocess
from src.storage import make_history_record
from src.validation import ImageValidationError, decode_image


def image_bytes(mode="RGB", format="PNG", size=(13, 9)):
    output = io.BytesIO()
    Image.new(mode, size).save(output, format=format)
    return output.getvalue()


class UploadTests(unittest.TestCase):
    def test_rgb_grayscale_and_alpha_become_rgb_without_size_change(self):
        for mode in ("RGB", "L", "RGBA"):
            with self.subTest(mode=mode):
                image = decode_image(image_bytes(mode))
                self.assertEqual(image.mode, "RGB")
                self.assertEqual(image.size, (13, 9))
                self.assertEqual(tuple(preprocess(image).shape), (1, 3, 224, 224))

    def test_jpeg_is_accepted(self):
        self.assertEqual(decode_image(image_bytes(format="JPEG")).mode, "RGB")

    def test_empty_corrupt_and_truncated_uploads_are_rejected(self):
        for payload in (b"", b"not an image", image_bytes()[:20]):
            with self.subTest(payload=payload[:10]):
                with self.assertRaises(ImageValidationError):
                    decode_image(payload)

    def test_unsupported_content_is_rejected(self):
        with self.assertRaisesRegex(ImageValidationError, "JPEG and PNG"):
            decode_image(image_bytes(format="GIF"))

    def test_byte_and_pixel_limits_are_enforced(self):
        with patch("src.validation.MAX_UPLOAD_BYTES", 3):
            with self.assertRaisesRegex(ImageValidationError, "20 MiB"):
                decode_image(b"1234")
        with patch("src.validation.MAX_IMAGE_PIXELS", 4):
            with self.assertRaisesRegex(ImageValidationError, "16 million"):
                decode_image(image_bytes(size=(3, 2)))


class UniformModel(torch.nn.Module):
    def forward(self, tensor):
        return torch.zeros((tensor.shape[0], 6))


class PredictionContractTests(unittest.TestCase):
    def setUp(self):
        self.loaded = LoadedModel(UniformModel().eval(), "a" * 64, "resnet18-test")

    def test_tied_scores_keep_original_class_order_and_fractional_scores(self):
        result = predict(self.loaded, Image.new("RGB", (10, 10)))
        self.assertEqual(result.class_index, 0)
        self.assertEqual(result.label, CLASSES[0])
        self.assertEqual([p.class_index for p in result.top3], [0, 1, 2])
        self.assertAlmostEqual(result.confidence, 1 / 6)
        self.assertAlmostEqual(sum(result.probabilities), 1)
        serialized = json.loads(json.dumps(result.to_dict()))
        self.assertEqual(serialized["model_version"], "resnet18-test")
        self.assertEqual(serialized["checkpoint_sha256"], "a" * 64)

    def test_missing_checkpoint_fails_with_file_error(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):
                load_model(Path(folder) / "missing.pth")

    def test_default_path_is_relative_to_project_not_working_directory(self):
        self.assertTrue(DEFAULT_MODEL_PATH.is_absolute())
        self.assertEqual(DEFAULT_MODEL_PATH, PROJECT_ROOT / "models" / "leaf_model_final.pth")

    def test_history_contract_is_serializable_and_does_not_store_image_bytes(self):
        result = predict(self.loaded, Image.new("RGB", (10, 10)))
        record = make_history_record(result, "C:\\uploads\\leaf.png", b"image-payload")
        self.assertEqual(record["image_name"], "leaf.png")
        self.assertEqual(record["schema_version"], 1)
        self.assertTrue(record["created_at"].endswith("+07:00"))
        self.assertNotIn("image_bytes", record)
        self.assertEqual(json.loads(json.dumps(record))["prediction"]["label"], CLASSES[0])


if __name__ == "__main__":
    unittest.main()
