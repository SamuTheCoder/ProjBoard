from datetime import datetime
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dal.models.base import Base


class TaskStatus(str, Enum):
    backlog = "backlog"
    ready = "ready"
    in_progress = "in_progress"
    to_review = "to_review"
    done = "done"


class ReviewStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class Task(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "priority >= 1 AND priority <= 5", name="check_task_priority_range"
        ),
        CheckConstraint(
            "length(trim(task_name)) > 0", name="check_task_name_not_blank"
        ),
        CheckConstraint(
            "review_status IS NULL OR reviewer_id IS NOT NULL",
            name="check_task_review_status_requires_reviewer",
        ),
    )

    task_id: Mapped[int] = mapped_column(primary_key=True)

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    task_name: Mapped[str] = mapped_column(String(100), nullable=False)

    task_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    created_by: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    assignee_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reviewer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    priority: Mapped[int] = mapped_column(
        nullable=False,
        default=3,
        server_default="3",
    )

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status"),
        nullable=False,
        default=TaskStatus.backlog,
        server_default=TaskStatus.backlog.value,
    )

    review_status: Mapped[ReviewStatus | None] = mapped_column(
        SQLEnum(ReviewStatus, name="review_status"),
        nullable=True,
    )

    task_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    project = relationship("Project", back_populates="tasks")

    creator = relationship(
        "User",
        foreign_keys=[created_by],
        back_populates="created_tasks",
    )

    assignee = relationship(
        "User",
        foreign_keys=[assignee_id],
        back_populates="assigned_tasks",
    )

    reviewer = relationship(
        "User",
        foreign_keys=[reviewer_id],
        back_populates="review_tasks",
    )

    # comments = relationship(
    #    "TaskComment",
    #    back_populates="task",
    #    cascade="all, delete-orphan",
    # )


#
# history = relationship(
#    "TaskHistory",
#    back_populates="task",
#    cascade="all, delete-orphan",
# )
