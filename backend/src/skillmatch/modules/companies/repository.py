"""Persistence for companies."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.modules.companies.models import Company


class CompanyRepository:
    """Queries and staged changes for company profiles."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: int) -> Company | None:
        """Return company by user id."""
        result = await self._session.execute(select(Company).where(Company.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_id(self, company_id: int) -> Company | None:
        """Return company by id."""
        result = await self._session.execute(select(Company).where(Company.id == company_id))
        return result.scalar_one_or_none()

    def add(self, company: Company) -> None:
        """Stage company."""
        self._session.add(company)

    async def delete(self, company: Company) -> None:
        """Delete company."""
        await self._session.delete(company)
