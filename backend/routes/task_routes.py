from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dal.database import get_db
from core.dependencies import get_current_user
from dal.models.user_model import User
from schemas.task_schemas import TaskCreate, TaskUpdate, TaskResponse
import services.task_service as task_service

router = APIRouter(tags=["tasks"])


def _value_error_status_code(error: ValueError) -> int:
    message = str(error).lower()

    if "not found" in message:
        return status.HTTP_404_NOT_FOUND

    return status.HTTP_400_BAD_REQUEST


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.create_task(
            db=db,
            project_id=project_id,
            task_data=task_data,
            current_user_id=current_user.user_id,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=_value_error_status_code(e),
            detail=str(e),
        )


@router.get(
    "/projects/{project_id}/tasks",
    response_model=list[TaskResponse],
    status_code=status.HTTP_200_OK,
)
def list_project_tasks(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.get_tasks_for_project(
            db=db,
            project_id=project_id,
            current_user_id=current_user.user_id,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=_value_error_status_code(e),
            detail=str(e),
        )


@router.get(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def get_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.get_task_for_user(
            db=db,
            project_id=project_id,
            task_id=task_id,
            current_user_id=current_user.user_id,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=_value_error_status_code(e),
            detail=str(e),
        )


@router.patch(
    "/projects/{project_id}/tasks/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
)
def update_task(
    project_id: int,
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return task_service.update_task(
            db=db,
            project_id=project_id,
            task_id=task_id,
            task_data=task_data,
            current_user_id=current_user.user_id,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=_value_error_status_code(e),
            detail=str(e),
        )


@router.delete(
    "/projects/{project_id}/tasks/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    project_id: int,
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        task_service.delete_task(
            db=db,
            project_id=project_id,
            task_id=task_id,
            current_user_id=current_user.user_id,
        )
        return None

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=_value_error_status_code(e),
            detail=str(e),
        )
