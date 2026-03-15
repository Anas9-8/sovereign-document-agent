"""Tracks which documents have been indexed."""

import json
import os
from datetime import datetime, timezone
from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)


def _registry_path():
    """Return the registry file path from env."""
    return Path(os.getenv("REGISTRY_PATH", "./data/registry.json"))


def _load():
    """Load registry from disk, creating it if missing."""
    path = _registry_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text("[]")
        return []

    with open(path, "r") as f:
        return json.load(f)


def _save(entries):
    """Write registry to disk."""
    with open(_registry_path(), "w") as f:
        json.dump(entries, f, indent=2)


def is_indexed(filename):
    """Check if a document is already in the registry."""
    entries = _load()
    return any(e["filename"] == filename for e in entries)


def add_entry(filename, chunk_count):
    """Register a newly indexed document."""
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
    """Return all registry entries."""
    return _load()


def count():
    """Return total number of indexed documents."""
    return len(_load())
