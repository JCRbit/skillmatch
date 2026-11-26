"""add companies and vacancies.

Revision ID: c3d4e5f6a7b8
Revises: 174019ed5756
Create Date: 2026-11-26 14:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "c3d4e5f6a7b8"
down_revision: str | Sequence[str] | None = "174019ed5756"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create companies and vacancies tables."""
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_user_id"), "companies", ["user_id"], unique=True)

    op.create_table(
        "vacancies",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("seniority", sa.String(length=20), nullable=False),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("work_mode", sa.String(length=20), nullable=False),
        sa.Column("contract_type", sa.String(length=20), nullable=False),
        sa.Column("salary_min", sa.Integer(), nullable=True),
        sa.Column("salary_max", sa.Integer(), nullable=True),
        sa.Column("salary_currency", sa.String(length=3), nullable=True),
        sa.Column("essential_skills", sa.JSON(), nullable=False),
        sa.Column("desirable_skills", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_vacancies_company_id"), "vacancies", ["company_id"], unique=False)


def downgrade() -> None:
    """Drop companies and vacancies tables."""
    op.drop_index(op.f("ix_vacancies_company_id"), table_name="vacancies")
    op.drop_table("vacancies")
    op.drop_index(op.f("ix_companies_user_id"), table_name="companies")
    op.drop_table("companies")
