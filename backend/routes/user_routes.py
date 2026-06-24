from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from dal.database import get_db
from schemas.user_schemas import UserResponse
from services.user_service import get_current_user_from_token, delete_user

router = APIRouter(prefix="/users", tags=["users"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.get("/me", response_model=UserResponse)
def get_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        return get_current_user_from_token(db, token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        current_user = get_current_user_from_token(db, token)
        delete_user(db, current_user)
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
