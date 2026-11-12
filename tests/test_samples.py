import hashlib
import io
import unittest
from unittest.mock import patch

from src.labels import CLASSES
from src.samples import REVISION, sample_bytes, sample_manifest


class SampleTests(unittest.TestCase):
    def test_manifest_contains_one_training_example_per_class(self):
        samples = sample_manifest()
        self.assertEqual([s["label"] for s in samples], list(CLASSES))
        self.assertTrue(all(s["split"] == "train" for s in samples))

    def test_network_fallback_fetches_only_selected_pinned_image(self):
        payload = b"fixture content"
        sample = {"local_path": "data/missing.jpg", "source_path": "raw/color/Leaf 1.JPG",
                  "sha256": hashlib.sha256(payload).hexdigest()}
        with patch("src.samples.sample_manifest", return_value=[sample]), \
             patch("pathlib.Path.is_file", return_value=False), \
             patch("src.samples.urllib.request.urlopen", return_value=io.BytesIO(payload)) as fetch:
            self.assertEqual(sample_bytes(0), payload)
            self.assertIn(REVISION, fetch.call_args.args[0].full_url)
            self.assertIn("Leaf%201.JPG", fetch.call_args.args[0].full_url)
            self.assertEqual(fetch.call_count, 1)

    def test_incorrect_download_hash_is_rejected(self):
        sample = {"local_path": "data/missing.jpg", "source_path": "raw/color/Leaf.JPG", "sha256": "0" * 64}
        with patch("src.samples.sample_manifest", return_value=[sample]), \
             patch("pathlib.Path.is_file", return_value=False), \
             patch("src.samples.urllib.request.urlopen", return_value=io.BytesIO(b"wrong")):
            with self.assertRaises(ValueError):
                sample_bytes(0)
