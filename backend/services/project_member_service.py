from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.schemas.project_member_schemas import ProjectMemberResponse
from dal.models.user_model import User
from dal.models.project_model import Project
from dal.models.project_member_model import ProjectRole, ProjectMember
from schemas.project_schemas import ProjectCreate, ProjectUpdate
from services.user_service import get_user_by_id


def add_user_to_project(
    db: Session, project_id: int, user_id: int, current_user_id: int
) -> ProjectMemberResponse:
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    if project.owner_id != current_user_id:
        raise PermissionError("Only the project owner can add members")

    target_user = db.execute(
        select(User).where(User.user_id == user_id)
    ).scalar_one_or_none()

    if target_user is None:
        raise ValueError("User not found")

    existing_membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    ).scalar_one_or_none()

    if existing_membership is not None:
        raise ValueError("User is already a member of this project")

    new_membership = ProjectMember(
        project_id=project_id, user_id=user_id, role=ProjectRole.member
    )

    db.add(new_membership)
    db.commit()
    db.refresh(new_membership)

    return new_membership


def get_project_members(db: Session, project_id: int, current_user_id: int):
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    current_user_membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user_id,
        )
    ).scalar_one_or_none()

    if current_user_membership is None:
        raise PermissionError("Current user does not belong to this project")

    return (
        db.execute(
            select(ProjectMember).where(
                ProjectMember.project_id == project_id,
            )
        )
        .scalar()
        .all()
    )


def update_member_role(
    db: Session, project_id: int, member_id: int, current_user_id: int
) -> ProjectMember:
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    if project.owner_id != current_user_id:
        raise ValueError("Only the project owner can update member's role")

    changing_membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == member_id
        )
    ).scalar_one_or_none()

    if changing_membership is None:
        raise ValueError("Member to change doesn't exist in the project")

    changing_membership.role = ProjectRole.owner
    project.owner = changing_membership.user_id

    old_owner_membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user_id,
        )
    ).scalar_one_or_none()

    old_owner_membership.role = ProjectRole.member

    db.add(changing_membership)
    db.add(old_owner_membership)
    db.commit()
    db.refresh()

    return changing_membership
