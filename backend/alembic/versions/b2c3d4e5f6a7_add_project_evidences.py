"""add project evidence review tables.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-11-26 13:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create project evidence and audit tables."""
    op.create_table(
        "candidate_project_evidences",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("candidate_id", sa.Integer(), nullable=False),
        sa.Column("canonical_id", sa.String(length=120), nullable=False),
        sa.Column("skill_label", sa.String(length=120), nullable=False),
        sa.Column("matched_term", sa.String(length=120), nullable=False),
        sa.Column("source", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('proposed', 'confirmed', 'corrected', 'withdrawn')",
            name="ck_candidate_project_evidences_status",
        ),
        sa.ForeignKeyConstraint(["candidate_id"], ["candidate_profiles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["candidate_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "canonical_id",
            name="uq_candidate_project_evidences_project_canonical",
        ),
    )
    op.create_index(
        op.f("ix_candidate_project_evidences_candidate_id"),
        "candidate_project_evidences",
        ["candidate_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_candidate_project_evidences_project_id"),
        "candidate_project_evidences",
        ["project_id"],
        unique=False,
    )

    op.create_table(
        "candidate_project_evidence_audits",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("evidence_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("actor_user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=20), nullable=False),
        sa.Column("from_status", sa.String(length=20), nullable=False),
        sa.Column("to_status", sa.String(length=20), nullable=False),
        sa.Column("before", sa.JSON(), nullable=False),
        sa.Column("after", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["evidence_id"], ["candidate_project_evidences.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["project_id"], ["candidate_projects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_candidate_project_evidence_audits_actor_user_id"),
        "candidate_project_evidence_audits",
        ["actor_user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_candidate_project_evidence_audits_evidence_id"),
        "candidate_project_evidence_audits",
        ["evidence_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_candidate_project_evidence_audits_project_id"),
        "candidate_project_evidence_audits",
        ["project_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop project evidence and audit tables."""
    op.drop_index(
        op.f("ix_candidate_project_evidence_audits_project_id"),
        table_name="candidate_project_evidence_audits",
    )
    op.drop_index(
        op.f("ix_candidate_project_evidence_audits_evidence_id"),
        table_name="candidate_project_evidence_audits",
    )
    op.drop_index(
        op.f("ix_candidate_project_evidence_audits_actor_user_id"),
        table_name="candidate_project_evidence_audits",
    )
    op.drop_table("candidate_project_evidence_audits")
    op.drop_index(
        op.f("ix_candidate_project_evidences_project_id"),
        table_name="candidate_project_evidences",
    )
    op.drop_index(
        op.f("ix_candidate_project_evidences_candidate_id"),
        table_name="candidate_project_evidences",
    )
    op.drop_table("candidate_project_evidences")
