from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from dal.models.project_member_model import ProjectRole


class ProjectMemberCreate(BaseModel):
    username: str


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    user_id: int
    role: ProjectRole
    joined_at: datetime


class ProjectMemberDetailsResponse(ProjectMemberResponse):
    username: str
    email: EmailStr
    first_name: str
    last_name: str
