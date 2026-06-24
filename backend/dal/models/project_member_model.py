import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from dal.models.base import Base


class ProjectRole(str, enum.Enum):
    owner = "owner"
    member = "member"


class ProjectMember(Base):
    __tablename__ = "project_members"

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.project_id", ondelete="CASCADE"),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"),
        primary_key=True,
    )

    role: Mapped[ProjectRole] = mapped_column(
        Enum(ProjectRole, name="project_role"),
        nullable=False,
        default=ProjectRole.member,
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    project = relationship("Project", back_populates="members")

    user = relationship("User", back_populates="project_memberships")
