"""Identity module models for user management."""

import enum
from datetime import UTC, datetime
from typing import Final

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from skillmatch.core.database import Base

ACTIVE_ACCOUNT_STATUS: Final = "active"
"""Status of an account that may authenticate. Any other value (``suspended``, ``disabled``…) is
rejected at login and on every authenticated request."""


class UserRole(enum.StrEnum):
    """Possible roles a user can have in the platform."""

    TALENTO = "talento"
    EMPRESA = "empresa"
    ADMIN = "admin"


class User(Base):
    """Identity record: who the user is, separated from talent/company profile data."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)

    # Nullable: an external identity provider may own the credentials instead.
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)

    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    status: Mapped[str] = mapped_column(String, default=ACTIVE_ACCOUNT_STATUS, nullable=False)

    # timezone=True makes the column store timezone-aware timestamps.
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
