"""Fast, offline artifact verification for CI; does not run the model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evaluation import load_evaluation

if __name__ == "__main__":
    report = load_evaluation()
    print(f'Artifacts verified: {report["metrics"]["sample_count"]} images, {report["groups"]} groups; independent_test=False')
