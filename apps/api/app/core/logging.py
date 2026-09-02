"""Structured application logging sent to standard output."""

import json
import logging
import logging.config
from datetime import UTC, datetime
from typing import Any, override

from app.core.request_context import current_request_id

_STANDARD_LOG_RECORD_FIELDS = frozenset(logging.makeLogRecord({}).__dict__)


class JsonFormatter(logging.Formatter):
    """Render application log records as one JSON object per line."""

    @override
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        request_id = current_request_id.get()
        if request_id is not None:
            payload["request_id"] = request_id

        for key, value in record.__dict__.items():
            if key not in _STANDARD_LOG_RECORD_FIELDS and key not in payload:
                payload[key] = value

        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, separators=(",", ":"))


def configure_logging(log_level: str) -> None:
    """Configure the process root logger with a structured stdout handler."""
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {"json": {"()": JsonFormatter}},
            "handlers": {
                "stdout": {
                    "class": "logging.StreamHandler",
                    "formatter": "json",
                    "level": log_level,
                    "stream": "ext://sys.stdout",
                }
            },
            "root": {"handlers": ["stdout"], "level": log_level},
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a standard logger configured by the composition root."""
    return logging.getLogger(name)
