"""Persistence for vacancies."""

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.modules.companies import Company
from skillmatch.modules.jobs.models import Vacancy


class VacancyRepository:
    """Queries and staged changes for vacancies."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_company(self, company_id: int) -> Sequence[Vacancy]:
        """List vacancies by company."""
        result = await self._session.execute(
            select(Vacancy).where(Vacancy.company_id == company_id).order_by(Vacancy.id.desc())
        )
        return result.scalars().all()

    async def get_by_id(self, vacancy_id: int) -> Vacancy | None:
        """Get vacancy by id."""
        result = await self._session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
        return result.scalar_one_or_none()

    async def get_owned(self, vacancy_id: int, user_id: int) -> Vacancy | None:
        """Get vacancy owned by user."""
        result = await self._session.execute(
            select(Vacancy)
            .join(Company, Vacancy.company_id == Company.id)
            .where(Vacancy.id == vacancy_id, Company.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_owner_user_id(self, vacancy_id: int) -> int | None:
        """Get vacancy owner user id."""
        result = await self._session.execute(
            select(Company.user_id)
            .join(Vacancy, Vacancy.company_id == Company.id)
            .where(Vacancy.id == vacancy_id)
        )
        return result.scalar_one_or_none()

    def add(self, vacancy: Vacancy) -> None:
        """Stage vacancy."""
        self._session.add(vacancy)

    async def delete(self, vacancy: Vacancy) -> None:
        """Delete vacancy."""
        await self._session.delete(vacancy)
