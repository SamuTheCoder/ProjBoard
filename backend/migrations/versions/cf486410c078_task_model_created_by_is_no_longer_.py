"""task model created_by is no longer restrict. Passive deletes to owned_projects and project_memberships in user

Revision ID: cf486410c078
Revises: 14e1673f9e2d
Create Date: 2026-08-23 16:16:01.640061

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "cf486410c078"
down_revision: Union[str, Sequence[str], None] = "14e1673f9e2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("tasks_created_by_fkey", "tasks", type_="foreignkey")

    op.create_foreign_key(
        "tasks_created_by_fkey",
        "tasks",
        "users",
        ["created_by"],
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_constraint("tasks_created_by_fkey", "tasks", type_="foreignkey")

    op.create_foreign_key(
        "tasks_created_by_fkey",
        "tasks",
        "users",
        ["created_by"],
        ["user_id"],
        ondelete="RESTRICT",
    )
