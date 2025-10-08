# app/core/logging_config.py

import logging.config
import os
from pathlib import Path

# مسیر ریشه پروژه را پیدا کن (دو بار .parent می‌زنیم تا از app/core به ریشه برسیم)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs" # مسیر کامل پوشه logs

# --- اگر پوشه logs وجود ندارد، آن را بساز ---
LOGS_DIR.mkdir(parents=True, exist_ok=True)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "file": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s"
        },
    },
    "handlers": {

        "file": {
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            # --- مسیر کامل فایل لاگ را بده ---
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["file"], # به کنسول و فایل بفرست
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["file"], # به کنسول و فایل بفرست
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

def setup_logging():
    """Applies the logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
