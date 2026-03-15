import os
import logging
from pathlib import Path

LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"
FMT = "%(asctime)s | %(levelname)s | %(message)s"
DATE_FMT = "%Y-%m-%d %H:%M:%S"


def get_logger(name):
    LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    formatter = logging.Formatter(FMT, datefmt=DATE_FMT)

    for handler in [logging.StreamHandler(), logging.FileHandler(LOG_FILE)]:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
