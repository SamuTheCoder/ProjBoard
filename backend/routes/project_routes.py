from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dal.database import get_db
from core.dependencies import get_current_user
from schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
from schemas.project_member_schemas import (
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberDetailsResponse,
)
from dal.models.user_model import User
import services.project_service as project_service
import services.project_member_service as project_member_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return project_service.create_project(db, project_data, current_user.user_id)


@router.get(
    "/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    project = project_service.get_project_for_user(db, project_id, current_user.user_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or you do not have access to it",
        )
    return project


@router.get("/", response_model=list[ProjectResponse], status_code=status.HTTP_200_OK)
def get_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    projects = project_service.get_projects_for_user(db, current_user.user_id)
    return projects


@router.patch(
    "/{project_id}", response_model=ProjectResponse, status_code=status.HTTP_200_OK
)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        return project_service.update_project(
            db, project_id, project_data, current_user.user_id
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{project_id}", status_code=status.HTTP_200_OK)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        project_service.delete_project(db, project_id, current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_member(
    project_id: int,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_member_service.add_user_to_project(
            db=db,
            project_id=project_id,
            username=member_data.username,
            current_user_id=current_user.user_id,
        )

    except PermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberDetailsResponse],
    status_code=status.HTTP_200_OK,
)
def list_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_member_service.get_project_members(
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.patch(
    "/{project_id}/members/{new_owner_id}",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_200_OK,
)
def transfer_ownership(
    project_id: int,
    new_owner_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return project_member_service.transfer_project_ownership(
            db=db,
            project_id=project_id,
            new_owner_id=new_owner_id,
            current_user_id=current_user.user_id,
        )

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        project_member_service.remove_user_from_project(
            db=db,
            project_id=project_id,
            old_member_id=user_id,
            current_user_id=current_user.user_id,
        )
        return None

    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
