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

Two rules make the guarantee complete rather than partial:

- **Only approved messages are written.** A message is kept only when it is a static template in
  :data:`SAFE_MESSAGES` with no arguments. An f-string or a pre-interpolated string carries
  personal data while ``record.args`` is empty, so inspecting ``args`` is not enough: anything
  that is not on the allowlist becomes :data:`UNLOGGED_MESSAGE`.
- **Every SkillMatch logger is covered.** A filter on a parent logger is not applied to records
  emitted by a child logger, so the filter is attached to each SkillMatch logger by
  :func:`get_logger`, and :func:`configure_logging` retrofits the ones created before it ran.
  Third-party loggers are never touched.
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
"""What replaces a message that is not on the allowlist.

An f-string or a pre-interpolated string carries personal data while ``record.args`` is empty, so
the message itself has to be checked, not only its arguments. A caller that wants a value visible
must log it as an identifier through ``extra``, which is redacted by name.
"""

SAFE_MESSAGES: Final[frozenset[str]] = frozenset(
    {
        "readiness check passed",
        "readiness check failed",
        "Login refused: SKILLMATCH_AUTH_SERVICE_SECRET is not configured.",
        "Unhandled error while processing %s %s",
    }
)
"""Exact static messages approved for logging.

Messages outside this allowlist are withheld because a string without formatting arguments may
still contain personal data, for example an f-string. ``"Unhandled error while processing %s %s"``
is listed as a template: it is approved before formatting, and its arguments are always dropped.
"""

_ROOT_LOGGER_NAME: Final = "skillmatch"
"""Namespace of every application logger. Third-party loggers are never touched."""

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
    data has to be gone before it leaves the caller. This filter is attached to every SkillMatch
    logger by :func:`get_logger` and retrofitted by :func:`configure_logging`.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        """Strip personal data from ``record`` and keep it.

        Args:
            record: The record about to be handled.

        Returns:
            Always ``True``: the record is kept, only its contents change.
        """
        # A message is written only when it is an approved template. Checking ``args`` is not
        # enough: an f-string already carries the data with empty ``args``.
        if record.args or not isinstance(record.msg, str) or record.msg not in SAFE_MESSAGES:
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
            "message": (
                record.msg
                if isinstance(record.msg, str) and record.msg in SAFE_MESSAGES and not record.args
                else UNLOGGED_MESSAGE
            ),
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


def _redacting_filter() -> RedactingFilter:
    """Return the filter to attach to a logger.

    Returns:
        A new filter instance. Each logger gets its own, so removing one never disarms another.
    """
    return RedactingFilter()


def _ensure_filter(logger: logging.Logger) -> None:
    """Attach the redacting filter to ``logger`` unless it already has one.

    Args:
        logger: A SkillMatch logger.

    Only the exact type is checked: a subclass would mean a different redaction rule, which is
    precisely what this module exists to prevent.
    """
    if not any(type(existing) is RedactingFilter for existing in logger.filters):
        logger.addFilter(_redacting_filter())


def get_logger(name: str) -> logging.Logger:
    """Return a SkillMatch logger that is guaranteed to redact.

    Args:
        name: Logger name, usually ``__name__``.

    Returns:
        The named logger, with :class:`RedactingFilter` attached.

    Every application logger must come from here instead of ``logging.getLogger``: a filter on a
    parent logger does not run for records emitted by a child, so a child with its own handler
    would otherwise write unsanitised data. A name outside the ``skillmatch`` namespace is
    refused, because third-party loggers are not ours to modify.

    Raises:
        ValueError: If the logger name is outside the SkillMatch namespace.
    """
    if name != _ROOT_LOGGER_NAME and not name.startswith(f"{_ROOT_LOGGER_NAME}."):
        raise ValueError("Logger name must belong to the skillmatch namespace.")

    logger = logging.getLogger(name)
    _ensure_filter(logger)
    return logger


def configure_logging(level: str = "INFO") -> None:
    """Install the redacting filter and the JSON formatter on the application's loggers.

    Args:
        level: Minimum level to emit, as a name (``DEBUG``, ``INFO``...).

    The root logger keeps its handlers untouched: this only reconfigures the ``skillmatch``
    namespace, so uvicorn's own output is unaffected. Records still propagate, so a caller's own
    handler (``caplog`` in tests, a collector in production) sees them already sanitised.

    Existing SkillMatch loggers are protected, including child loggers with handlers attached
    directly to them. Future application loggers use :func:`get_logger` to receive the same
    protection.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger(_ROOT_LOGGER_NAME)
    root.handlers.clear()
    root.addHandler(handler)

    for name, existing_logger in list(logging.root.manager.loggerDict.items()):
        in_namespace = name == _ROOT_LOGGER_NAME or name.startswith(f"{_ROOT_LOGGER_NAME}.")
        if in_namespace and isinstance(existing_logger, logging.Logger):
            _ensure_filter(existing_logger)

    _ensure_filter(root)

    # Fall back to INFO when the configured level is unknown.
    normalized_level = level.strip().upper()
    resolved_level = logging.getLevelNamesMapping().get(normalized_level, logging.INFO)
    root.setLevel(resolved_level)

    root.propagate = True
