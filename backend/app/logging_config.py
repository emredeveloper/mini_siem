from __future__ import annotations

import json
import logging
import os
import socket
import sys
from copy import deepcopy
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

SERVICE_NAME = os.getenv("SERVICE_NAME", "mini-siem-backend")
APP_ENV = os.getenv("APP_ENV", "local")
DEFAULT_LOG_PATH = Path(os.getenv("APP_LOG_PATH", "logs/app.log"))


def _deep_merge(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    for key, value in extra.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value
    return base


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        document: dict[str, Any] = {
            "@timestamp": datetime.now(timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "message": record.getMessage(),
            "log": {
                "level": record.levelname.lower(),
                "logger": record.name,
            },
            "service": {
                "name": SERVICE_NAME,
                "environment": APP_ENV,
            },
            "process": {
                "pid": record.process,
            },
            "host": {
                "name": socket.gethostname(),
            },
        }

        payload = getattr(record, "payload", None)
        if isinstance(payload, dict):
            _deep_merge(document, deepcopy(payload))

        if record.exc_info:
            _deep_merge(
                document,
                {"error": {"stack_trace": self.formatException(record.exc_info)}},
            )

        return json.dumps(document, ensure_ascii=False)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("mini_siem")
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    DEFAULT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    formatter = JsonFormatter()

    file_handler = RotatingFileHandler(
        DEFAULT_LOG_PATH,
        maxBytes=5_000_000,
        backupCount=5,
        encoding="utf-8",
    )
    stream_handler = logging.StreamHandler(sys.stdout)

    for handler in (file_handler, stream_handler):
        handler.setFormatter(formatter)
        handler.setLevel(logging.INFO)
        logger.addHandler(handler)

    logging.getLogger("uvicorn.access").disabled = True
    return logger

