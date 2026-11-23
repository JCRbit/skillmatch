"""Structured JSON logging with request correlation.

Every log line is a JSON object, so log collectors can index it without a regex. The
``request_id`` of the current request is added automatically, which lets one trace through every
line a request produced, including the ones written by other modules.

Personal data must never reach the logs: callers pass identifiers and outcomes, not payloads.
"""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any, Final

REQUEST_ID_HEADER: Final = "X-Request-ID"
"""Header used to receive and return the correlation id of a request."""

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
"""Correlation id of the request being handled in the current context."""

# Attributes every LogRecord carries; anything else was added by the caller via `extra`.
_RESERVED_ATTRIBUTES: Final = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }
)


class JsonFormatter(logging.Formatter):
    """Render every record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        """Build the JSON line for ``record``.

        Args:
            record: The log record to serialise.

        Returns:
            A JSON object with the timestamp, level, logger, message, request id and any extra
            fields the caller attached.
        """
        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id", None) or request_id_var.get()
        if request_id:
            payload["request_id"] = request_id

        payload.update(
            {
                key: value
                for key, value in record.__dict__.items()
                if key not in _RESERVED_ATTRIBUTES and not key.startswith("_")
            }
        )

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Install the JSON formatter on the application's logger.

    Args:
        level: Minimum level to emit, as a name (``DEBUG``, ``INFO``…).

    The root logger keeps its handlers untouched: this only reconfigures the ``skillmatch``
    logger, so uvicorn's own output is unaffected.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("skillmatch")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(level.upper())
    logger.propagate = False
