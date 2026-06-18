"""add size constraints to username and email fields of users table

Revision ID: 90778d07a7d3
Revises: c9808a759288
Create Date: 2026-06-18 13:08:12.162934

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "90778d07a7d3"
down_revision: Union[str, Sequence[str], None] = "c9808a759288"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(),
        type_=sa.String(length=50),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(),
        type_=sa.String(length=255),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=50),
        type_=sa.String(),
        existing_nullable=False,
    )

    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=255),
        type_=sa.String(),
        existing_nullable=False,
    )
