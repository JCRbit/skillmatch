"""Use cases for company profiles."""

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from skillmatch.modules.companies.errors import CompanyAlreadyExistsError, CompanyNotFoundError
from skillmatch.modules.companies.models import Company
from skillmatch.modules.companies.repository import CompanyRepository
from skillmatch.modules.companies.schemas import CompanyCreate, CompanyUpdate


class CompanyService:
    """Manages the authenticated EMPRESA user's company profile."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = CompanyRepository(session)

    async def create(self, user_id: int, data: CompanyCreate) -> Company:
        """Create company profile."""
        if await self._repo.get_by_user_id(user_id) is not None:
            raise CompanyAlreadyExistsError
        company = Company(
            user_id=user_id,
            name=data.name,
            description=data.description,
            website=data.website,
            location=data.location,
        )
        self._repo.add(company)
        try:
            await self._session.commit()
        except IntegrityError as exc:
            await self._session.rollback()
            raise CompanyAlreadyExistsError from exc
        await self._session.refresh(company)
        return company

    async def get_mine(self, user_id: int) -> Company:
        """Get my company."""
        company = await self._repo.get_by_user_id(user_id)
        if company is None:
            raise CompanyNotFoundError
        return company

    async def update_mine(self, user_id: int, data: CompanyUpdate) -> Company:
        """Update my company."""
        company = await self.get_mine(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)
        await self._session.commit()
        await self._session.refresh(company)
        return company

    async def delete_mine(self, user_id: int) -> None:
        """Delete my company."""
        company = await self.get_mine(user_id)
        await self._repo.delete(company)
        await self._session.commit()
