from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from dal.database import get_db
from schemas.user_schemas import UserCreate, UserResponse, UserLogin, UserLoginResponse
from services.user_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        return register_user(db, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )


@router.post("/login", response_model=UserLoginResponse, status_code=status.HTTP_200_OK)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    try:
        return login_user(db, login_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={
                "WWW-Authenticate": "Bearer"
            },  # this endpoint requires bearer token auth
        )
