from http import HTTPStatus

import pytest

from skillmatch.core.errors import (
    AppError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)


def test_detail_defaults_to_the_title() -> None:
    error = NotFoundError()

    assert error.detail == "Resource not found"
    assert str(error) == "Resource not found"


def test_detail_can_be_customised() -> None:
    assert NotFoundError("Candidate does not exist.").detail == "Candidate does not exist."


@pytest.mark.parametrize(
    ("error_class", "status", "code"),
    [
        (AppError, HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error"),
        (AuthenticationError, HTTPStatus.UNAUTHORIZED, "authentication_required"),
        (PermissionDeniedError, HTTPStatus.FORBIDDEN, "permission_denied"),
        (NotFoundError, HTTPStatus.NOT_FOUND, "not_found"),
        (ConflictError, HTTPStatus.CONFLICT, "conflict"),
    ],
)
def test_each_error_maps_to_a_stable_status_and_code(
    error_class: type[AppError], status: HTTPStatus, code: str
) -> None:
    assert error_class.status_code is status
    assert error_class.code == code
