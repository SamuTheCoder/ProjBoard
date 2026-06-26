from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dal.database import get_db
from core.dependencies import get_current_user
from schemas.project_schemas import ProjectCreate, ProjectUpdate, ProjectResponse
import services.project_service as project_service

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
        return project_service.update(
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
        project_service.delete(db, project_id, current_user.user_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
