"""Ideas and votes, with one vote per user per idea enforced in the stored data.

The file name follows the work item; the chain continues from revision 0003.

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "ideas",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(120), nullable=False),
        sa.Column("description", sa.String(500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_ideas_user_id", "ideas", ["user_id"])
    op.create_table(
        "votes",
        sa.Column("id", sa.String(36), primary_key=True, nullable=False),
        sa.Column(
            "user_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "idea_id",
            sa.String(36),
            sa.ForeignKey("ideas.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("user_id", "idea_id", name="uq_votes_user_id_idea_id"),
    )
    op.create_index("ix_votes_user_id", "votes", ["user_id"])
    op.create_index("ix_votes_idea_id", "votes", ["idea_id"])


def downgrade() -> None:
    op.drop_index("ix_votes_idea_id", table_name="votes")
    op.drop_index("ix_votes_user_id", table_name="votes")
    op.drop_table("votes")
    op.drop_index("ix_ideas_user_id", table_name="ideas")
    op.drop_table("ideas")
