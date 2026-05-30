"""Structured logging for QC System"""
import logging
import json
import sys
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON log formatter"""

    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        if hasattr(record, "extra_data"):
            log_data["data"] = record.extra_data

        return json.dumps(log_data, ensure_ascii=False)


def setup_logger(name="qc", level=logging.INFO):
    """Setup structured logger"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Console handler
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    ))
    logger.addHandler(console)

    # File handler (JSON)
    try:
        file_handler = logging.FileHandler("logs/qc.log", encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)
    except FileNotFoundError:
        import os
        os.makedirs("logs", exist_ok=True)
        file_handler = logging.FileHandler("logs/qc.log", encoding="utf-8")
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


# Pre-configured loggers
logger = setup_logger("qc")
api_logger = setup_logger("qc.api")
cv_logger = setup_logger("qc.cv")
db_logger = setup_logger("qc.db")
