"""add candidate projects.

Revision ID: a1b2c3d4e5f6
Revises: 174019ed5756
Create Date: 2026-11-26 12:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "174019ed5756"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "candidate_projects",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=120), nullable=False),
        sa.Column("stack", sa.JSON(), nullable=False),
        sa.Column("source_type", sa.String(length=20), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("project_date", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_candidate_projects_candidate_id"),
        "candidate_projects",
        ["candidate_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_candidate_projects_candidate_id"), table_name="candidate_projects")
    op.drop_table("candidate_projects")
