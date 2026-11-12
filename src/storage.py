"""History record contract for Phase 5. No database or file writes yet."""

from __future__ import annotations

import hashlib
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.inference import PredictionResult


def make_history_record(result: PredictionResult, image_name: str, image_bytes: bytes) -> dict:
    """Return a versioned, JSON-serializable record without retaining image bytes."""
    return {
        "schema_version": 1,
        "created_at": datetime.now(ZoneInfo("Asia/Bangkok")).isoformat(),
        "image_name": image_name.replace("\\", "/").rsplit("/", 1)[-1],
        "image_sha256": hashlib.sha256(image_bytes).hexdigest(),
        "prediction": result.to_dict(),
    }
