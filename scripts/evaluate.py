"""Descriptive evaluation of inherited checkpoint on the fixed manifest test rows.

Training overlap is unknown. This command never trains or selects a model.
"""

import csv
import hashlib
import io
import json
import platform
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import DEFAULT_MODEL_PATH
from src.inference import load_model, predict
from src.labels import CLASSES
from src.metrics import classification_metrics
from src.validation import decode_image

OUTPUT = ROOT / "reports" / "evaluation"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def figures(report, predictions):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    labels = [label.replace("___", "\n").replace("_", " ") for label in CLASSES]
    matrix = np.array(report["confusion_matrix"])
    fractions = matrix / matrix.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(9, 7.5))
    heatmap = ax.imshow(fractions, cmap="Greens", vmin=0, vmax=1)
    ax.set(xticks=range(6), yticks=range(6), xticklabels=labels, yticklabels=labels,
           xlabel="Predicted class", ylabel="Dataset label",
           title=f'Descriptive verification: {len(predictions)} images\nInherited checkpoint; training overlap unknown')
    plt.setp(ax.get_xticklabels(), rotation=35, ha="right", fontsize=9)
    plt.setp(ax.get_yticklabels(), fontsize=9)
    for i in range(6):
        for j in range(6):
            ax.text(j, i, f"{matrix[i,j]}\n{fractions[i,j]:.1%}", ha="center", va="center",
                    color="white" if fractions[i,j] > .55 else "#183c2b", fontsize=9)
    fig.colorbar(heatmap, ax=ax, label="Fraction within true class", shrink=.7)
    fig.tight_layout()
    fig.savefig(OUTPUT / "confusion_matrix.png", dpi=160)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist([row["decode_predict_ms"] for row in predictions], bins=24, color="#277A53", edgecolor="white")
    ax.set(xlabel="Decode + preprocessing + CPU prediction (ms/image)", ylabel="Images",
           title="Local latency distribution (after warm-up; excludes file I/O)")
    fig.tight_layout()
    fig.savefig(OUTPUT / "latency.png", dpi=160)
    plt.close(fig)

    errors = sorted((p for p in predictions if not p["correct"]), key=lambda p: (-p["confidence"], p["source_path"]))[:6]
    correct = []
    for index in range(6):
        candidates = [p for p in predictions if p["correct"] and p["expected_index"] == index]
        if candidates:
            correct.append(min(candidates, key=lambda p: (p["confidence"], p["source_path"])))
    examples = correct + errors
    fig, axes = plt.subplots(4, 3, figsize=(12, 14))
    for ax in axes.flat:
        ax.axis("off")
    for ax, prediction in zip(axes.flat, examples):
        with Image.open(ROOT / prediction["local_path"]) as image:
            ax.imshow(image.convert("RGB"))
        status = "MATCH" if prediction["correct"] else "ERROR"
        expected = CLASSES[prediction["expected_index"]].replace("___", " / ").replace("_", " ")
        predicted = CLASSES[prediction["predicted_index"]].replace("___", " / ").replace("_", " ")
        ax.set_title(f'{status} | label: {expected}\npred: {predicted} ({prediction["confidence"]:.1%})',
                     fontsize=9, color="#176B4C" if prediction["correct"] else "#9f392f")
    fig.suptitle("Examples selected after evaluation: lowest-score match per class + highest-score errors\nNot an independent test of the inherited checkpoint", fontsize=12)
    fig.text(.5, .015, "Leaf images: PlantVillage, Mohanty et al. (2016), CC BY-SA 3.0 per dataset card. Source paths: examples.json.", ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .035, 1, .95))
    fig.savefig(OUTPUT / "examples.png", dpi=140)
    plt.close(fig)
    write_json(OUTPUT / "examples.json", {"selection": "One lowest-confidence correct image per class, followed by up to six highest-confidence errors; no retuning.", "examples": examples})


def main():
    import importlib.metadata
    import numpy as np
    import torch

    manifest_path = ROOT / "reports/dataset/manifest.csv"
    summary = json.loads((ROOT / "reports/dataset/summary.json").read_text(encoding="utf-8"))
    if sha(manifest_path) != summary["manifest_sha256"]:
        raise ValueError("Dataset manifest checksum changed")
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        rows = [row for row in csv.DictReader(handle) if row["split"] == "test" and row["use_for_training_evaluation"] == "True"]
    assert len(rows) == summary["split_counts"]["test"] == 776
    assert {int(row["label_index"]) for row in rows} == set(range(6))
    torch.manual_seed(0)
    loaded = load_model()
    archived = json.loads((ROOT / "reports/baseline/results.json").read_text(encoding="utf-8"))
    assert loaded.checkpoint_sha256 == archived["checkpoint_sha256"]
    payload = (ROOT / rows[0]["local_path"]).read_bytes()
    for _ in range(3):
        predict(loaded, decode_image(payload))
    matrix = [[0] * 6 for _ in range(6)]
    group_matrices = defaultdict(lambda: np.zeros((6, 6), dtype=np.int64))
    predictions = []
    started = time.perf_counter()
    for position, row in enumerate(rows, 1):
        path = ROOT / row["local_path"]
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != row["sha256"]:
            raise ValueError(f'Image checksum changed: {row["source_path"]}')
        begin = time.perf_counter()
        image = decode_image(payload)
        predict_begin = time.perf_counter()
        result = predict(loaded, image)
        end = time.perf_counter()
        expected = int(row["label_index"])
        assert row["label"] == CLASSES[expected]
        matrix[expected][result.class_index] += 1
        group_matrices[row["group_id"]][expected, result.class_index] += 1
        predictions.append({"source_path": row["source_path"], "local_path": row["local_path"],
                            "group_id": row["group_id"], "image_sha256": row["sha256"],
                            "expected_index": expected, "predicted_index": result.class_index,
                            "expected": row["label"], "predicted": result.label,
                            "correct": expected == result.class_index, "confidence": result.confidence,
                            "probabilities": result.probabilities,
                            "predict_ms": (end - predict_begin) * 1000,
                            "decode_predict_ms": (end - begin) * 1000})
        if position % 100 == 0:
            print(f"Evaluated {position}/{len(rows)}", flush=True)
    elapsed = time.perf_counter() - started
    metrics = classification_metrics(matrix, list(CLASSES))
    group_values = np.stack([group_matrices[key] for key in sorted(group_matrices)])
    rng = np.random.default_rng(42)
    bootstrap = []
    for _ in range(1000):
        draw = group_values[rng.integers(0, len(group_values), len(group_values))].sum(axis=0)
        value = classification_metrics(draw.tolist(), list(CLASSES))
        bootstrap.append((value["accuracy"], value["macro_f1"]))
    intervals = np.quantile(np.array(bootstrap), [.025, .975], axis=0)
    durations = [p["decode_predict_ms"] for p in predictions]
    source_paths = [ROOT / "scripts/evaluate.py", ROOT / "src/metrics.py", ROOT / "src/inference.py", ROOT / "src/preprocessing.py", ROOT / "src/labels.py", ROOT / "src/validation.py"]
    report = {
        "schema_version": 1, "created_at": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(),
        "scope": "descriptive_inherited_checkpoint", "independent_test": False,
        "warning_vi": "Kiểm chứng trên 776 ảnh thuộc partition test mới. Checkpoint kế thừa có thể đã học các ảnh này; không phải test độc lập hoặc ước lượng tổng quát ngoài đồng.",
        "split": "test", "manifest_sha256": sha(manifest_path), "dataset_revision": summary["revision"],
        "checkpoint_sha256": loaded.checkpoint_sha256, "model_version": loaded.model_version,
        "labels": list(CLASSES), "confusion_matrix": matrix, "metrics": metrics,
        "groups": len(group_values), "bootstrap": {"unit": "group_id", "replicates": 1000, "seed": 42,
            "method": "Percentile group bootstrap, fixed six classes, zero_division=0; conditional on this dataset, not evidence of independent generalization.",
            "accuracy_95_interval": intervals[:, 0].tolist(), "macro_f1_95_interval": intervals[:, 1].tolist()},
        "timing": {"warm_up_predictions": 3, "device": "cpu", "torch_threads": torch.get_num_threads(),
                   "median_decode_predict_ms": statistics.median(durations), "p95_decode_predict_ms": float(np.quantile(durations, .95)),
                   "median_predict_ms": statistics.median(p["predict_ms"] for p in predictions),
                   "total_loop_seconds": elapsed, "protocol": "Sequential single-image CPU production API; decode_predict includes validation/decode/preprocess/forward/softmax, excludes file I/O/checksum. No tuning."},
        "environment": {"python": platform.python_version(), "platform": platform.platform(), "processor": platform.processor(),
                        "versions": {name: importlib.metadata.version(name) for name in ("torch", "torchvision", "pillow", "numpy", "matplotlib")}},
        "code_base_commit": subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip(),
        "source_sha256": {path.relative_to(ROOT).as_posix(): sha(path) for path in source_paths},
        "limitations": ["Original checkpoint training membership is unknown; overlap cannot be ruled out.",
                        "Only mapped, non-quarantined test rows are included; 1582 unresolved images excluded in Phase 3.",
                        "Physical independence depends on upstream leaf metadata; near duplicates not exhaustively excluded.",
                        "Potato healthy test contains only 7 leaf groups (28 images).", "No threshold/model tuning or retraining performed."]}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    fields = [key for key in predictions[0] if key != "probabilities"] + [f"probability_{i}" for i in range(6)]
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for prediction in predictions:
        writer.writerow({**{key: value for key, value in prediction.items() if key != "probabilities"},
                         **{f"probability_{i}": value for i, value in enumerate(prediction["probabilities"])}})
    (OUTPUT / "predictions.csv").write_text(buffer.getvalue(), encoding="utf-8", newline="\n")
    report["predictions_sha256"] = sha(OUTPUT / "predictions.csv")
    figures(report, predictions)
    report["figures_sha256"] = {name: sha(OUTPUT / name) for name in ("confusion_matrix.png", "latency.png", "examples.png")}
    write_json(OUTPUT / "latest.json", report)
    print(json.dumps({"accuracy": metrics["accuracy"], "macro_f1": metrics["macro_f1"], "samples": len(rows), "groups": len(group_values), "timing": report["timing"]}, indent=2))


if __name__ == "__main__":
    main()
