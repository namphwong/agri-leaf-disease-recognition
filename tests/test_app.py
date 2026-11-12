import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from streamlit.testing.v1 import AppTest

from src.config import PROJECT_ROOT
from src.storage import HistoryStore


class AppFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "ui.sqlite3"
        self.environment = patch.dict(os.environ, {"AGRI_HISTORY_PATH": str(self.path)})
        self.environment.start()
        self.addCleanup(self.environment.stop)
        sample = io.BytesIO()
        Image.new("RGB", (40, 40), (30, 120, 40)).save(sample, format="PNG")
        self.sample_patch = patch("src.ui.recognition.sample_bytes", return_value=sample.getvalue())
        self.sample_patch.start()
        self.addCleanup(self.sample_patch.stop)
        from src.ui.recognition import cached_sample
        cached_sample.clear()
        self.app = AppTest.from_file(str(PROJECT_ROOT / "app.py"), default_timeout=60)

    def assert_healthy(self):
        self.assertFalse(self.app.exception, [str(e.value) for e in self.app.exception])
        self.assertFalse(self.app.error, [e.value for e in self.app.error])

    def test_sample_analysis_save_filter_and_delete(self):
        self.app.run()
        self.assert_healthy()
        self.app.button(key="use_sample").click().run()
        self.app.button(key="analyze").click().run()
        self.assert_healthy()
        self.assertIn("analysis", self.app.session_state)
        self.app.button(key="save_result").click().run()
        self.assertEqual(HistoryStore(self.path).count(), 1)
        self.app.button(key="save_result").click().run()
        self.assertEqual(HistoryStore(self.path).count(), 1)
        self.app.radio(key="navigation").set_value("Lịch sử").run()
        self.assert_healthy()
        self.app.text_input(key="history_search").set_value("not-a-matching-file").run()
        self.assertTrue(self.app.info)
        self.app.text_input(key="history_search").set_value("").run()
        identifier = HistoryStore(self.path).list()[0]["id"]
        self.assertTrue(self.app.button(key=f"delete_{identifier}").disabled)
        self.app.checkbox(key=f"confirm_{identifier}").check().run()
        self.app.button(key=f"delete_{identifier}").click().run()
        self.assert_healthy()
        self.assertEqual(HistoryStore(self.path).count(), 0)

    def test_all_pages_render_and_evaluation_discloses_limits(self):
        self.app.run()
        for page in ("Lịch sử", "Đánh giá", "Hướng dẫn", "Nhận dạng"):
            self.app.radio(key="navigation").set_value(page).run()
            self.assert_healthy()
        self.app.radio(key="navigation").set_value("Đánh giá").run()
        self.assertTrue(any("không phải độ chính xác 100%" in e.value for e in self.app.info))

    def test_corrupt_upload_does_not_create_prediction(self):
        with patch("streamlit.file_uploader", return_value=io.BytesIO(b"bad image")):
            self.app.run()
        self.assertFalse(self.app.exception)
        self.assertTrue(any("Không thể đọc ảnh" in e.value for e in self.app.error))
        self.assertNotIn("analysis", self.app.session_state)
        self.assertFalse(self.path.exists())

    def test_storage_failure_keeps_prediction_visible(self):
        self.app.run()
        self.app.button(key="use_sample").click().run()
        self.app.button(key="analyze").click().run()
        self.path.write_bytes(b"broken database")
        with self.assertLogs("src.ui.recognition", level="ERROR"):
            self.app.button(key="save_result").click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.error)
        self.assertIn("analysis", self.app.session_state)

    def test_new_upload_invalidates_previous_prediction(self):
        self.app.run()
        self.app.button(key="use_sample").click().run()
        self.app.button(key="analyze").click().run()
        self.assertIn("analysis", self.app.session_state)
        payload = io.BytesIO()
        Image.new("RGB", (20, 20), "red").save(payload, format="PNG")
        payload.seek(0)
        with patch("streamlit.file_uploader", return_value=payload):
            self.app.run()
        self.assert_healthy()
        self.assertNotIn("analysis", self.app.session_state)
        self.assertFalse(any(button.key == "save_result" for button in self.app.button))

    def test_clear_history_requires_confirmation(self):
        self.app.run()
        self.app.button(key="use_sample").click().run()
        self.app.button(key="analyze").click().run()
        self.app.button(key="save_result").click().run()
        self.app.radio(key="navigation").set_value("Lịch sử").run()
        self.assertTrue(self.app.button(key="clear_history").disabled)
        self.app.checkbox(key="confirm_clear").check().run()
        self.app.button(key="clear_history").click().run()
        self.assert_healthy()
        self.assertEqual(HistoryStore(self.path).count(), 0)

    def test_missing_model_does_not_break_navigation(self):
        self.app.run()
        self.app.button(key="use_sample").click().run()
        with patch("src.ui.recognition.DEFAULT_MODEL_PATH", Path(self.temp.name) / "missing.pth"), \
             self.assertLogs("src.ui.recognition", level="ERROR"):
            self.app.button(key="analyze").click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.error)
        self.assertNotIn("analysis", self.app.session_state)
        self.app.radio(key="navigation").set_value("Hướng dẫn").run()
        self.assert_healthy()


if __name__ == "__main__":
    unittest.main()
