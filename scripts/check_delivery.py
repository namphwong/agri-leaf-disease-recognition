"""Offline integrity/coherence gate for Phase 7; Python standard library only."""
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    receipt = json.loads((ROOT / "reports/delivery/phase7.json").read_text(encoding="utf-8"))
    assert receipt["independent_test"] is False
    for source in [receipt["evaluation_source"], receipt["dataset_source"]]:
        assert sha(ROOT / source["path"]) == source["sha256"], source["path"]
    for file in receipt["files"]:
        path = (ROOT / file["path"]).resolve()
        assert path.is_relative_to(ROOT / "deliverables/phase7")
        assert path.stat().st_size == file["bytes"] and sha(path) == file["sha256"], file["path"]
    assert len(receipt["files"]) == 5
    evaluation = json.loads((ROOT / receipt["evaluation_source"]["path"]).read_text(encoding="utf-8"))
    assert receipt["checkpoint_sha256"] == evaluation["checkpoint_sha256"]
    assert receipt["manifest_sha256"] == evaluation["manifest_sha256"]
    assert receipt["report_pages"] == receipt["slides"] == 12
    video = receipt["video"]
    assert abs(float(video["format"]["duration"]) - 240) < .1
    stream, = video["streams"]
    assert stream["codec_type"] == "video" and stream["codec_name"] == "h264"
    assert (stream["width"], stream["height"], stream["r_frame_rate"]) == (1920, 1080, "12/1")
    with ZipFile(ROOT / "deliverables/phase7/bao-cao-agri-leaf.docx") as z:
        text = " ".join(ET.fromstring(z.read("word/document.xml")).itertext())
        assert "92,27%" in text and "91,85%" in text and "33,59 ms" in text
        assert "chưa" in text.lower() and "test độc lập" in text
        assert "smart-leaf-ai" in text and "CC BY-SA" in text
    with ZipFile(ROOT / "deliverables/phase7/slide-agri-leaf.pptx") as z:
        slides = [p for p in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", p)]
        notes = [p for p in z.namelist() if re.fullmatch(r"ppt/notesSlides/notesSlide\d+\.xml", p)]
        assert len(slides) == len(notes) == 12
        text = " ".join(" ".join(ET.fromstring(z.read(p)).itertext()) for p in slides)
        assert "92,27%" in text and "91,85%" in text and "33,59 ms" in text
        assert "chưa có test độc lập" in text
        tables = [i for i in range(1, 13) if b"<a:tbl>" in z.read(f"ppt/slides/slide{i}.xml")]
        assert tables == [4, 5, 9, 10, 11]
        # Empty image bytes can pass package checks but render blank.
        source_image = (ROOT / "docs/screenshots/phase5-desktop.jpg").read_bytes()
        assert any(z.read(p) == source_image for p in z.namelist() if p.startswith("ppt/media/")), "Screenshot not embedded"
    scenes = json.loads((ROOT / "docs/phase7/demo-scenes.json").read_text(encoding="utf-8"))
    assert len(scenes) == 12 and sum(len(s["subtitles"]) for s in scenes) == 48
    for scene in scenes:
        assert (ROOT / "docs/screenshots/phase7" / scene["image"]).is_file()
        if "evidence_path" in scene:
            assert (ROOT / scene["evidence_path"]).is_file()
    srt = (ROOT / "deliverables/phase7/demo-agri-leaf.srt").read_text(encoding="utf-8")
    assert srt.count(" --> ") == 48 and "00:04:00,000" in srt
    for scene in scenes:
        assert all(caption in srt for caption in scene["subtitles"])
    print("Phase 7 verified: 5 files, 12 report pages, 12 slides, 240-second captioned video; independent_test=False")


if __name__ == "__main__":
    main()
