from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from dal.models.project_member_model import ProjectMember
from dal.models.project_model import Project
from dal.models.task_model import ReviewStatus, Task, TaskStatus
from schemas.task_schemas import TaskCreate, TaskUpdate

_CREATOR_UPDATE_FIELDS = frozenset(
    {
        "task_name",
        "task_description",
        "assignee_id",
        "reviewer_id",
        "priority",
        "task_deadline",
    }
)
_ASSIGNEE_UPDATE_FIELDS = frozenset({"status"})
_REVIEWER_UPDATE_FIELDS = frozenset({"review_status"})
_ALLOWED_STATUS_TRANSITIONS = {
    TaskStatus.backlog: frozenset({TaskStatus.ready}),
    TaskStatus.ready: frozenset({TaskStatus.in_progress}),
    TaskStatus.in_progress: frozenset({TaskStatus.to_review}),
    TaskStatus.to_review: frozenset({TaskStatus.done}),
    TaskStatus.done: frozenset(),
}


def _get_project(db: Session, project_id: int) -> Project:
    project = db.execute(
        select(Project).where(Project.project_id == project_id)
    ).scalar_one_or_none()

    if project is None:
        raise ValueError("Project not found")

    return project


def _get_task(db: Session, task_id: int) -> Task:
    task = db.execute(select(Task).where(Task.task_id == task_id)).scalar_one_or_none()

    if task is None:
        raise ValueError("Task not found")

    return task


def _is_project_member(
    db: Session,
    project: Project,
    user_id: int,
) -> bool:
    if project.owner_id == user_id:
        return True

    membership = db.execute(
        select(ProjectMember).where(
            ProjectMember.project_id == project.project_id,
            ProjectMember.user_id == user_id,
        )
    ).scalar_one_or_none()

    return membership is not None


def _require_project_member(
    db: Session,
    project: Project,
    user_id: int,
    *,
    role_name: str = "User",
) -> None:
    if not _is_project_member(db, project, user_id):
        raise PermissionError(f"{role_name} does not belong to this project")


def _validate_participants(
    db: Session,
    project: Project,
    *,
    assignee_id: int | None = None,
    reviewer_id: int | None = None,
    fields_to_validate: Iterable[str],
) -> None:
    fields = set(fields_to_validate)

    if "assignee_id" in fields and assignee_id is not None:
        if not _is_project_member(db, project, assignee_id):
            raise ValueError("Assignee must be a member of this project")

    if "reviewer_id" in fields and reviewer_id is not None:
        if not _is_project_member(db, project, reviewer_id):
            raise ValueError("Reviewer must be a member of this project")


def _apply_task_workflow_rules(task: Task, update_data: dict) -> None:
    requested_fields = set(update_data)
    requested_status = update_data.get("status")
    requested_review_status = update_data.get("review_status")

    resulting_reviewer_id = update_data.get("reviewer_id", task.reviewer_id)
    reviewer_changed = (
        "reviewer_id" in requested_fields and resulting_reviewer_id != task.reviewer_id
    )

    if reviewer_changed:
        if requested_review_status is not None:
            raise ValueError("Review status cannot be set while changing the reviewer")
        update_data["review_status"] = None

    if requested_status is not None and requested_status != task.status:
        allowed_statuses = _ALLOWED_STATUS_TRANSITIONS[task.status]
        if requested_status not in allowed_statuses:
            raise ValueError(
                f"Task status cannot change from {task.status.value} "
                f"to {requested_status.value}"
            )

        if requested_status == TaskStatus.to_review:
            if resulting_reviewer_id is None:
                raise ValueError("A task entering review must have a reviewer")
            update_data["review_status"] = ReviewStatus.pending

        if requested_status == TaskStatus.done:
            resulting_review_status = update_data.get(
                "review_status", task.review_status
            )
            if resulting_review_status != ReviewStatus.approved:
                raise ValueError("A task must be approved before it can be done")

    if "review_status" in requested_fields and not reviewer_changed:
        if requested_review_status not in {
            ReviewStatus.approved,
            ReviewStatus.rejected,
        }:
            raise ValueError("Review status can only be approved or rejected")

        if task.status != TaskStatus.to_review:
            raise ValueError(
                "A task can only be approved or rejected while it is in review"
            )

        if resulting_reviewer_id is None:
            raise ValueError("A task without a reviewer cannot be reviewed")

        if requested_review_status == ReviewStatus.rejected:
            update_data["status"] = TaskStatus.in_progress

    resulting_status = update_data.get("status", task.status)
    if resulting_reviewer_id is None:
        update_data["review_status"] = None

        if resulting_status == TaskStatus.to_review:
            if requested_status == TaskStatus.to_review:
                raise ValueError("A task entering review must have a reviewer")
            update_data["status"] = TaskStatus.in_progress
            resulting_status = TaskStatus.in_progress

    resulting_review_status = update_data.get("review_status", task.review_status)
    if (
        resulting_status == TaskStatus.done
        and resulting_review_status != ReviewStatus.approved
    ):
        raise ValueError("A completed task must retain an approved review")


def _commit_and_refresh(db: Session, task: Task) -> Task:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    db.refresh(task)
    return task


def _get_task_in_project_for_user(
    db: Session,
    project_id: int,
    task_id: int,
    current_user_id: int,
) -> tuple[Project, Task]:
    project = _get_project(db, project_id)
    _require_project_member(db, project, current_user_id, role_name="Current user")

    task = _get_task(db, task_id)

    if task.project_id != project_id:
        raise ValueError("Task not found in this project")

    return project, task


def create_task(
    db: Session,
    project_id: int,
    task_data: TaskCreate,
    current_user_id: int,
) -> Task:
    project = _get_project(db, project_id)
    _require_project_member(db, project, current_user_id, role_name="Current user")

    _validate_participants(
        db,
        project,
        assignee_id=task_data.assignee_id,
        reviewer_id=task_data.reviewer_id,
        fields_to_validate={"assignee_id", "reviewer_id"},
    )

    new_task = Task(
        project_id=project_id,
        created_by=current_user_id,
        task_name=task_data.task_name,
        task_description=task_data.task_description,
        assignee_id=task_data.assignee_id,
        reviewer_id=task_data.reviewer_id,
        priority=task_data.priority,
        review_status=None,
        task_deadline=task_data.task_deadline,
    )

    db.add(new_task)
    return _commit_and_refresh(db, new_task)


def get_tasks_for_project(
    db: Session, project_id: int, current_user_id: int
) -> list[Task]:
    project = _get_project(db, project_id)
    _require_project_member(db, project, current_user_id, role_name="Current user")

    tasks = (
        db.execute(
            select(Task)
            .where(Task.project_id == project_id)
            .order_by(Task.created_at.desc())
        )
        .scalars()
        .all()
    )
    return tasks


def get_task_for_user(
    db: Session,
    project_id: int,
    task_id: int,
    current_user_id: int,
) -> Task:
    _, task = _get_task_in_project_for_user(db, project_id, task_id, current_user_id)

    return task


def update_task(
    db: Session,
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    current_user_id: int,
) -> Task:
    project, task = _get_task_in_project_for_user(
        db, project_id, task_id, current_user_id
    )

    update_data = task_data.model_dump(exclude_unset=True)
    if not update_data:
        return task

    if project.owner_id != current_user_id:
        allowed_fields: set[str] = set()

        if task.created_by == current_user_id:
            allowed_fields.update(_CREATOR_UPDATE_FIELDS)
        if task.assignee_id == current_user_id:
            allowed_fields.update(_ASSIGNEE_UPDATE_FIELDS)
        if task.reviewer_id == current_user_id:
            allowed_fields.update(_REVIEWER_UPDATE_FIELDS)

        forbidden_fields = sorted(set(update_data) - allowed_fields)
        if forbidden_fields:
            fields = ", ".join(forbidden_fields)
            raise PermissionError(
                f"Current user cannot update these task fields: {fields}"
            )

    _validate_participants(
        db,
        project,
        assignee_id=update_data.get("assignee_id"),
        reviewer_id=update_data.get("reviewer_id"),
        fields_to_validate=update_data,
    )

    _apply_task_workflow_rules(task, update_data)

    for field, value in update_data.items():
        setattr(task, field, value)

    return _commit_and_refresh(db, task)


def delete_task(
    db: Session,
    project_id: int,
    task_id: int,
    current_user_id: int,
) -> None:
    project, task = _get_task_in_project_for_user(
        db, project_id, task_id, current_user_id
    )

    if project.owner_id != current_user_id and task.created_by != current_user_id:
        raise PermissionError("Only the project owner or task creator can delete tasks")

    db.delete(task)

    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
