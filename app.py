import base64
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from flask import Flask, jsonify, request
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent

FIELDS = [
    "name", "next", "ids", "nama", "bio", "jenis_kelamin", "golongan_darah",
    "skil", "html", "css", "js", "website", "status", "pekerjaan",
    "kewarganegaraan", "masa_berlaku", "kota", "terbuat",
]
MAX_PHOTO_BYTES = 3 * 1024 * 1024


def build_card(payload):
    data = {}
    for key in FIELDS:
        value = str(payload.get(key, "")).strip()
        if not value:
            raise ValueError(f"Field '{key}' wajib diisi")
        data[key] = value

    photo_b64 = payload.get("photo", "")
    if "," in photo_b64:
        photo_b64 = photo_b64.split(",", 1)[1]
    if not photo_b64:
        raise ValueError("Foto wajib diupload")
    raw = base64.b64decode(photo_b64)
    if len(raw) > MAX_PHOTO_BYTES:
        raise ValueError("Ukuran foto terlalu besar (maks 3 MB)")
    try:
        photo = Image.open(io.BytesIO(raw))
        photo = ImageOps.exif_transpose(photo).convert("RGB")
    except Exception:
        raise ValueError("File foto tidak valid")
    # Normalisasi ke 432x450 supaya sesuai logika paste di create.py
    photo = ImageOps.fit(photo, (432, 450), Image.LANCZOS, centering=(0.5, 0.3))

    work = Path(tempfile.mkdtemp(prefix="card_"))
    try:
        (work / "src").mkdir()
        shutil.copytree(ROOT / "font", work / "font")
        shutil.copy(ROOT / "src" / "Template.png", work / "src" / "Template.png")
        shutil.copy(ROOT / "create.py", work / "create.py")
        photo.save(work / "src" / "photo.jpg", quality=95)
        data["pas_photo"] = "src/photo.jpg"
        with open(work / "data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

        proc = subprocess.run(
            [sys.executable, "create.py"],
            cwd=work, capture_output=True, text=True, timeout=30,
        )
        result = work / "src" / "result.png"
        if proc.returncode != 0 or not result.exists():
            raise RuntimeError(proc.stderr.strip() or "Gagal membuat kartu")
        return result.read_bytes()
    finally:
        shutil.rmtree(work, ignore_errors=True)



app = Flask(__name__)


@app.post("/api/generate")
def generate():
    try:
        payload = request.get_json(force=True, silent=True) or {}
        png = build_card(payload)
        return jsonify(image="data:image/png;base64," + base64.b64encode(png).decode())
    except ValueError as e:
        return jsonify(error=str(e)), 400
    except Exception as e:
        return jsonify(error=f"Server error: {e}"), 500


@app.get("/api/generate")
def health():
    return jsonify(status="ok")
