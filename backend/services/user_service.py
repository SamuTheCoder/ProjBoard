from sqlalchemy.orm import Session
from sqlalchemy import select

from dal.models.user_model import User
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


def delete_user(db: Session, user: User) -> None:
    """
    Business rule:
    User can delete their own account.
    """

    # TODO: db.delete(user), db.commit()
    pass
