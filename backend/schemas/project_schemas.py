from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    AfterValidator,
)
import re
from datetime import datetime
from typing import Annotated


class ProjectBase(BaseModel):
    project_name: str = Field(min_length=1, max_length=100)
    project_description: str | None = Field(max_length=255)


# owner_id is decided by the current logged-in user
class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(ProjectBase):
    project_name: str | None = Field(default=None, min_length=1, max_length=100)
    project_description: str | None = Field(default=None, max_length=255)


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime | None
