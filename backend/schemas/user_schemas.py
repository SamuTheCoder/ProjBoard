from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    AfterValidator,
)
import re
from datetime import datetime
from typing import Annotated


def validate_password_strength(password: str) -> str:
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one number")
    return password


Password = Annotated[
    str,
    Field(min_length=8, max_length=128),
    AfterValidator(validate_password_strength),
]


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=255)
    first_name: str = Field(min_length=1, max_length=50)
    last_name: str = Field(min_length=1, max_length=50)


class UserCreate(UserBase):
    password: Password


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = Field(default=None, max_length=255)
    first_name: str | None = Field(default=None, min_length=1, max_length=50)
    last_name: str | None = Field(default=None, min_length=1, max_length=50)
    password: Password | None = None


class UserResponse(UserBase):
    user_id: int
    created_at: datetime

    # converts SQLAlchemy object model to Pydantic JSON/dict model
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)


class UserLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
