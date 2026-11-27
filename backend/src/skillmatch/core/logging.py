"""Structured JSON logging with request correlation.

Every log line is a JSON object, so log collectors can index it without a regex. The
``request_id`` of the current request is added automatically, which lets one trace through every
line a request produced, including the ones written by other modules.

Personal data must never reach the logs: callers pass identifiers and outcomes, not payloads.
This module enforces that rule instead of trusting it, because a single careless call is enough
to leak a candidate's data into a log collector that keeps it forever (FR-012, NFR-006):

- ``extra`` fields whose name is in :data:`SENSITIVE_KEYS` are replaced, at any depth.
- The message is written **without interpolating its arguments**, so
  ``logger.info("email: %s", email)`` never puts the address in the line.
- An exception contributes only its type. Its message and traceback are dropped, because both
  can carry the personal data that caused it.

The redaction happens on the record itself (:class:`RedactingFilter`), not only in the JSON
formatter: a record can reach more than one handler, and a plain-text handler would happily print
the traceback the JSON one drops. Sanitising the record first makes every handler safe.
"""

import json
import logging
import sys
from collections.abc import Mapping, Sequence
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Final

REDACTED_PLACEHOLDER: Final = "[redacted]"
"""What replaces a sensitive value in a log line."""

SENSITIVE_KEYS: Final[frozenset[str]] = frozenset(
    {
        "display_name",
        "summary",
        "city",
        "languages",
        "skills",
        "email",
        "phone",
        "password",
        "password_hash",
        "token",
        "access_token",
        "authorization",
        "cookie",
        "candidate",
        "profile",
        "projection",
    }
)
"""Field names that must never reach a log line, even when a caller passes them by mistake.

This is the log half of the non-leakage requirement (FR-012, B-06): logs carry identifiers and
outcomes, never personal data, but a redaction list makes the rule enforced instead of agreed.
``projection`` covers the whole pseudonymised payload, which must be logged as a count or an id.
"""

UNLOGGED_MESSAGE: Final = "<message withheld>"
"""What replaces a message that interpolated arguments.

Only the template is kept, so a message built from personal data cannot reach the line. A caller
that wants the value visible must log it as an identifier through ``extra``.
"""

REQUEST_ID_HEADER: Final = "X-Request-ID"
"""Header used to receive and return the correlation id of a request."""

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
"""Correlation id of the request being handled in the current context."""

MAX_REDACTION_DEPTH: Final = 5
"""How deep redaction walks before replacing the whole structure."""

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


def _redact(value: object, *, depth: int = 0) -> object:
    """Redact a value, descending into mappings and sequences.

    Args:
        value: The value attached to a record.
        depth: Current nesting level, used to stop on a self-referencing structure.

    Returns:
        The value with every sensitive key replaced, or a short placeholder for a structure too
        deep to walk.

    Nested structures are covered because ``extra={"candidate": {"email": ...}}`` is a leak too:
    redacting only the top-level key would leave the address one level down.
    """
    if depth > MAX_REDACTION_DEPTH:
        return REDACTED_PLACEHOLDER

    if isinstance(value, Mapping):
        return {
            str(key): (
                REDACTED_PLACEHOLDER
                if str(key) in SENSITIVE_KEYS
                else _redact(item, depth=depth + 1)
            )
            for key, item in value.items()
        }

    if isinstance(value, str | bytes):
        return value

    if isinstance(value, Sequence | set | frozenset):
        return [_redact(item, depth=depth + 1) for item in value]

    return value


def _exception_type(record: logging.LogRecord) -> str | None:
    """Return the exception's type, and nothing of its message or traceback.

    Args:
        record: The log record, possibly carrying an exception.

    Returns:
        The exception's class name, or ``None`` when the record carries no exception.
    """
    if not record.exc_info:
        return None

    exception_type = record.exc_info[0]
    return exception_type.__name__ if exception_type else None


class RedactingFilter(logging.Filter):
    """Sanitise a record in place, so every handler receives it already clean.

    A formatter only protects the handler it belongs to. The same record can be printed by a
    plain-text handler, collected by a test fixture or forwarded by a library, so the personal
    data has to be gone before it leaves the caller. This filter is installed on the
    ``skillmatch`` logger and does exactly that.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Strip personal data from ``record`` and keep it.

        Args:
            record: The record about to be handled.

        Returns:
            Always ``True``: the record is kept, only its contents change.
        """
        # An interpolated message would carry its arguments once formatted: keep the template.
        if record.args:
            record.msg = UNLOGGED_MESSAGE
            record.args = ()

        # The traceback and the exception's message can carry the data that caused it.
        exception_type = _exception_type(record)
        record.exc_info = None
        record.exc_text = None
        if exception_type:
            record.exception_type = exception_type

        for key, value in list(record.__dict__.items()):
            if key in _RESERVED_ATTRIBUTES or key.startswith("_"):
                continue
            if key in SENSITIVE_KEYS:
                setattr(record, key, REDACTED_PLACEHOLDER)
            else:
                setattr(record, key, _redact(value))

        return True


class JsonFormatter(logging.Formatter):
    """Render every record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        """Build the JSON line for ``record``.

        Args:
            record: The log record to serialise.

        Returns:
            A JSON object with the timestamp, level, logger, message, request id, any extra
            fields the caller attached, and the exception's type when there is one.

        The record is expected to have passed through :class:`RedactingFilter`; the checks here
        are a second line of defence, not the only one.
        """
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": str(record.msg) if not record.args else UNLOGGED_MESSAGE,
        }

        request_id = getattr(record, "request_id", None) or request_id_var.get()
        if request_id:
            payload["request_id"] = request_id

        payload.update(
            {
                key: (REDACTED_PLACEHOLDER if key in SENSITIVE_KEYS else _redact(value))
                for key, value in record.__dict__.items()
                if key not in _RESERVED_ATTRIBUTES and not key.startswith("_")
            }
        )

        exception_type = _exception_type(record) or getattr(record, "exception_type", None)
        if exception_type:
            payload["exception"] = exception_type

        return json.dumps(payload, ensure_ascii=False, default=str)


def configure_logging(level: str = "INFO") -> None:
    """Install the redacting filter and the JSON formatter on the application's logger.

    Args:
        level: Minimum level to emit, as a name (``DEBUG``, ``INFO``...).

    The root logger keeps its handlers untouched: this only reconfigures the ``skillmatch``
    logger, so uvicorn's own output is unaffected. Records still propagate, so a caller's own
    handler (``caplog`` in tests, a collector in production) sees them already sanitised.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    logger = logging.getLogger("skillmatch")
    logger.handlers.clear()
    logger.addHandler(handler)
    logger.addFilter(RedactingFilter())

    # Fall back to INFO when the configured level is unknown.
    normalized_level = level.strip().upper()
    resolved_level = logging.getLevelNamesMapping().get(normalized_level, logging.INFO)
    logger.setLevel(resolved_level)

    logger.propagate = True
