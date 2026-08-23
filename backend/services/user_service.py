from sqlalchemy.orm import Session
from sqlalchemy import select, update, case, delete
from sqlalchemy.exc import SQLAlchemyError

from dal.models.user_model import User
from dal.models.task_model import Task, TaskStatus
from dal.models.project_model import Project
from schemas.user_schemas import UserCreate, UserLogin, UserLoginResponse
from core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)


def register_user(db: Session, user_data: UserCreate) -> User:

    check_username = db.execute(
        select(User).where(User.username == user_data.username)
    ).scalar_one_or_none()
    if check_username is not None:
        raise ValueError("Username already exists")

    check_email = db.execute(
        select(User).where(User.email == user_data.email)
    ).scalar_one_or_none()
    if check_email is not None:
        raise ValueError("Email already exists")

    created_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        first_name=user_data.first_name,
        last_name=user_data.last_name,
    )

    db.add(created_user)
    db.commit()
    db.refresh(created_user)

    return created_user


def login_user(db: Session, login_data: UserLogin) -> UserLoginResponse:

    user = db.execute(
        select(User).where(User.username == login_data.username)
    ).scalar_one_or_none()

    if user is None:
        raise ValueError("Invalid username or password")

    if not verify_password(login_data.password, user.password_hash):
        raise ValueError("Invalid username or password")

    token = create_access_token(data={"sub": str(user.user_id)})

    return UserLoginResponse(access_token=token)


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Data lookup helper.
    """

    return db.execute(select(User).where(User.user_id == user_id)).scalar_one_or_none()


def get_current_user_from_token(db: Session, token: str) -> User:
    payload = decode_access_token(token)

    sub = payload.get("sub")
    if sub is None:
        raise ValueError("Invalid token")

    try:
        user_id = int(sub)
    except ValueError:
        raise ValueError("Invalid token")

    user = get_user_by_id(db, user_id)

    if user is None:
        raise ValueError("User for token not found")

    return user


def delete_user(db: Session, user_id: int) -> None:
    existing_user = db.execute(
        select(User).where(User.user_id == user_id)
    ).scalar_one_or_none()

    if existing_user is None:
        raise ValueError("User does not exist")

    try:
        # 1. Delete projects owned by this user.
        # Their tasks/members should cascade.
        db.execute(delete(Project).where(Project.owner_id == user_id))

        # 2. Reassign remaining tasks created by this user.
        # These are tasks in projects owned by other users.
        project_owner_subquery = (
            select(Project.owner_id)
            .where(Project.project_id == Task.project_id)
            .scalar_subquery()
        )

        db.execute(
            update(Task)
            .where(Task.created_by == user_id)
            .values(created_by=project_owner_subquery)
        )

        # 3. Clean reviewer state.
        db.execute(
            update(Task)
            .where(Task.reviewer_id == user_id)
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

        # 4. Delete user.
        db.delete(existing_user)
        db.commit()

    except SQLAlchemyError:
        db.rollback()
        raise
