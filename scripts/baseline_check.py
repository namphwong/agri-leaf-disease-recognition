"""Check the current CPU pipeline against the immutable pre-refactor reference.

Downloads exactly one pinned PlantVillage image per class only when requested.
These are smoke samples, not an independent test set.
"""

import argparse
import ast
import hashlib
import io
import json
import os
import platform
import socket
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "data" / "baseline"
REPORTS = ROOT / "reports" / "baseline"
MANIFEST = REPORTS / "samples.json"
REPO = "spMohanty/PlantVillage-Dataset"
REFERENCE_COMMIT = "7b021d59a970d6ae5da32cae81a0a4d025ad1748"
sys.path.insert(0, str(ROOT))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "agri-leaf-baseline"})
    with urllib.request.urlopen(request, timeout=90) as response:
        return response.read()


def app_contract():
    """Read the original implementation from Git, not the refactored services."""
    source = subprocess.check_output(["git", "-C", str(ROOT), "show", f"{REFERENCE_COMMIT}:app.py"])
    tree = ast.parse(source)
    classes = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "CLASSES" for t in node.targets)
    )
    selected = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "load_model":
            node.decorator_list = []
            selected.append(node)
        if isinstance(node, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "transform" for t in node.targets
        ):
            selected.append(node)
    return classes, selected


def download_samples(classes):
    revision = json.loads(fetch(f"https://api.github.com/repos/{REPO}/commits/master"))["sha"]
    raw_folders = json.loads(fetch(
        f"https://api.github.com/repos/{REPO}/contents/raw/color?ref={revision}"
    ))
    normalize = lambda value: value.replace("___", "_")
    samples = []
    SAMPLES.mkdir(parents=True, exist_ok=True)
    for label in classes:
        folder = next(item for item in raw_folders if normalize(item["name"]) == normalize(label))
        path = urllib.parse.quote(folder["path"], safe="/")
        listing = json.loads(fetch(
            f"https://api.github.com/repos/{REPO}/contents/{path}?ref={revision}"
        ))
        candidates = sorted(
            (item for item in listing if item["name"].lower().endswith((".jpg", ".jpeg", ".png"))),
            key=lambda item: item["name"],
        )
        sample = candidates[0]
        url = f"https://raw.githubusercontent.com/{REPO}/{revision}/" + urllib.parse.quote(sample["path"], safe="/")
        destination = SAMPLES / (label + Path(sample["name"]).suffix.lower())
        destination.write_bytes(fetch(url))
        samples.append({
            "expected": label,
            "local_path": destination.relative_to(ROOT).as_posix(),
            "source_path": sample["path"],
            "source_url": url,
            "git_blob_sha": sample["sha"],
            "sha256": sha256(destination),
            "bytes": destination.stat().st_size,
        })
    manifest = {
        "repository": f"https://github.com/{REPO}",
        "revision": revision,
        "selection": "First filename lexicographically in GitHub contents API response for each class; response may be capped at 1000 entries.",
        "purpose": "Six smoke samples; training overlap unknown; not an independent test set.",
        "license_reference": "https://huggingface.co/datasets/mohanty/PlantVillage",
        "samples": samples,
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def restore_samples(manifest):
    for sample in manifest["samples"]:
        path = ROOT / sample["local_path"]
        if not path.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(fetch(sample["source_url"]))
        if sha256(path) != sample["sha256"]:
            raise ValueError(f"Sample hash mismatch: {path}")


def check_http_server():
    """Start a loopback-only Streamlit process and clean it up after the check."""
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    command = [sys.executable, "-m", "streamlit", "run", str(ROOT / "app.py"),
               "--server.headless=true", "--server.address=127.0.0.1",
               f"--server.port={port}", "--browser.gatherUsageStats=false"]
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 30
        while time.monotonic() < deadline:
            if process.poll() is not None:
                raise RuntimeError("Streamlit server exited before health check")
            try:
                health = fetch(f"http://127.0.0.1:{port}/_stcore/health").decode()
                with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=5) as response:
                    status = response.status
                assert health == "ok" and status == 200
                return {"health": health, "root_status": status, "loopback_only": True}
            except (urllib.error.URLError, ConnectionError):
                time.sleep(0.25)
        raise TimeoutError("Streamlit server did not become healthy within 30s")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def run_checks(manifest, classes, selected, result_name):
    import importlib.metadata
    import numpy as np
    import torch
    import torch.nn as nn
    from PIL import Image
    from streamlit.testing.v1 import AppTest
    from torchvision import models, transforms
    from src.inference import load_model, predict
    from src.labels import CLASSES
    from src.preprocessing import build_transform, preprocess
    from src.validation import decode_image

    torch.manual_seed(0)
    checkpoint = ROOT / "models" / "leaf_model_final.pth"
    archived = json.loads((REPORTS / "results.json").read_text(encoding="utf-8"))
    assert sha256(checkpoint) == archived["checkpoint_sha256"]
    assert classes == archived["class_order"]
    namespace = {"models": models, "nn": nn, "torch": torch, "CLASSES": classes,
                 "MODEL_PATH": checkpoint, "transforms": transforms}
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(ROOT / "app.py"), "exec"), namespace)
    started = time.perf_counter()
    loaded = load_model(checkpoint)
    model = loaded.module
    load_ms = (time.perf_counter() - started) * 1000
    reference_model = namespace["load_model"]()
    transform = build_transform()
    assert list(CLASSES) == classes
    assert next(model.parameters()).device.type == "cpu"
    assert not model.training
    assert model.fc.out_features == len(classes) == 6

    notebook = json.loads((ROOT / "notebooks/plant_leaf_disease_classification_training.ipynb").read_text(encoding="utf-8"))
    notebook_code = "\n".join("".join(c["source"]) for c in notebook["cells"] if c["cell_type"] == "code")
    notebook_output = "\n".join("".join(o.get("text", [])) for c in notebook["cells"] for o in c.get("outputs", []))
    printed = next(line.removeprefix("Classes: ") for line in notebook_output.splitlines() if line.startswith("Classes: "))
    notebook_classes = ast.literal_eval(printed)
    normalized = lambda values: [v.replace("___", "_") for v in values]
    assert normalized(classes) == normalized(notebook_classes)
    eval_assignment = next(node for node in ast.parse(notebook_code).body
                           if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "eval_transform" for t in node.targets))
    eval_namespace = {"transforms": transforms}
    exec(compile(ast.Module(body=[eval_assignment], type_ignores=[]), "notebook-eval", "exec"), eval_namespace)
    test_image = Image.fromarray(np.random.default_rng(0).integers(0, 256, (257, 331, 3), dtype=np.uint8))
    assert torch.equal(transform(test_image), eval_namespace["eval_transform"](test_image))
    assert torch.equal(preprocess(test_image), namespace["transform"](test_image.convert("RGB")).unsqueeze(0))

    predictions = []
    regression_deltas = []
    for sample in manifest["samples"]:
        path = ROOT / sample["local_path"]
        with Image.open(path) as original:
            image = original.convert("RGB")
            original_size = list(original.size)
        tensor = transform(image).unsqueeze(0)
        assert tensor.shape == (1, 3, 224, 224)
        with torch.no_grad():
            model(tensor)  # One warm-up; timing below excludes file I/O/preprocessing.
            durations = []
            for _ in range(5):
                started = time.perf_counter()
                output = model(tensor)
                durations.append((time.perf_counter() - started) * 1000)
            probabilities = torch.softmax(output, dim=1)[0]
        assert torch.isfinite(probabilities).all()
        assert abs(probabilities.sum().item() - 1) < 1e-5
        current_result = predict(loaded, decode_image(path.read_bytes()))
        with torch.no_grad():
            reference_tensor = namespace["transform"](image).unsqueeze(0)
            reference_scores = torch.softmax(reference_model(reference_tensor), dim=1)[0]
        delta = max(abs(score - reference_scores[index].item()) for index, score in enumerate(current_result.probabilities))
        assert delta <= 1e-7, delta
        assert current_result.label == classes[int(reference_scores.argmax())]
        expected_top3 = sorted(range(6), key=lambda index: reference_scores[index].item(), reverse=True)[:3]
        assert [item.class_index for item in current_result.top3] == expected_top3
        regression_deltas.append({"expected": sample["expected"], "max_abs_probability_delta": delta})
        archived_prediction = archived["predictions"][len(predictions)]
        assert archived_prediction["expected"] == sample["expected"]
        assert current_result.label == archived_prediction["predicted"]
        assert abs(current_result.confidence - archived_prediction["confidence"]) <= 1e-7
        for current, previous in zip(current_result.top3, archived_prediction["top3"]):
            assert current.label == previous["label"] and abs(current.score - previous["score"]) <= 1e-7
        values, indices = torch.topk(probabilities, 3)
        predicted = classes[indices[0].item()]
        predictions.append({
            "expected": sample["expected"], "predicted": predicted,
            "match": predicted == sample["expected"], "original_size": original_size,
            "confidence": values[0].item(),
            "top3": [{"label": classes[idx.item()], "score": value.item()} for value, idx in zip(values, indices)],
            "forward_ms": durations, "median_forward_ms": statistics.median(durations),
        })

    def app_run(payload=None):
        test = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60)
        if payload is None:
            test.run()
        else:
            with patch("streamlit.file_uploader", return_value=payload):
                test.run()
                if any(button.key == "analyze" for button in test.button):
                    test.button(key="analyze").click().run()
        assert not test.exception, [str(item.value) for item in test.exception]
        return test

    startup = app_run()
    assert not startup.error, [item.value for item in startup.error]
    app_uploads = []
    for sample, prediction in zip(manifest["samples"], predictions):
        app = app_run(io.BytesIO((ROOT / sample["local_path"]).read_bytes()))
        assert not app.error, [item.value for item in app.error]
        from src.labels import vietnamese_label
        expected_label = vietnamese_label(prediction["predicted"])
        assert expected_label in [item.value for item in app.subheader]
        confidence_metric = next(item for item in app.metric if item.label == "Điểm tin cậy")
        assert confidence_metric.value == f'{prediction["confidence"] * 100:.2f}%'
        app_uploads.append({"expected": sample["expected"], "rendered_label": expected_label,
                            "rendered_confidence": confidence_metric.value, "pass": True})
    corrupt = app_run(io.BytesIO(b"this is not a valid image"))
    assert any("Không thể đọc ảnh" in item.value for item in corrupt.error)
    http_server = check_http_server()

    all_times = [value for prediction in predictions for value in prediction["forward_ms"]]
    report = {
        "timestamp": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "processor": platform.processor(), "logical_cpus": os.cpu_count(),
        "torch_threads": torch.get_num_threads(), "device": "cpu",
        "versions": {name: importlib.metadata.version(name) for name in ["torch", "torchvision", "streamlit", "pillow", "numpy"]},
        "checkpoint_sha256": sha256(checkpoint), "checkpoint_bytes": checkpoint.stat().st_size,
        "app_sha256": sha256(ROOT / "app.py"),
        "notebook_sha256": sha256(ROOT / "notebooks/plant_leaf_disease_classification_training.ipynb"),
        "class_order": classes, "notebook_printed_classes": notebook_classes,
        "checks": {"checkpoint_cpu_load": True, "semantic_class_order": True,
                   "eval_transform_tensor_equal": True, "app_startup": True,
                   "app_six_uploads": True, "invalid_image_handled": True,
                   "http_server_health": True, "pre_refactor_probabilities_match": True,
                   "archived_phase2_checkpoint_and_predictions_match": True},
        "regression_reference_commit": REFERENCE_COMMIT,
        "regression_tolerance": 1e-7,
        "regression_deltas": regression_deltas,
        "service_sha256": {path.relative_to(ROOT / "src").as_posix(): sha256(path) for path in sorted((ROOT / "src").rglob("*.py"))},
        "http_server": http_server,
        "notebook_caveats": ["Tomato labels use single underscores; app uses triple underscores; semantic order matches.",
                             "Notebook save filename leaf_model_v2.pth differs from bundled leaf_model_final.pth; original training provenance is not fully reconstructible.",
                             "Original split indices/seed are not saved; smoke samples may overlap training data."],
        "model_load_ms": load_ms, "median_forward_ms": statistics.median(all_times),
        "timing_protocol": "One warm-up per image; 5 CPU forwards per image; excludes decode, preprocessing, UI and softmax; default PyTorch thread count.",
        "sample_matches": sum(p["match"] for p in predictions), "sample_count": len(predictions),
        "not_independent_test": True,
        "predictions": predictions, "app_upload_checks": app_uploads,
        "ui_check_method": "Streamlit AppTest, file_uploader patched to BytesIO; real app prediction and render path executed. Native browser upload not automated.",
    }
    (REPORTS / result_name).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["versions", "checks", "sample_matches", "sample_count", "median_forward_ms"]}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download-samples", action="store_true", help="Select samples and overwrite manifest; only for first preparation")
    parser.add_argument("--restore-samples", action="store_true", help="Restore pinned samples from the existing manifest")
    parser.add_argument("--result-name", default="current-results.json", help="Output JSON filename inside reports/baseline; preserves Phase 2 results")
    args = parser.parse_args()
    if Path(args.result_name).name != args.result_name or not args.result_name.endswith(".json"):
        parser.error("--result-name must be a plain .json filename")
    REPORTS.mkdir(parents=True, exist_ok=True)
    classes, selected = app_contract()
    if args.download_samples:
        manifest = download_samples(classes)
    else:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if [sample["expected"] for sample in manifest["samples"]] != classes:
        raise ValueError("Manifest must contain exactly one sample per class in app order")
    if args.restore_samples:
        restore_samples(manifest)
    for sample in manifest["samples"]:
        if sha256(ROOT / sample["local_path"]) != sample["sha256"]:
            raise ValueError("Sample checksum mismatch")
    run_checks(manifest, classes, selected, args.result_name)


if __name__ == "__main__":
    main()
