# app/core/logging_config.py

import logging.config
from pathlib import Path

# مسیر پایه پروژه:
BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,

    "formatters": {
        "default": {
            "format": "%(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "file": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - "
                      "%(module)s:%(lineno)d - %(message)s",
        },
    },

    "handlers": {
        # هندلر مربوط به فایل‌ها (چرخان)
        "file": {
            "formatter": "file",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 5 * 1024 * 1024,   # 5 MB
            "backupCount": 5,
            "encoding": "utf-8",
            "level": "DEBUG",
        },

        # هندلر کنسول با Rich برای نمایش رنگی و زیبا
        "console": {
            "class": "rich.logging.RichHandler",
            "formatter": "default",
            "rich_tracebacks": True,
            "level": "INFO",
        },
    },

    "loggers": {
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "app": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}

def setup_logging():
    """اعمال تنظیمات لاگینگ برنامه"""
    logging.config.dictConfig(LOGGING_CONFIG)
