"""Company profile endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from skillmatch.api.deps import SessionDep, require_roles
from skillmatch.api.problems import problem_responses
from skillmatch.modules.companies.schemas import CompanyCreate, CompanyRead, CompanyUpdate
from skillmatch.modules.companies.service import CompanyService
from skillmatch.modules.identity.models import User, UserRole

router = APIRouter(prefix="/companies", tags=["companies"])
CompanyUserDep = Annotated[User, Depends(require_roles(UserRole.EMPRESA))]


def get_company_service(session: SessionDep) -> CompanyService:
    """Build company service for request."""
    return CompanyService(session)


CompanyServiceDep = Annotated[CompanyService, Depends(get_company_service)]


@router.post(
    "/me",
    status_code=status.HTTP_201_CREATED,
    summary="Create my company profile",
    responses=problem_responses(401, 403, 409, 422),
)
async def create_company(
    body: CompanyCreate, current_user: CompanyUserDep, service: CompanyServiceDep
) -> CompanyRead:
    """Create company profile for authenticated EMPRESA user."""
    company = await service.create(current_user.id, body)
    return CompanyRead.from_company(company)


@router.get("/me", summary="Read my company profile", responses=problem_responses(401, 403, 404))
async def read_company(current_user: CompanyUserDep, service: CompanyServiceDep) -> CompanyRead:
    """Return authenticated user's company profile."""
    company = await service.get_mine(current_user.id)
    return CompanyRead.from_company(company)


@router.patch(
    "/me", summary="Update my company profile", responses=problem_responses(401, 403, 404, 422)
)
async def update_company(
    body: CompanyUpdate, current_user: CompanyUserDep, service: CompanyServiceDep
) -> CompanyRead:
    """Update authenticated user's company profile."""
    company = await service.update_mine(current_user.id, body)
    return CompanyRead.from_company(company)


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete my company profile",
    responses=problem_responses(401, 403, 404),
)
async def delete_company(current_user: CompanyUserDep, service: CompanyServiceDep) -> None:
    """Delete authenticated user's company profile."""
    await service.delete_mine(current_user.id)
