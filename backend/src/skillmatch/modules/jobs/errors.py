"""Domain errors for the jobs module."""

from skillmatch.core.errors import NotFoundError


class VacancyNotFoundError(NotFoundError):
    """The vacancy does not exist or is not accessible."""

    code = "not_found"
    title = "Not found"
