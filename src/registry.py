import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)


def _registry_path():
    return Path(os.getenv("REGISTRY_PATH", "./data/registry.json"))


def _load():
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("[]")
        return []
    with open(path, "r") as f:
        return json.load(f)


def _save(entries):
    with open(_registry_path(), "w") as f:
        json.dump(entries, f, indent=2)


def is_indexed(filename):
    return any(e["filename"] == filename for e in _load())


def add_entry(filename, chunk_count):
    entries = _load()
    entries.append({
        "filename": filename,
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "chunk_count": chunk_count,
        "status": "ok",
    })
    _save(entries)
    logger.info("Registered: %s (%d chunks)", filename, chunk_count)


def get_all():
    return _load()


def count():
    return len(_load())
