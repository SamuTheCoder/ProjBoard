from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dal.models.base import Base


class Project(Base):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint("owner_id", "project_name", name="uq_project_owner_name"),
    )

    project_id: Mapped[int] = mapped_column(primary_key=True)

    project_name: Mapped[str] = mapped_column(String(100), nullable=False)

    project_description: Mapped[str | None] = mapped_column(String(255), nullable=True)

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=True,
    )

    owner = relationship("User", back_populates="owned_projects")

    members = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    @property
    def member_count(self) -> int:
        return len(self.members)

    tasks = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )
