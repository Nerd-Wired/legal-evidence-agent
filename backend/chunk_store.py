import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKS_PATH = BASE_DIR / "data" / "chunks.json"


def save_chunks(chunks):
    CHUNKS_PATH.parent.mkdir(parents=True, exist_ok=True)
    CHUNKS_PATH.write_text(
        json.dumps(chunks, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def load_chunks():
    if not CHUNKS_PATH.exists():
        return []

    return json.loads(CHUNKS_PATH.read_text(encoding="utf-8"))