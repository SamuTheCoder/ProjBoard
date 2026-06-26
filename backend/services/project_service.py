from sqlalchemy.orm import Session
from sqlalchemy import select

from dal.models.project_model import Project
from dal.models.project_member_model import ProjectRole, ProjectMember
from schemas.project_schemas import ProjectCreate, ProjectUpdate


def create_project(
    db: Session,
    project_data: ProjectCreate,
    owner_id: int,
) -> Project:
    existing_project = db.execute(
        select(Project).where(
            Project.owner_id == owner_id,
            Project.project_name == project_data.project_name,
        )
    ).scalar_one_or_none()

    if existing_project is not None:
        raise ValueError("Project name already exists for this user")

    new_project = Project(
        project_name=project_data.project_name,
        project_description=project_data.project_description,
        owner_id=owner_id,
    )

    db.add(new_project)

    # Needed because ProjectMember needs the generated project_id
    db.flush()

    owner_membership = ProjectMember(
        project_id=new_project.project_id,
        user_id=owner_id,
        role=ProjectRole.owner,
    )

    db.add(owner_membership)

    db.commit()
    db.refresh(new_project)

    return new_project


def get_project_by_id(db: Session, project_id: int) -> Project | None:
    return db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()


def get_project_for_user(
    db: Session,
    project_id: int,
    user_id: int,
) -> Project | None:
    return db.execute(
        select(Project)
        .join(Project.members)
        .where(
            Project.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
    ).scalar_one_or_none()


def get_projects_for_user(db: Session, user_id: int) -> list[Project]:
    return (
        db.execute(
            select(Project)
            .join(Project.members)
            .where(ProjectMember.user_id == user_id)
        )
        .scalars()
        .all()
    )


def get_projects_by_owner(db: Session, owner_id: int) -> list[Project]:
    return (
        db.execute(select(Project).where(Project.owner_id == owner_id)).scalars().all()
    )


def update_project(
    db: Session,
    project_id: int,
    project_data: ProjectUpdate,
    current_user_id: int,
) -> Project:
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    if project.owner_id != current_user_id:
        raise PermissionError("Only the project owner can update this project")

    update_data = project_data.model_dump(exclude_unset=True)

    if "project_name" in update_data:
        if update_data["project_name"] is None:
            raise ValueError("Project name cannot be null")

        existing_project = db.execute(
            select(Project).where(
                Project.owner_id == current_user_id,
                Project.project_name == update_data["project_name"],
                Project.project_id != project_id,
            )
        ).scalar_one_or_none()

        if existing_project is not None:
            raise ValueError("Project name already exists for this user")

        project.project_name = update_data["project_name"]

    if "project_description" in update_data:
        project.project_description = update_data["project_description"]

    db.commit()
    db.refresh(project)

    return project


def delete_project(
    db: Session,
    project_id: int,
    current_user_id: int,
) -> None:
    project = get_project_by_id(db, project_id)

    if project is None:
        raise ValueError("Project not found")

    if project.owner_id != current_user_id:
        raise PermissionError("Only the project owner can delete this project")

    db.delete(project)
    db.commit()
