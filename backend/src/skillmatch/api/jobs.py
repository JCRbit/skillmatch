"""Vacancy endpoints for company users."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from skillmatch.api.deps import SessionDep, require_roles, verify_resource_ownership
from skillmatch.api.problems import problem_responses
from skillmatch.modules.identity.models import User, UserRole
from skillmatch.modules.jobs.schemas import VacancyCreate, VacancyRead, VacancyUpdate
from skillmatch.modules.jobs.service import VacancyService

router = APIRouter(prefix="/jobs", tags=["jobs"])
CompanyUserDep = Annotated[User, Depends(require_roles(UserRole.EMPRESA))]
_MAX_DB_INTEGER = 2_147_483_647
VacancyIdPath = Annotated[int, Path(ge=1, le=_MAX_DB_INTEGER, description="Id of a vacancy.")]


def get_vacancy_service(session: SessionDep) -> VacancyService:
    """Build vacancy service for request."""
    return VacancyService(session)


VacancyServiceDep = Annotated[VacancyService, Depends(get_vacancy_service)]


@router.get("", summary="List my company vacancies", responses=problem_responses(401, 403, 404))
async def list_vacancies(
    current_user: CompanyUserDep, service: VacancyServiceDep
) -> list[VacancyRead]:
    """List vacancies owned by authenticated company."""
    vacancies = await service.list_mine(current_user.id)
    return [VacancyRead.from_vacancy(v) for v in vacancies]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Create a vacancy",
    responses=problem_responses(401, 403, 404, 422),
)
async def create_vacancy(
    body: VacancyCreate, current_user: CompanyUserDep, service: VacancyServiceDep
) -> VacancyRead:
    """Create a vacancy for authenticated company."""
    vacancy = await service.create(current_user.id, body)
    return VacancyRead.from_vacancy(vacancy)


@router.get(
    "/{vacancy_id}",
    summary="Read one of my vacancies",
    responses=problem_responses(401, 403, 404),
)
async def read_vacancy(
    vacancy_id: VacancyIdPath, current_user: CompanyUserDep, service: VacancyServiceDep
) -> VacancyRead:
    """Read an owned vacancy."""
    owner_id = await service.get_owner_user_id(vacancy_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    vacancy = await service.get(vacancy_id, current_user.id)
    return VacancyRead.from_vacancy(vacancy)


@router.patch(
    "/{vacancy_id}",
    summary="Update one of my vacancies",
    responses=problem_responses(401, 403, 404, 422),
)
async def update_vacancy(
    vacancy_id: VacancyIdPath,
    body: VacancyUpdate,
    current_user: CompanyUserDep,
    service: VacancyServiceDep,
) -> VacancyRead:
    """Update an owned vacancy."""
    owner_id = await service.get_owner_user_id(vacancy_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    vacancy = await service.update(vacancy_id, current_user.id, body)
    return VacancyRead.from_vacancy(vacancy)


@router.delete(
    "/{vacancy_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete one of my vacancies",
    responses=problem_responses(401, 403, 404),
)
async def delete_vacancy(
    vacancy_id: VacancyIdPath, current_user: CompanyUserDep, service: VacancyServiceDep
) -> None:
    """Delete an owned vacancy."""
    owner_id = await service.get_owner_user_id(vacancy_id)
    verify_resource_ownership(owner_id, current_user, hide_if_unauthorized=True)
    await service.delete(vacancy_id, current_user.id)
