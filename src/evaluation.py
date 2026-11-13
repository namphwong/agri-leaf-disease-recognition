"""Validate published evaluation against prediction rows and the pinned manifest."""

import csv
import hashlib
import json
import math
from pathlib import Path

from src.config import DEFAULT_MODEL_PATH, PROJECT_ROOT
from src.labels import CLASSES
from src.metrics import classification_metrics

EVALUATION_PATH = PROJECT_ROOT / "reports" / "evaluation"


def file_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_evaluation(folder: Path = EVALUATION_PATH) -> dict:
    report = json.loads((folder / "latest.json").read_text(encoding="utf-8"))
    if report.get("schema_version") != 1 or report.get("scope") != "descriptive_inherited_checkpoint" or report.get("independent_test") is not False:
        raise ValueError("Unknown evaluation scope or schema")
    if report["labels"] != list(CLASSES):
        raise ValueError("Evaluation class order mismatch")
    if file_sha(DEFAULT_MODEL_PATH) != report["checkpoint_sha256"]:
        raise ValueError("Evaluation checkpoint mismatch")
    manifest_path = PROJECT_ROOT / "reports/dataset/manifest.csv"
    if file_sha(manifest_path) != report["manifest_sha256"]:
        raise ValueError("Evaluation manifest mismatch")
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        expected = {row["source_path"]: row for row in csv.DictReader(handle)
                    if row["split"] == "test" and row["use_for_training_evaluation"] == "True"}
    if file_sha(folder / "predictions.csv") != report["predictions_sha256"]:
        raise ValueError("Prediction artifact checksum mismatch")
    matrix = [[0] * 6 for _ in range(6)]
    seen = set()
    groups = set()
    with (folder / "predictions.csv").open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            source = row["source_path"]
            if source not in expected or source in seen:
                raise ValueError("Unexpected or repeated evaluation image")
            seen.add(source)
            original = expected[source]
            true_index, predicted_index = int(row["expected_index"]), int(row["predicted_index"])
            if (true_index != int(original["label_index"]) or not 0 <= predicted_index < 6
                    or row["image_sha256"] != original["sha256"] or row["group_id"] != original["group_id"]
                    or row["expected"] != CLASSES[true_index] or row["predicted"] != CLASSES[predicted_index]):
                raise ValueError("Prediction metadata mismatch")
            scores = [float(row[f"probability_{i}"]) for i in range(6)]
            if (not all(math.isfinite(value) and 0 <= value <= 1 for value in scores)
                    or abs(sum(scores) - 1) > 1e-5 or max(range(6), key=lambda i: scores[i]) != predicted_index
                    or abs(float(row["confidence"]) - scores[predicted_index]) > 1e-7
                    or row["correct"] != str(true_index == predicted_index)):
                raise ValueError("Prediction scores mismatch")
            matrix[true_index][predicted_index] += 1
            groups.add(row["group_id"])
    if seen != set(expected) or matrix != report["confusion_matrix"] or len(groups) != report["groups"]:
        raise ValueError("Evaluation cohort or confusion matrix mismatch")
    computed = classification_metrics(matrix, list(CLASSES))
    for name in ("accuracy", "macro_precision", "macro_recall", "macro_f1", "weighted_f1", "sample_count"):
        if abs(computed[name] - report["metrics"][name]) > 1e-12:
            raise ValueError(f"Reported metric mismatch: {name}")
    if computed["per_class"] != report["metrics"]["per_class"]:
        raise ValueError("Per-class metrics mismatch")
    for name, expected_sha in report["figures_sha256"].items():
        if name not in {"confusion_matrix.png", "latency.png", "examples.png"} or file_sha(folder / name) != expected_sha:
            raise ValueError("Figure checksum mismatch")
    return report
