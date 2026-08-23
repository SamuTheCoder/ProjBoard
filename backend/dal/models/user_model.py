from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import String, DateTime, func
import uuid

from dal.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)

    owned_projects = relationship(
        "Project",
        back_populates="owner",
        passive_deletes=True,  # passive_deletes -> let the database handle deletion of owned projects
    )

    project_memberships = relationship(
        "ProjectMember",
        back_populates="user",
        passive_deletes=True,
    )

    created_tasks = relationship(
        "Task",
        foreign_keys="Task.created_by",
        back_populates="creator",
    )

    assigned_tasks = relationship(
        "Task",
        foreign_keys="Task.assignee_id",
        back_populates="assignee",
    )

    review_tasks = relationship(
        "Task",
        foreign_keys="Task.reviewer_id",
        back_populates="reviewer",
    )
