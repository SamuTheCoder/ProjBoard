"""harden task constraints and defaults

Revision ID: 14e1673f9e2d
Revises: da58a8cd1ee4
Create Date: 2026-08-18 18:37:04.749098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '14e1673f9e2d'
down_revision: Union[str, Sequence[str], None] = 'da58a8cd1ee4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Harden task constraints and defaults."""
    op.drop_constraint(
        "tasks_created_by_fkey",
        "tasks",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "tasks_created_by_fkey",
        "tasks",
        "users",
        ["created_by"],
        ["user_id"],
        ondelete="RESTRICT",
    )

    op.create_check_constraint(
        "check_task_name_not_blank",
        "tasks",
        "length(trim(task_name)) > 0",
    )
    op.create_check_constraint(
        "check_task_review_status_requires_reviewer",
        "tasks",
        "review_status IS NULL OR reviewer_id IS NOT NULL",
    )

    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=sa.text("3"),
    )
    op.alter_column(
        "tasks",
        "status",
        existing_type=sa.Enum(
            "backlog",
            "ready",
            "in_progress",
            "to_review",
            "done",
            name="task_status",
        ),
        existing_nullable=False,
        server_default=sa.text("'backlog'"),
    )


def downgrade() -> None:
    """Restore the previous task schema."""
    op.alter_column(
        "tasks",
        "status",
        existing_type=sa.Enum(
            "backlog",
            "ready",
            "in_progress",
            "to_review",
            "done",
            name="task_status",
        ),
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "tasks",
        "priority",
        existing_type=sa.Integer(),
        existing_nullable=False,
        server_default=None,
    )

    op.drop_constraint(
        "check_task_review_status_requires_reviewer",
        "tasks",
        type_="check",
    )
    op.drop_constraint(
        "check_task_name_not_blank",
        "tasks",
        type_="check",
    )

    op.drop_constraint(
        "tasks_created_by_fkey",
        "tasks",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "tasks_created_by_fkey",
        "tasks",
        "users",
        ["created_by"],
        ["user_id"],
        ondelete="CASCADE",
    )
