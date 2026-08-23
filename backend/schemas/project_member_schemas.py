from datetime import datetime
from pydantic import BaseModel, ConfigDict

from dal.models.project_member_model import ProjectRole


class ProjectMemberCreate(BaseModel):
    user_id: int


class ProjectMemberResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    user_id: int
    role: ProjectRole
    joined_at: datetime
