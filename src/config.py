"""Project paths, independent of the caller's working directory."""

from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "leaf_model_final.pth"
DEFAULT_HISTORY_PATH = PROJECT_ROOT / "storage" / "history.sqlite3"


def history_path() -> Path:
    configured = Path(os.environ.get("AGRI_HISTORY_PATH", DEFAULT_HISTORY_PATH))
    return configured if configured.is_absolute() else PROJECT_ROOT / configured
