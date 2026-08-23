from datetime import datetime
from typing import Any, ClassVar

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, model_validator

from dal.models.task_model import TaskStatus, ReviewStatus


class TaskBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    task_name: str = Field(min_length=1, max_length=100)
    task_description: str | None = None


class TaskCreate(TaskBase):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    assignee_id: int | None = Field(default=None, gt=0)
    reviewer_id: int | None = Field(default=None, gt=0)
    priority: int = Field(default=3, ge=1, le=5)
    task_deadline: AwareDatetime | None = None


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    _NON_NULLABLE_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {"task_name", "priority", "status"}
    )

    task_name: str | None = Field(default=None, min_length=1, max_length=100)
    task_description: str | None = None
    assignee_id: int | None = Field(default=None, gt=0)
    reviewer_id: int | None = Field(default=None, gt=0)
    priority: int | None = Field(default=None, ge=1, le=5)
    status: TaskStatus | None = None
    review_status: ReviewStatus | None = None
    task_deadline: AwareDatetime | None = None

    @model_validator(mode="before")
    @classmethod
    def reject_null_for_non_nullable_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            null_fields = sorted(
                field
                for field in cls._NON_NULLABLE_FIELDS
                if field in data and data[field] is None
            )
            if null_fields:
                fields = ", ".join(null_fields)
                raise ValueError(f"These fields cannot be null: {fields}")
        return data


class TaskResponse(TaskBase):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    project_id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    assignee_id: int | None
    reviewer_id: int | None
    priority: int
    status: TaskStatus
    review_status: ReviewStatus | None
    task_deadline: datetime | None
