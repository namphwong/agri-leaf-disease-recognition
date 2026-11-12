"""Pinned UI examples selected from the Phase 3 training partition."""

import hashlib
import json
import urllib.parse
import urllib.request

from src.config import PROJECT_ROOT

REVISION = "7f7ecc7e1eaca78107e3affe7cb5abd9427e139a"


def sample_manifest() -> list[dict]:
    return json.loads((PROJECT_ROOT / "reports/dataset/demo_samples.json").read_text(encoding="utf-8"))["samples"]


def sample_bytes(index: int) -> bytes:
    sample = sample_manifest()[index]
    local = PROJECT_ROOT / sample["local_path"]
    if local.is_file():
        payload = local.read_bytes()
    else:
        url = f"https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/{REVISION}/" + urllib.parse.quote(sample["source_path"], safe="/")
        request = urllib.request.Request(url, headers={"User-Agent": "agri-leaf-demo"})
        with urllib.request.urlopen(request, timeout=15) as response:
            payload = response.read(20 * 1024 * 1024 + 1)
    if hashlib.sha256(payload).hexdigest() != sample["sha256"]:
        raise ValueError("Ảnh mẫu không khớp phiên bản đã kiểm chứng.")
    return payload
