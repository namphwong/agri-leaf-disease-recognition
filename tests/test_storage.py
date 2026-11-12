import csv
import io
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from types import SimpleNamespace

from src.storage import HistoryError, HistoryStore, export_csv, make_history_record


def record(label="Potato___healthy", image=b"one", name="lá.png", day="2026-11-12"):
    prediction = {"label": label, "confidence": .8, "class_index": 2,
                  "probabilities": [.04, .04, .8, .04, .04, .04],
                  "top3": [{"label": label, "class_index": 2, "score": .8}],
                  "model_version": "test-v1", "checkpoint_sha256": "a" * 64, "device": "cpu"}
    result = make_history_record(SimpleNamespace(to_dict=lambda: prediction), name, image)
    result["created_at"] = day + "T10:00:00+07:00"
    return result


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "history.sqlite3"
        self.store = HistoryStore(self.path)

    def test_persists_after_reopening_and_preserves_preview(self):
        identifier, created = self.store.save(record(), b"preview")
        self.assertTrue(created)
        reopened = HistoryStore(self.path)
        self.assertEqual(reopened.count(), 1)
        self.assertEqual(reopened.list()[0]["id"], identifier)
        self.assertEqual(reopened.list()[0]["thumbnail"], b"preview")

    def test_duplicate_save_is_idempotent_but_new_model_is_new_record(self):
        item = record()
        first, _ = self.store.save(item, b"preview")
        second, created = self.store.save(item, b"preview")
        self.assertEqual(first, second)
        self.assertFalse(created)
        item["prediction"]["checkpoint_sha256"] = "b" * 64
        self.store.save(item, b"preview")
        self.assertEqual(self.store.count(), 2)

    def test_filters_dates_pagination_and_export_cover_all_matching_rows(self):
        for index in range(13):
            self.store.save(record(image=str(index).encode(), name=f"lá {index}.png"), b"p")
        self.store.save(record("Tomato___healthy", b"tomato", "khác.png", "2026-11-11"), b"p")
        self.assertEqual(self.store.count(crop="Potato"), 13)
        self.assertEqual(self.store.count(start_date="2026-11-12", end_date="2026-11-12"), 13)
        self.assertEqual(self.store.count(search="lá 12"), 1)
        self.assertEqual(self.store.count(search="LÁ 12"), 1)
        self.assertEqual(self.store.count(search="' OR 1=1 --"), 0)
        self.assertEqual(len(self.store.list(limit=10, offset=10, crop="Potato")), 3)
        data = export_csv(self.store.list(limit=None, include_thumbnails=False, crop="Potato"))
        self.assertTrue(data.startswith(b"\xef\xbb\xbf"))
        rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
        self.assertEqual(len(rows), 13)
        self.assertIn("lá", rows[0]["image_name"])
        self.assertNotIn("thumbnail", rows[0])

    def test_csv_keeps_formula_filename_as_text(self):
        self.store.save(record(name="=SUM(1,2).png"), b"p")
        self.assertIn("'=SUM", export_csv(self.store.list()).decode("utf-8-sig"))

    def test_delete_one_and_clear_do_not_leave_records(self):
        identifier, _ = self.store.save(record(), b"p")
        self.store.save(record(image=b"two"), b"p")
        self.assertTrue(self.store.delete(identifier))
        self.assertFalse(self.store.delete(identifier))
        self.assertEqual(self.store.clear(), 1)
        self.assertEqual(HistoryStore(self.path).count(), 0)

    def test_concurrent_duplicate_save_creates_one_row(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: HistoryStore(self.path).save(record(), b"p"), range(2)))
        self.assertEqual(len({item[0] for item in results}), 1)
        self.assertEqual(self.store.count(), 1)

    def test_invalid_database_and_unknown_schema_report_storage_error(self):
        self.path.write_bytes(b"not sqlite")
        with self.assertRaises(HistoryError):
            self.store.count()
        other = Path(self.temp.name) / "future.sqlite3"
        with closing(sqlite3.connect(other)) as connection:
            connection.execute("PRAGMA user_version=2")
        with self.assertRaises(HistoryError):
            HistoryStore(other).count()


if __name__ == "__main__":
    unittest.main()
