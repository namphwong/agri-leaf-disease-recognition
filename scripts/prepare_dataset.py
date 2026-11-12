"""Prepare/audit six pinned PlantVillage classes; no training or model evaluation.

Raw images stay under ignored data/. Committed reports contain metadata only.
"""

import argparse
import ast
import csv
import hashlib
import io
import json
import random
import subprocess
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "plantvillage-source"
REPORTS = ROOT / "reports" / "dataset"
REPOSITORY = "https://github.com/spMohanty/PlantVillage-Dataset.git"
REVISION = "7f7ecc7e1eaca78107e3affe7cb5abd9427e139a"
SEED = 42


def git(*args):
    return subprocess.check_output(["git", "-C", str(SOURCE), *args], text=True, encoding="utf-8").strip()


def classes_from_app():
    tree = ast.parse((ROOT / "app.py").read_text(encoding="utf-8"))
    return next(ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "CLASSES" for t in node.targets))


def download(classes):
    SOURCE.mkdir(parents=True, exist_ok=True)
    if not (SOURCE / ".git").exists():
        git("init")
        git("remote", "add", "origin", REPOSITORY)
    if git("remote", "get-url", "origin") != REPOSITORY:
        raise ValueError("Unexpected source repository; refusing to change it")
    if git("status", "--porcelain"):
        raise ValueError("Source checkout has local changes; refusing to overwrite them")
    git("config", "remote.origin.promisor", "true")
    git("config", "remote.origin.partialclonefilter", "blob:none")
    git("fetch", "--depth=1", "--filter=blob:none", "origin", REVISION)
    git("sparse-checkout", "init", "--cone")
    git("sparse-checkout", "set", *[f"raw/color/{label}" for label in classes])
    git("checkout", "--detach", REVISION)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def leaf_candidates(filename, label, leaf_map):
    # Match the identifier extraction in the pinned official plant_village.py.
    identifier = filename.replace("_final_masked", "").split("___")[-1].split("copy")[0]
    for extension in (".jpg", ".JPG", ".png", ".PNG"):
        identifier = identifier.replace(extension, "")
    suggestions = leaf_map.get(identifier.strip().lower(), [])
    # Keep *all* matching candidates, conservatively linking ambiguous leaves.
    return sorted({item for item in suggestions if item.split(":::")[0] == label})


def inspect_image(item):
    path, label, label_index, blob_sha, leaf_map = item
    relative = path.relative_to(SOURCE).as_posix()
    payload = path.read_bytes()
    actual_blob = hashlib.sha1(b"blob " + str(len(payload)).encode() + b"\0" + payload).hexdigest()
    if actual_blob != blob_sha:
        raise ValueError(f"Source bytes differ from pinned Git blob: {relative}")
    row = {"source_path": relative, "local_path": path.relative_to(ROOT).as_posix(),
           "label": label, "label_index": label_index, "git_blob_sha": blob_sha,
           "sha256": digest(payload), "bytes": len(payload), "width": "", "height": "",
           "mode": "", "rgb_sha256": "", "leaf_ids": leaf_candidates(path.name, label, leaf_map),
           "error": ""}
    try:
        with Image.open(io.BytesIO(payload)) as image:
            image.verify()
        with Image.open(io.BytesIO(payload)) as image:
            image.load()
            row.update(width=image.width, height=image.height, mode=image.mode)
            rgb = image.convert("RGB")
            row["rgb_sha256"] = digest(f"{rgb.width}x{rgb.height}:".encode() + rgb.tobytes())
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        row["error"] = f"{type(exc).__name__}: {exc}"
    return row


class Components:
    def __init__(self, n):
        self.parent = list(range(n))

    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a, b):
        a, b = self.find(a), self.find(b)
        if a != b:
            self.parent[max(a, b)] = min(a, b)


def connect_and_split(rows, seed):
    components = Components(len(rows))
    owners = {}
    for index, row in enumerate(rows):
        keys = [("leaf", leaf) for leaf in row["leaf_ids"]]
        keys.append(("file", row["sha256"]))
        if row["rgb_sha256"]:
            keys.append(("rgb", row["rgb_sha256"]))
        for key in keys:
            if key in owners:
                components.union(index, owners[key])
            else:
                owners[key] = index
    groups = defaultdict(list)
    for index in range(len(rows)):
        groups[components.find(index)].append(index)
    by_class = defaultdict(list)
    for members in groups.values():
        group_id = digest("\n".join(sorted(rows[i]["source_path"] for i in members)).encode())[:24]
        reasons = []
        if any(rows[i]["error"] for i in members):
            reasons.append("decode_error")
        if any(not rows[i]["leaf_ids"] for i in members):
            reasons.append("unresolved_leaf_id")
        if len({rows[i]["label"] for i in members}) > 1:
            reasons.append("conflicting_labels")
        for index in members:
            rows[index].update(group_id=group_id, split="quarantine" if reasons else "",
                               quarantine_reason=";".join(reasons))
        if not reasons:
            by_class[rows[members[0]]["label"]].append((group_id, members))
    for label in sorted(by_class):
        ordered = sorted(by_class[label])
        random.Random(f"{seed}:{label}").shuffle(ordered)
        n = len(ordered)
        if n < 3:
            raise ValueError(f"Too few independent groups for a three-way split: {label}")
        n_train = min(n - 2, max(1, int(0.7 * n)))
        n_val = min(n - n_train - 1, max(1, int(0.15 * n)))
        for position, (_, members) in enumerate(ordered):
            split = "train" if position < n_train else "validation" if position < n_train + n_val else "test"
            for index in members:
                rows[index]["split"] = split
    # Keep one representative per exact decoded image in each component.
    # Conflicting/corrupt/unresolved components have already been quarantined.
    representatives = set()
    for row in sorted(rows, key=lambda r: r["source_path"]):
        if row["split"] == "quarantine":
            row["use_for_training_evaluation"] = False
            row["exclusion_reason"] = row["quarantine_reason"]
        else:
            duplicate_key = (row["group_id"], row["rgb_sha256"])
            row["use_for_training_evaluation"] = duplicate_key not in representatives
            row["exclusion_reason"] = "exact_rgb_duplicate" if duplicate_key in representatives else ""
            representatives.add(duplicate_key)
    return len(groups)


def duplicate_groups(rows, field):
    buckets = defaultdict(list)
    for row in rows:
        if row[field]:
            buckets[row[field]].append(row["source_path"])
    return [{"hash": value, "paths": paths} for value, paths in sorted(buckets.items()) if len(paths) > 1]


def assert_integrity(rows, classes):
    assert len({r["source_path"] for r in rows}) == len(rows)
    assert set(r["label"] for r in rows) == set(classes)
    for field in ("group_id", "sha256", "rgb_sha256"):
        partitions = defaultdict(set)
        for row in rows:
            if row[field] and row["split"] != "quarantine":
                partitions[row[field]].add(row["split"])
        assert all(len(splits) == 1 for splits in partitions.values()), field
    leaf_partitions = defaultdict(set)
    for row in rows:
        if row["split"] != "quarantine":
            assert row["leaf_ids"] and not row["error"]
            for leaf_id in row["leaf_ids"]:
                leaf_partitions[leaf_id].add(row["split"])
    assert all(len(splits) == 1 for splits in leaf_partitions.values())
    selected_hashes = [r["rgb_sha256"] for r in rows if r["use_for_training_evaluation"]]
    assert len(selected_hashes) == len(set(selected_hashes))
    for label in classes:
        for split in ("train", "validation", "test"):
            assert any(r["label"] == label and r["split"] == split and r["use_for_training_evaluation"] for r in rows)


def csv_bytes(rows, fields):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        serial = {key: row[key] for key in fields}
        if "leaf_ids" in serial:
            serial["leaf_ids"] = json.dumps(serial["leaf_ids"], ensure_ascii=False)
        writer.writerow(serial)
    return output.getvalue().encode("utf-8")


def audit(classes):
    if git("rev-parse", "HEAD") != REVISION or git("status", "--porcelain"):
        raise ValueError("Source must be a clean checkout of the pinned revision")
    leaf_bytes = subprocess.check_output(["git", "-C", str(SOURCE), "show", "HEAD:leaf-map.json"])
    readme_bytes = subprocess.check_output(["git", "-C", str(SOURCE), "show", "HEAD:README_HF.md"])
    leaf_map = json.loads(leaf_bytes)
    listing = git("ls-tree", "-r", "HEAD", "--", *[f"raw/color/{label}" for label in classes])
    blobs = {}
    for line in listing.splitlines():
        header, path = line.split("\t", 1)
        blobs[path] = header.split()[2]
    tasks = []
    for index, label in enumerate(classes):
        paths = sorted((SOURCE / "raw" / "color" / label).iterdir())
        for path in paths:
            if path.is_file():
                relative = path.relative_to(SOURCE).as_posix()
                tasks.append((path, label, index, blobs[relative], leaf_map))
    assert len(tasks) == len(blobs), "Missing source files"
    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(inspect_image, tasks))
    rows.sort(key=lambda row: row["source_path"])
    group_count = connect_and_split(rows, SEED)
    assert_integrity(rows, classes)
    # Independently reassign on copies in reverse input order to prove stable membership.
    replay = [dict(row) for row in reversed(rows)]
    connect_and_split(replay, SEED)
    expected = {row["source_path"]: (row["group_id"], row["split"], row["use_for_training_evaluation"]) for row in rows}
    assert all(expected[row["source_path"]] == (row["group_id"], row["split"], row["use_for_training_evaluation"]) for row in replay)
    per_class = []
    for label in classes:
        selected = [r for r in rows if r["label"] == label]
        per_class.append({"label": label, "images": len(selected),
                          "leaf_ids": len({leaf for r in selected for leaf in r["leaf_ids"]}),
                          "components": len({r["group_id"] for r in selected}),
                          "unresolved": sum(not r["leaf_ids"] for r in selected),
                          "quarantine": sum(r["split"] == "quarantine" for r in selected),
                          "deduplicated_exclusions": sum(r["exclusion_reason"] == "exact_rgb_duplicate" for r in selected),
                          **{split: sum(r["split"] == split and r["use_for_training_evaluation"] for r in selected)
                             for split in ("train", "validation", "test")}})
    fields = list(rows[0])
    manifest = csv_bytes(rows, fields)
    duplicates = {"byte_identical": duplicate_groups(rows, "sha256"),
                  "decoded_rgb_identical": duplicate_groups(rows, "rgb_sha256")}
    summary = {
        "created_at": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(),
        "repository": REPOSITORY, "revision": REVISION,
        "license_declaration": "CC BY-SA 3.0 per upstream dataset card; see docs/dataset.md",
        "source_readme_sha256": digest(readme_bytes),
        "leaf_map_sha256": digest(leaf_bytes),
        "manifest_sha256": digest(manifest), "seed": SEED,
        "split_method": "Per-class connected components of official leaf IDs + byte/RGB duplicates; 70/15/remainder by shuffled group count, not image count. Unresolved/corrupt/conflicting components quarantined. One representative per exact RGB image retained.",
        "images": len(rows), "bytes": sum(r["bytes"] for r in rows),
        "size_distribution": dict(Counter(f'{r["width"]}x{r["height"]}' for r in rows)),
        "mode_distribution": dict(Counter(r["mode"] for r in rows)),
        "decode_errors": [{"source_path": r["source_path"], "error": r["error"]} for r in rows if r["error"]],
        "connected_components": group_count,
        "ambiguous_leaf_mappings": sum(len(r["leaf_ids"]) > 1 for r in rows),
        "unresolved_leaf_mappings": sum(not r["leaf_ids"] for r in rows),
        "quarantined_images": sum(r["split"] == "quarantine" for r in rows),
        "selected_images": sum(r["use_for_training_evaluation"] for r in rows),
        "selected_components": len({r["group_id"] for r in rows if r["use_for_training_evaluation"]}),
        "split_counts": dict(Counter(r["split"] for r in rows if r["use_for_training_evaluation"])),
        "byte_duplicate_groups": len(duplicates["byte_identical"]),
        "rgb_duplicate_groups": len(duplicates["decoded_rgb_identical"]),
        "excluded_exact_rgb_duplicates": sum(r["exclusion_reason"] == "exact_rgb_duplicate" for r in rows),
        "class_imbalance_max_min": max(c["images"] for c in per_class) / min(c["images"] for c in per_class),
        "per_class": per_class,
        "checks": {"all_git_blobs_match": True, "all_classes_in_all_splits": True,
                   "no_group_leaf_or_exact_duplicate_cross_split": True,
                   "unique_rgb_in_selected_rows": True, "split_reproducible_on_reversed_input": True},
        "not_independent_for_inherited_checkpoint": True,
        "limitations": ["Leaf metadata may be incomplete or wrong; cannot prove physical independence beyond source metadata.",
                        "Near-duplicate/perceptual similarity not exhaustively audited.",
                        "No original checkpoint train/test membership; this split is for future retraining, not independent evaluation of the inherited model."]}
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "manifest.csv").write_bytes(manifest)
    for name, value in (("summary.json", summary), ("duplicates.json", duplicates),
                        ("labels.json", [{"index": i, "label": label, "crop": label.split("___")[0],
                                         "condition": label.split("___")[1]} for i, label in enumerate(classes)])):
        (REPORTS / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (REPORTS / "class_distribution.csv").write_bytes(csv_bytes(per_class, list(per_class[0])))
    demo_rows = [next(r for r in rows if r["label"] == label and r["split"] == "train" and r["use_for_training_evaluation"]) for label in classes]
    (REPORTS / "demo_samples.json").write_text(json.dumps({
        "purpose": "UI demo candidates selected only from the new training partition; not test examples.",
        "samples": [{key: row[key] for key in ("label", "local_path", "source_path", "sha256", "group_id", "split")} for row in demo_rows]
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({key: summary[key] for key in ("images", "bytes", "decode_errors", "unresolved_leaf_mappings", "quarantined_images", "rgb_duplicate_groups", "per_class", "checks")}, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--download", action="store_true", help="Fetch pinned sparse source checkout (requires Git and internet)")
    args = parser.parse_args()
    classes = classes_from_app()
    if args.download:
        download(classes)
    audit(classes)


if __name__ == "__main__":
    main()
