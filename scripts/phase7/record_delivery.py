"""Record output fingerprints after real visual/manual review; authoring runtime only."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / "deliverables/phase7"
    epath = ROOT / "reports/evaluation/latest.json"
    dpath = ROOT / "reports/dataset/summary.json"
    evaluation = json.loads(epath.read_text(encoding="utf-8"))
    probe = subprocess.run([shutil.which("ffprobe"), "-v", "error", "-show_entries", "format=duration:stream=codec_type,codec_name,width,height,r_frame_rate", "-of", "json", str(out / "demo-agri-leaf.mp4")], check=True, capture_output=True, text=True)
    payload = {
        "schema_version": 1, "prepared_on": "2026-11-22", "timezone": "Asia/Bangkok",
        "scope": "phase7_report_slides_and_demo_no_training",
        "evaluation_source": {"path": epath.relative_to(ROOT).as_posix(), "sha256": sha(epath), "created_at": evaluation["created_at"]},
        "dataset_source": {"path": dpath.relative_to(ROOT).as_posix(), "sha256": sha(dpath)},
        "checkpoint_sha256": evaluation["checkpoint_sha256"],
        "manifest_sha256": evaluation["manifest_sha256"], "independent_test": False,
        "report_pages": len(PdfReader(out / "bao-cao-agri-leaf.pdf").pages), "slides": 12,
        "spaces_page_id": "page_c9ec92984c788191901495603ba250f3",
        "video": json.loads(probe.stdout),
        "files": [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size, "sha256": sha(p)} for p in sorted(out.iterdir()) if p.is_file() and not p.name.startswith(".")],
        "review": {
            "report": "Canonical render_docx.py with LibreOffice 26.8.3 and Poppler; all 12 pages visually inspected; title border removed and re-rendered.",
            "slides": "Spaces saved 12 editable slides. Native render crashed twice on Windows; fallback exported same slide state, hydrated screenshot from source bytes, validated package/layout/import and visually reviewed all 12 LibreOffice slide renders. No native PowerPoint execution test.",
            "video": "Captioned still-image walkthrough, 12 scenes / 48 subtitles, four minutes; no audio or simulated cursor. UI captures from real browser session; not continuous screen recording or latency measurement.",
            "ui": "Sample Potato EB -> predict 85.58% -> explicit save -> history -> CSV download -> evaluation -> guide. Separate ignored demo SQLite; downloaded CSV label/confidence/model checksum matched.",
            "tests": "39 existing offline tests passed; scripts/check_evaluation.py passed. No model or data pipeline changes."
        },
        "limitations": [
            "Report identity fields intentionally blank; school rubric/template and self-training requirements remain unconfirmed in issue #2.",
            "Inherited checkpoint training membership unknown; evaluation may overlap original training.",
            "Spaces page remains personal; GitHub readers use committed fallback PPTX.",
            "Phase 8 clean clone and release v1.0.0 not yet performed."
        ]
    }
    target = ROOT / "reports/delivery/phase7.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(target)


if __name__ == "__main__":
    main()
