from sqlalchemy.orm import Session
from sqlalchemy import select, update, case
from sqlalchemy.exc import SQLAlchemyError

from schemas.project_member_schemas import ProjectMemberResponse
from dal.models.user_model import User
from dal.models.project_model import Project
from dal.models.project_member_model import ProjectRole, ProjectMember
from dal.models.task_model import Task, TaskStatus
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
        .scalars()
        .all()
    )


def transfer_project_ownership(
    db: Session, project_id: int, new_owner_id: int, current_user_id: int
) -> ProjectMember:
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    if project.owner_id != current_user_id:
        raise PermissionError("Only the project owner can update member's role")

    changing_membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == new_owner_id,
        )
    ).scalar_one_or_none()

    if changing_membership is None:
        raise ValueError("Member to change doesn't exist in the project")

    changing_membership.role = ProjectRole.owner
    project.owner_id = new_owner_id

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
    db.refresh(changing_membership)

    return changing_membership


def remove_user_from_project(
    db: Session,
    project_id: int,
    old_member_id: int,
    current_user_id: int,
) -> None:
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    if project.owner_id != current_user_id:
        raise PermissionError("Only the project owner can remove members")

    if old_member_id == project.owner_id:
        raise ValueError("Cannot remove the project owner from the project")

    old_member = db.execute(
        select(ProjectMember).where(
            ProjectMember.user_id == old_member_id,
            ProjectMember.project_id == project_id,
        )
    ).scalar_one_or_none()

    if old_member is None:
        raise ValueError("Member to remove not found in the project")

    db.execute(
        update(Task)
        .where(
            Task.project_id == project_id,
            Task.assignee_id == old_member_id,
        )
        .values(assignee_id=None)
    )
    db.execute(
        update(Task)
        .where(
            Task.project_id == project_id,
            Task.reviewer_id == old_member_id,
        )
        .values(
            reviewer_id=None,
            review_status=None,
            status=case(
                (
                    Task.status == TaskStatus.to_review,
                    TaskStatus.in_progress,
                ),
                else_=Task.status,
            ),
        )
    )

    db.delete(old_member)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
