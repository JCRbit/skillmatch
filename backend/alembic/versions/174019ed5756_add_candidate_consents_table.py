"""Add the candidate_consents table (B-05, US-08, FR-019).

Revision ID: 174019ed5756
Revises: 5d1e7a3c9b24
Create Date: 2026-11-26 11:01:50.650503

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "174019ed5756"
down_revision: str | Sequence[str] | None = "5d1e7a3c9b24"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "candidate_consents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("purpose", sa.String(length=20), nullable=False),
        sa.Column("granted", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("granted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("policy_version", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "purpose IN ('discovery', 'location', 'skills')", name="ck_candidate_consents_purpose"
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "candidate_id", "purpose", name="uq_candidate_consents_candidate_id_purpose"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("candidate_consents")
