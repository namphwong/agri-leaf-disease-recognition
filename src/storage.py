"""Local SQLite history. Store a preview only after an explicit save."""

from __future__ import annotations

import hashlib
import csv
import io
import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from zoneinfo import ZoneInfo
from typing import TYPE_CHECKING

from src.config import history_path
from src.labels import CLASSES

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


class HistoryError(RuntimeError):
    """Storage is unavailable; prediction can continue independently."""


class HistoryStore:
    def __init__(self, path: str | Path | None = None):
        self.path = Path(path) if path is not None else history_path()

    @contextmanager
    def _connection(self):
        connection = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            connection = sqlite3.connect(self.path, timeout=10)
            connection.row_factory = sqlite3.Row
            connection.create_function("casefold", 1, lambda value: value.casefold() if isinstance(value, str) else "", deterministic=True)
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise HistoryError("Phiên bản dữ liệu lịch sử chưa được hỗ trợ.")
            connection.execute("""CREATE TABLE IF NOT EXISTS predictions (
                id TEXT PRIMARY KEY, created_at TEXT NOT NULL, image_name TEXT NOT NULL,
                image_sha256 TEXT NOT NULL, label TEXT NOT NULL, confidence REAL NOT NULL,
                model_version TEXT NOT NULL, checkpoint_sha256 TEXT NOT NULL,
                prediction_json TEXT NOT NULL, thumbnail BLOB NOT NULL,
                UNIQUE(image_sha256, checkpoint_sha256)
            )""")
            connection.execute("CREATE INDEX IF NOT EXISTS predictions_created ON predictions(created_at DESC)")
            connection.execute("PRAGMA user_version=1")
            yield connection
            connection.commit()
        except HistoryError:
            if connection:
                connection.rollback()
            raise
        except (sqlite3.Error, OSError, json.JSONDecodeError) as exc:
            if connection:
                connection.rollback()
            raise HistoryError("Không thể truy cập lịch sử. Vui lòng kiểm tra quyền ghi và thử lại.") from exc
        finally:
            if connection:
                connection.close()

    def save(self, record: dict, thumbnail: bytes) -> tuple[str, bool]:
        prediction = record["prediction"]
        if prediction["label"] not in CLASSES or not 0 <= prediction["confidence"] <= 1:
            raise ValueError("Invalid prediction record")
        identifier = uuid4().hex
        with self._connection() as connection:
            cursor = connection.execute("""INSERT INTO predictions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(image_sha256, checkpoint_sha256) DO NOTHING""", (
                identifier, record["created_at"], record["image_name"], record["image_sha256"],
                prediction["label"], prediction["confidence"], prediction["model_version"],
                prediction["checkpoint_sha256"], json.dumps(prediction, ensure_ascii=False), thumbnail,
            ))
            if cursor.rowcount == 1:
                return identifier, True
            existing = connection.execute(
                "SELECT id FROM predictions WHERE image_sha256=? AND checkpoint_sha256=?",
                (record["image_sha256"], prediction["checkpoint_sha256"]),
            ).fetchone()
            return existing["id"], False

    @staticmethod
    def _where(search="", crop="", label="", start_date="", end_date=""):
        conditions, parameters = [], []
        if search:
            conditions.append("instr(casefold(image_name), casefold(?)) > 0")
            parameters.append(search)
        if crop:
            if crop not in {"Potato", "Tomato"}:
                raise ValueError("Invalid crop")
            conditions.append("label LIKE ?")
            parameters.append(crop + "%")
        if label:
            if label not in CLASSES:
                raise ValueError("Invalid label")
            conditions.append("label=?")
            parameters.append(label)
        for value, operator in ((start_date, ">="), (end_date, "<=")):
            if value:
                conditions.append(f"substr(created_at,1,10) {operator} ?")
                parameters.append(str(value))
        return (" WHERE " + " AND ".join(conditions) if conditions else ""), parameters

    def list(self, *, limit: int | None = 20, offset: int = 0, include_thumbnails: bool = True, **filters) -> list[dict]:
        where, parameters = self._where(**filters)
        columns = "*" if include_thumbnails else "id,created_at,image_name,image_sha256,label,confidence,model_version,checkpoint_sha256,prediction_json"
        query = "SELECT " + columns + " FROM predictions" + where + " ORDER BY created_at DESC, id DESC"
        if limit is not None:
            if limit < 1 or offset < 0:
                raise ValueError("Invalid pagination")
            query += " LIMIT ? OFFSET ?"
            parameters += [limit, offset]
        with self._connection() as connection:
            records = []
            for row in connection.execute(query, parameters):
                record = dict(row)
                record["prediction"] = json.loads(record.pop("prediction_json"))
                records.append(record)
            return records

    def count(self, **filters) -> int:
        where, parameters = self._where(**filters)
        with self._connection() as connection:
            return connection.execute("SELECT COUNT(*) FROM predictions" + where, parameters).fetchone()[0]

    def delete(self, identifier: str) -> bool:
        with self._connection() as connection:
            return connection.execute("DELETE FROM predictions WHERE id=?", (identifier,)).rowcount > 0

    def clear(self) -> int:
        with self._connection() as connection:
            return connection.execute("DELETE FROM predictions").rowcount


def export_csv(records: list[dict]) -> bytes:
    output = io.StringIO(newline="")
    fields = ["id", "created_at", "image_name", "label", "confidence", "model_version", "checkpoint_sha256", "image_sha256"]
    writer = csv.DictWriter(output, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    for record in records:
        values = {key: record[key] for key in fields}
        # Keep user filenames as text when the CSV is opened in Excel.
        if values["image_name"].lstrip().startswith(("=", "+", "-", "@")):
            values["image_name"] = "'" + values["image_name"]
        writer.writerow(values)
    return output.getvalue().encode("utf-8-sig")
