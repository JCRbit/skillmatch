"""Tests for request correlation, readiness, version and JSON logs (task P-05, NFR-004)."""

import json
import logging
import sys
from collections.abc import AsyncIterator, Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch import __version__
from skillmatch.api.deps import get_db_session
from skillmatch.app import create_app
from skillmatch.core.config import Environment, Settings
from skillmatch.core.logging import JsonFormatter, configure_logging, request_id_var

REQUEST_ID = "X-Request-ID"


@pytest.fixture
def settings() -> Settings:
    """Settings with a known build identity."""
    return Settings(environment=Environment.TEST, app_name="SkillMatch API", git_sha="abc1234")


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    """Client for an application whose database session works."""
    app = create_app(settings)

    async def _working_session() -> AsyncIterator[AsyncSession]:
        class _Session:
            async def execute(self, *_args: object, **_kwargs: object) -> None:
                return None

        yield _Session()  # type: ignore[misc]

    app.dependency_overrides[get_db_session] = _working_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


@pytest.fixture
def failing_client(settings: Settings) -> Iterator[TestClient]:
    """Client for an application whose database is unreachable."""
    app = create_app(settings)

    async def _failing_session() -> AsyncIterator[AsyncSession]:
        class _Session:
            async def execute(self, *_args: object, **_kwargs: object) -> None:
                raise OperationalError("SELECT 1", {}, Exception("connection refused"))

        yield _Session()  # type: ignore[misc]

    app.dependency_overrides[get_db_session] = _failing_session
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client


# --------------------------------------------------------------------------- #
# /version
# --------------------------------------------------------------------------- #
def test_version_reports_the_running_build(client: TestClient) -> None:
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {
        "name": "SkillMatch API",
        "version": __version__,
        "environment": "test",
        "git_sha": "abc1234",
    }


def test_version_defaults_to_unknown_without_build_metadata() -> None:
    app = create_app(Settings(environment=Environment.TEST))

    with TestClient(app) as test_client:
        assert test_client.get("/version").json()["git_sha"] == "unknown"


# --------------------------------------------------------------------------- #
# /ready
# --------------------------------------------------------------------------- #
def test_ready_returns_200_when_the_database_answers(client: TestClient) -> None:
    response = client.get("/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "checks": {"database": {"status": "ok"}}}


def test_ready_returns_503_when_the_database_is_down(failing_client: TestClient) -> None:
    response = failing_client.get("/ready")

    assert response.status_code == 503
    assert response.json() == {
        "status": "unavailable",
        "checks": {"database": {"status": "unavailable"}},
    }


def test_health_stays_a_liveness_probe_without_dependencies(failing_client: TestClient) -> None:
    # A failing database must not restart the process: /health keeps answering ok.
    response = failing_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


# --------------------------------------------------------------------------- #
# Request id
# --------------------------------------------------------------------------- #
def test_request_id_is_generated_when_missing(client: TestClient) -> None:
    request_id = client.get("/health").headers[REQUEST_ID]

    assert len(request_id) == 32  # uuid4().hex
    assert request_id.isalnum()


def test_incoming_request_id_is_echoed(client: TestClient) -> None:
    response = client.get("/health", headers={REQUEST_ID: "trace-123"})

    assert response.headers[REQUEST_ID] == "trace-123"


def test_generated_request_ids_are_unique(client: TestClient) -> None:
    first = client.get("/health").headers[REQUEST_ID]
    second = client.get("/health").headers[REQUEST_ID]

    assert first != second


@pytest.mark.parametrize("supplied", ["", "   ", "x" * 200, "bad\x00id"])
def test_unusable_request_ids_are_replaced(client: TestClient, supplied: str) -> None:
    request_id = client.get("/health", headers={REQUEST_ID: supplied}).headers[REQUEST_ID]

    assert request_id != supplied
    assert len(request_id) == 32


def test_request_id_is_present_on_error_responses(client: TestClient) -> None:
    response = client.get("/does-not-exist", headers={REQUEST_ID: "trace-err"})

    assert response.status_code == 404
    assert response.headers[REQUEST_ID] == "trace-err"
    assert response.json()["code"] == "http_404"


def test_request_id_is_available_to_logs_while_handling(client: TestClient) -> None:
    token = request_id_var.set("outer-context")
    try:
        client.get("/health", headers={REQUEST_ID: "trace-log"})
        # The request runs with its own id, and the surrounding context is restored afterwards.
        assert request_id_var.get() == "outer-context"
    finally:
        request_id_var.reset(token)


def test_json_logs_include_the_request_id_of_the_request(client: TestClient) -> None:
    lines: list[str] = []
    formatter = JsonFormatter()

    class _Collect(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # Format inside the request: the request id lives in a context variable.
            lines.append(formatter.format(record))

    handler = _Collect()
    logger = logging.getLogger("skillmatch.api.observability")
    logger.addHandler(handler)
    try:
        client.get("/ready", headers={REQUEST_ID: "trace-logged"})
    finally:
        logger.removeHandler(handler)

    payloads = [json.loads(line) for line in lines]
    assert payloads, "the request produced no log lines"
    assert all(entry["request_id"] == "trace-logged" for entry in payloads)


# --------------------------------------------------------------------------- #
# JSON logging
# --------------------------------------------------------------------------- #
def _record(**extra: object) -> logging.LogRecord:
    record = logging.LogRecord(
        name="skillmatch.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="something happened",
        args=(),
        exc_info=None,
    )
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_json_formatter_emits_one_object_per_line() -> None:
    payload = json.loads(JsonFormatter().format(_record()))

    assert payload["level"] == "INFO"
    assert payload["logger"] == "skillmatch.test"
    assert payload["message"] == "something happened"
    assert payload["timestamp"].endswith("+00:00")


def test_json_formatter_includes_extra_fields_and_request_id() -> None:
    token = request_id_var.set("trace-42")
    try:
        payload = json.loads(JsonFormatter().format(_record(method="GET", status_code=200)))
    finally:
        request_id_var.reset(token)

    assert payload["request_id"] == "trace-42"
    assert payload["method"] == "GET"
    assert payload["status_code"] == 200


def test_json_formatter_does_not_leak_internal_attributes() -> None:
    payload = json.loads(JsonFormatter().format(_record()))

    assert "msg" not in payload
    assert "args" not in payload
    assert "pathname" not in payload
    assert not any(key.startswith("_") for key in payload)


def test_json_formatter_serialises_the_traceback() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.LogRecord(
            name="skillmatch.test",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="failed",
            args=(),
            exc_info=sys.exc_info(),
        )

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["exception"]


def test_configure_logging_installs_a_single_json_handler() -> None:
    configure_logging("debug")
    configure_logging("debug")  # idempotent: never duplicates handlers

    logger = logging.getLogger("skillmatch")

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1
    assert isinstance(logger.handlers[0].formatter, JsonFormatter)
    assert logger.propagate is False


def test_configure_logging_defaults_to_info_for_invalid_level() -> None:
    configure_logging("INVALID")

    logger = logging.getLogger("skillmatch")

    assert logger.level == logging.INFO
