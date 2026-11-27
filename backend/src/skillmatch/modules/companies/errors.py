"""Domain errors for the companies module."""

from skillmatch.core.errors import ConflictError, NotFoundError


class CompanyAlreadyExistsError(ConflictError):
    """The user already has a company profile."""

    code = "company_already_exists"
    title = "Company already exists"


class CompanyNotFoundError(NotFoundError):
    """The user has no company profile."""

    code = "company_not_found"
    title = "Company not found"
