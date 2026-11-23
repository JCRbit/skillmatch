"""OpenAPI documentation of error responses.

Every error of the API is an RFC 9457 problem-details document (see
:mod:`skillmatch.core.errors`). These helpers describe that shape in the OpenAPI contract so each
route can declare the errors it may return::

    @router.post("/things", responses=problem_responses(401, 409))
"""

from typing import Any, Final

from pydantic import BaseModel, ConfigDict, Field

_DESCRIPTIONS: Final = {
    401: "Missing, invalid or expired credentials.",
    403: "The caller is authenticated but not allowed to do this.",
    404: "No such resource, or not visible to the caller.",
    409: "The request conflicts with the current state of the resource.",
    422: "The request body or parameters are invalid.",
    503: "The service cannot fulfil the request right now.",
}


class ProblemResponse(BaseModel):
    """RFC 9457 problem details, as returned for every error."""

    model_config = ConfigDict(populate_by_name=True)

    problem_type: str = Field(alias="type", description="Always `about:blank`.")
    title: str
    status: int
    detail: str
    code: str = Field(description="Stable machine-readable error code.")
    instance: str = Field(description="Path of the request that failed.")
    errors: list[dict[str, object]] | None = Field(
        default=None, description="Field-level problems of a validation error."
    )


def problem_responses(*statuses: int) -> dict[int | str, dict[str, Any]]:
    """Build the ``responses`` argument of a route for the given error statuses.

    Args:
        *statuses: HTTP status codes the route may answer with.

    Returns:
        A mapping suitable for FastAPI's ``responses=`` parameter.

    Raises:
        KeyError: If a status has no registered description.
    """
    return {
        status: {"model": ProblemResponse, "description": _DESCRIPTIONS[status]}
        for status in statuses
    }
