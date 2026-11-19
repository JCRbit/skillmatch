"""Identity module models for user management."""

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from skillmatch.core.database import Base


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
    status: Mapped[str] = mapped_column(String, default="active", nullable=False)

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
