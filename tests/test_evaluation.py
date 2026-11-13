import json
import shutil
import tempfile
import unittest
from pathlib import Path

from src.evaluation import EVALUATION_PATH, load_evaluation
from src.metrics import classification_metrics


class MetricsTests(unittest.TestCase):
    def test_known_binary_confusion_matrix(self):
        result = classification_metrics([[8, 2], [1, 9]], ["a", "b"])
        self.assertEqual(result["accuracy"], 17 / 20)
        self.assertAlmostEqual(result["per_class"][0]["precision"], 8 / 9)
        self.assertAlmostEqual(result["per_class"][1]["recall"], .9)
        self.assertAlmostEqual(result["macro_f1"], (16 / 19 + 18 / 21) / 2)

    def test_zero_support_classes_stay_in_macro_average(self):
        result = classification_metrics([[1, 0], [0, 0]], ["a", "b"])
        self.assertEqual(result["macro_f1"], .5)
        self.assertEqual(result["per_class"][1]["f1"], 0)

    def test_invalid_matrices_and_empty_evaluation_are_rejected(self):
        for matrix in ([], [[-1]], [[1.2]], [[True]], [[0]], [[1, 0]]):
            with self.subTest(matrix=matrix), self.assertRaises(ValueError):
                classification_metrics(matrix, ["a"])


class ArtifactTests(unittest.TestCase):
    def test_published_metrics_match_all_prediction_rows(self):
        report = load_evaluation()
        self.assertEqual(report["metrics"]["sample_count"], 776)
        self.assertFalse(report["independent_test"])

    def changed_report(self, mutate):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        destination = Path(temp.name)
        shutil.copytree(EVALUATION_PATH, destination, dirs_exist_ok=True)
        path = destination / "latest.json"
        report = json.loads(path.read_text(encoding="utf-8"))
        mutate(report)
        path.write_text(json.dumps(report), encoding="utf-8")
        return destination

    def test_fabricated_accuracy_is_rejected(self):
        folder = self.changed_report(lambda r: r["metrics"].update(accuracy=1.0))
        with self.assertRaisesRegex(ValueError, "metric mismatch"):
            load_evaluation(folder)

    def test_independent_claim_is_rejected_for_inherited_report(self):
        folder = self.changed_report(lambda r: r.update(independent_test=True))
        with self.assertRaisesRegex(ValueError, "scope"):
            load_evaluation(folder)

    def test_modified_predictions_are_rejected(self):
        folder = self.changed_report(lambda r: None)
        with (folder / "predictions.csv").open("a", encoding="utf-8") as handle:
            handle.write("unexpected row\n")
        with self.assertRaisesRegex(ValueError, "checksum"):
            load_evaluation(folder)
