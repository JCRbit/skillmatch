"""Regression tests of log redaction (B-06, FR-012, NFR-006).

The scenarios below are the ones a reviewer reproduced by hand: a message that interpolates
personal data, and an exception whose text carries it. Both must be impossible to write into a
log line, not merely discouraged in a docstring.

Two layers are checked separately, because a leak can happen in either: the record itself
(:class:`RedactingFilter`, which protects every handler) and the JSON line
(:class:`JsonFormatter`, which protects the application's own output).
"""

import json
import logging
from types import TracebackType
from typing import cast

import pytest

from skillmatch.core.logging import (
    REDACTED_PLACEHOLDER,
    SENSITIVE_KEYS,
    UNLOGGED_MESSAGE,
    JsonFormatter,
    RedactingFilter,
)

PERSONAL_EMAIL = "ana@example.test"

ExcInfo = (
    tuple[type[BaseException], BaseException, TracebackType | None] | tuple[None, None, None] | None
)


def _record(
    msg: str,
    args: tuple[object, ...] = (),
    *,
    exc_info: ExcInfo = None,
) -> logging.LogRecord:
    """Build a log record the way a caller would."""
    return logging.LogRecord(
        name="skillmatch.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg=msg,
        args=args,
        exc_info=exc_info,
    )


def _line(record: logging.LogRecord) -> dict[str, object]:
    """Format a record and return the parsed JSON line."""
    parsed: dict[str, object] = json.loads(JsonFormatter().format(record))
    return parsed


def _items(line: dict[str, object], key: str) -> list[object]:
    """Return a list field of a parsed line, checking its type first."""
    value = line[key]
    assert isinstance(value, list)
    return value


def _extra(record: logging.LogRecord, **values: object) -> logging.LogRecord:
    """Attach extra fields the way ``logger.info(..., extra=...)`` does."""
    for key, value in values.items():
        setattr(record, key, value)
    return record


def test_a_message_never_interpolates_its_arguments() -> None:
    """``logger.info("email: %s", email)`` must not put the address in the line."""
    line = _line(_record("Candidate email: %s", (PERSONAL_EMAIL,)))

    assert PERSONAL_EMAIL not in json.dumps(line)
    assert line["message"] == UNLOGGED_MESSAGE


def test_a_plain_message_is_kept() -> None:
    """A message with no arguments is the caller's own text and is safe to keep."""
    line = _line(_record("Projection served"))

    assert line["message"] == "Projection served"


def test_an_exception_keeps_only_its_type() -> None:
    """The exception's message and traceback are dropped, the type is kept."""
    error = ValueError(f"Candidate email: {PERSONAL_EMAIL}")
    line = _line(_record("profile read failed", exc_info=(ValueError, error, None)))

    assert line["exception"] == "ValueError"
    assert PERSONAL_EMAIL not in json.dumps(line)
    assert "Traceback" not in json.dumps(line)


def test_sensitive_extra_fields_are_still_redacted() -> None:
    """The behaviour that already worked must keep working."""
    record = _extra(_record("profile read"), email=PERSONAL_EMAIL, display_name="Ana P.")

    line = _line(record)

    assert line["email"] == REDACTED_PLACEHOLDER
    assert line["display_name"] == REDACTED_PLACEHOLDER
    assert PERSONAL_EMAIL not in json.dumps(line)


def test_sensitive_fields_are_redacted_at_any_depth() -> None:
    """``extra={"candidate": {"email": ...}}`` is a leak too, one level down."""
    record = _extra(
        _record("profile read"),
        candidate={"id": 3, "email": PERSONAL_EMAIL, "skills": [{"name": "Python"}]},
        items=[{"token": "abc"}, {"city": "Madrid"}],
    )

    line = _line(record)

    assert line["candidate"] == REDACTED_PLACEHOLDER
    nested = _items(line, "items")
    assert nested[0] == {"token": REDACTED_PLACEHOLDER}
    assert nested[1] == {"city": REDACTED_PLACEHOLDER}
    assert PERSONAL_EMAIL not in json.dumps(line)


def test_a_nested_structure_without_sensitive_keys_survives() -> None:
    """Redaction must not destroy a safe structure a caller relies on."""
    record = _extra(_record("match scored"), score={"total": 0.8, "parts": [0.5, 0.3]})

    line = _line(record)

    assert line["score"] == {"total": 0.8, "parts": [0.5, 0.3]}


def test_a_string_is_never_exploded_into_characters() -> None:
    """A string is a sequence, but redaction must leave it as one value."""
    record = _extra(_record("served"), outcome="ok")

    assert _line(record)["outcome"] == "ok"


@pytest.mark.parametrize("key", sorted(SENSITIVE_KEYS))
def test_every_sensitive_key_is_redacted(key: str) -> None:
    """The list is the contract: each name in it is replaced."""
    record = _record("payload")
    setattr(record, key, PERSONAL_EMAIL)

    assert _line(record)[key] == REDACTED_PLACEHOLDER


# ------------------------------------------------------------------ the record
def test_the_filter_removes_the_exception_before_any_handler_sees_it() -> None:
    """A plain-text handler must not be able to print the traceback either."""
    error = ValueError(f"Candidate email: {PERSONAL_EMAIL}")
    record = _record("profile read failed", exc_info=(ValueError, error, None))

    assert RedactingFilter().filter(record) is True

    assert record.exc_info is None
    assert record.exc_text is None
    assert cast(str, record.__dict__.get("exception_type")) == "ValueError"
    assert PERSONAL_EMAIL not in record.getMessage()
    # What a standard ``Formatter`` would print, which is what a stray handler prints.
    assert PERSONAL_EMAIL not in logging.Formatter().format(record)


def test_the_filter_removes_the_interpolated_message() -> None:
    """The template survives, the arguments do not."""
    record = _record("Candidate email: %s", (PERSONAL_EMAIL,))

    RedactingFilter().filter(record)

    assert record.args == ()
    assert record.getMessage() == UNLOGGED_MESSAGE
    assert PERSONAL_EMAIL not in logging.Formatter().format(record)


def test_the_filter_redacts_extra_fields_in_place() -> None:
    """Every handler sees the redacted value, not only the JSON one."""
    record = _extra(
        _record("profile read"), email=PERSONAL_EMAIL, candidate={"email": PERSONAL_EMAIL}
    )

    RedactingFilter().filter(record)

    assert record.__dict__.get("email") == REDACTED_PLACEHOLDER
    assert record.__dict__.get("candidate") == REDACTED_PLACEHOLDER
    assert PERSONAL_EMAIL not in logging.Formatter().format(record)
