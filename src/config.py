"""Project paths, independent of the caller's working directory."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "leaf_model_final.pth"
DEFAULT_HISTORY_PATH = PROJECT_ROOT / "storage" / "history.sqlite3"
