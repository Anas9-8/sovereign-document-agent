import os
from pathlib import Path

from src.logger import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".csv"}


def validate_file(file_path):
    path = Path(file_path)

    if not path.exists():
        return False, f"File not found: {file_path}"

    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported extension: {ext}. Allowed: {ALLOWED_EXTENSIONS}"

    max_mb = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File too large: {size_mb:.1f}MB exceeds {max_mb}MB limit"

    if path.stat().st_size == 0:
        return False, "File is empty"

    logger.info("Validated: %s (%.1f KB, %s)", path.name, size_mb * 1024, ext)
    return True, ""
