"""Use cases for vacancies."""

from collections.abc import Sequence
from http import HTTPStatus

from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.core.errors import AppError, NotFoundError
from skillmatch.modules.companies import Company, CompanyNotFoundError, CompanyRepository
from skillmatch.modules.jobs.models import Vacancy
from skillmatch.modules.jobs.repository import VacancyRepository
from skillmatch.modules.jobs.schemas import VacancyCreate, VacancyUpdate

_VACANCY_NOT_FOUND = "Recurso no encontrado."


class _VacancyValidationError(AppError):
    status_code = HTTPStatus.UNPROCESSABLE_ENTITY
    code = "validation_error"
    title = "Validation error"


class VacancyService:
    """Manages vacancies for the authenticated company user."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = VacancyRepository(session)
        self._company_repo = CompanyRepository(session)

    async def _require_company(self, user_id: int) -> Company:
        """Return company for user or raise."""
        company = await self._company_repo.get_by_user_id(user_id)
        if company is None:
            raise CompanyNotFoundError
        return company

    async def list_mine(self, user_id: int) -> Sequence[Vacancy]:
        """List vacancies for user's company."""
        company = await self._require_company(user_id)
        return await self._repo.list_by_company(company.id)

    async def create(self, user_id: int, data: VacancyCreate) -> Vacancy:
        """Create vacancy for user's company."""
        company = await self._require_company(user_id)
        vacancy = Vacancy(
            company_id=company.id,
            title=data.title,
            description=data.description,
            seniority=data.seniority.value,
            location=data.location,
            work_mode=data.work_mode.value,
            contract_type=data.contract_type.value,
            salary_min=data.salary_min,
            salary_max=data.salary_max,
            salary_currency=data.salary_currency,
            essential_skills=list(data.essential_skills),
            desirable_skills=list(data.desirable_skills),
            status=data.status.value,
        )
        self._repo.add(vacancy)
        await self._session.commit()
        await self._session.refresh(vacancy)
        return vacancy

    async def get_owner_user_id(self, vacancy_id: int) -> int:
        """Return owner user id for vacancy."""
        owner = await self._repo.get_owner_user_id(vacancy_id)
        if owner is None:
            raise NotFoundError(_VACANCY_NOT_FOUND)
        return owner

    async def get(self, vacancy_id: int, user_id: int) -> Vacancy:
        """Get owned vacancy."""
        vacancy = await self._repo.get_owned(vacancy_id, user_id)
        if vacancy is None:
            raise NotFoundError(_VACANCY_NOT_FOUND)
        return vacancy

    async def update(self, vacancy_id: int, user_id: int, data: VacancyUpdate) -> Vacancy:
        """Update owned vacancy."""
        vacancy = await self.get(vacancy_id, user_id)
        payload = data.model_dump(exclude_unset=True)

        final_min = payload.get("salary_min", vacancy.salary_min)
        final_max = payload.get("salary_max", vacancy.salary_max)
        final_currency = payload.get("salary_currency", vacancy.salary_currency)
        if final_min is not None and final_max is not None and final_min > final_max:
            raise _VacancyValidationError("salary_min must be <= salary_max")
        if (final_min is not None or final_max is not None) and final_currency is None:
            raise _VacancyValidationError("salary_currency is required when salary is provided")

        for field, value in payload.items():
            if hasattr(value, "value"):
                setattr(vacancy, field, value.value)
            else:
                setattr(vacancy, field, value)
        await self._session.commit()
        await self._session.refresh(vacancy)
        return vacancy

    async def delete(self, vacancy_id: int, user_id: int) -> None:
        """Delete owned vacancy."""
        vacancy = await self.get(vacancy_id, user_id)
        await self._repo.delete(vacancy)
        await self._session.commit()
