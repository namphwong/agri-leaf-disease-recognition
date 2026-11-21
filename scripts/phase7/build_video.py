"""Compose a captioned four-minute fallback walkthrough from real UI captures.

Uses Pillow for typesetting video frames and FFmpeg for H.264 encoding.
No fabricated UI state, simulated pointer action, voice or timing claim.
"""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / ".phase7-build/video"
OUT = ROOT / "deliverables/phase7"


def wrap(draw, text, font, width):
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if draw.textlength(candidate, font=font) > width and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def stamp(seconds):
    return f"{seconds // 3600:02}:{seconds % 3600 // 60:02}:{seconds % 60:02},000"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ffmpeg", default=shutil.which("ffmpeg"))
    parser.add_argument("--font-dir", default="C:/Windows/Fonts")
    args = parser.parse_args()
    if not args.ffmpeg:
        parser.error("Pass --ffmpeg with an installed FFmpeg executable")
    BUILD.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    fonts = Path(args.font_dir)
    regular = ImageFont.truetype(str(fonts / "arial.ttf"), 34)
    small = ImageFont.truetype(str(fonts / "arial.ttf"), 25)
    title = ImageFont.truetype(str(fonts / "arialbd.ttf"), 46)
    caption = ImageFont.truetype(str(fonts / "arial.ttf"), 38)
    scenes = json.loads((ROOT / "docs/phase7/demo-scenes.json").read_text(encoding="utf-8"))
    srt, concat, index = [], [], 0
    for si, scene in enumerate(scenes):
        source = ROOT / scene["evidence_path"] if "evidence_path" in scene else ROOT / "docs/screenshots/phase7" / scene["image"]
        ui = Image.open(source).convert("RGB")
        ui.thumbnail((1280, 720))
        for text in scene["subtitles"]:
            frame = Image.new("RGB", (1920, 1080), "#F6F9F4")
            draw = ImageDraw.Draw(frame)
            draw.text((58, 30), f"AGRI LEAF  /  DEMO DỰ PHÒNG  /  {si + 1:02} / 12", font=small, fill="#276B50")
            draw.text((58, 82), scene["title"], font=title, fill="#18362E")
            frame.paste(ui, (36 + (1280 - ui.width) // 2, 163 + (720 - ui.height) // 2))
            yy = 204
            for point in scene["points"]:
                for line in wrap(draw, point, regular, 510):
                    draw.text((1360, yy), line, font=regular, fill="#18362E")
                    yy += 45
                yy += 48
            kind = "Biểu đồ từ artifact Phase 6" if "evidence_path" in scene else "Ảnh chụp ứng dụng thật"
            draw.text((1360, 675), kind, font=small, fill="#52635B")
            draw.text((1360, 714), "Có phụ đề • Không có giọng đọc", font=small, fill="#52635B")
            draw.text((1360, 753), "Ảnh lá: PlantVillage", font=small, fill="#52635B")
            draw.text((1360, 792), "CC BY-SA 3.0 theo dataset card", font=small, fill="#52635B")
            draw.rectangle((0, 900, 1920, 1041), fill="#123E32")
            lines = wrap(draw, text, caption, 1760)
            if len(lines) > 2:
                raise ValueError(f"Caption needs more than two lines: {text}")
            y = 920 if len(lines) == 2 else 942
            for line in lines:
                draw.text((70, y), line, font=caption, fill="white")
                y += 48
            draw.text((54, 1050), "github.com/namphwong/agri-leaf-disease-recognition  •  Nguồn: smart-leaf-ai và PlantVillage", font=small, fill="#52635B")
            path = BUILD / f"frame-{index:02}.png"
            frame.save(path)
            concat += [f"file '{path.as_posix()}'", "duration 5"]
            srt.append(f"{index + 1}\n{stamp(index * 5)} --> {stamp((index + 1) * 5)}\n{text}\n")
            index += 1
    assert index == 48
    concat.append(f"file '{path.as_posix()}'")
    (BUILD / "frames.txt").write_text("\n".join(concat), encoding="utf-8")
    (OUT / "demo-agri-leaf.srt").write_text("\n".join(srt), encoding="utf-8", newline="\n")
    subprocess.run([args.ffmpeg, "-y", "-hide_banner", "-loglevel", "warning", "-f", "concat", "-safe", "0", "-i", str(BUILD / "frames.txt"), "-t", "240", "-r", "12", "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(OUT / "demo-agri-leaf.mp4")], check=True)
    print(f"Built 240-second captioned walkthrough from {len(scenes)} scenes; no audio.")


if __name__ == "__main__":
    main()
