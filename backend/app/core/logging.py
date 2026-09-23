import logging
import sys
from core.config import get_settings

def setup_logging() -> logging.Logger:
    settings = get_settings()
    logger = logging.getLogger("alias")
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

def get_logger(name: str = "alias") -> logging.Logger:
    return logging.getLogger(f"alias.{name}")
