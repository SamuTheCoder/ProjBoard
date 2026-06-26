from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from dal.database import get_db
from core.dependencies import get_current_user
from schemas.user_schemas import UserResponse
from services.user_service import get_current_user_from_token, delete_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return current_user


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    delete_user(db, current_user.user_id)
    return None
