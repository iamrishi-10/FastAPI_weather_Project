from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.schemas.auth_schemas import SignUpRequest,LoginRequest, TokenResponse
from app.schemas.user_schemas import  UserResponse
from app.services.auth_services import sign_up_new_user, authenticate_user
from app.core.security import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(signup_data: SignUpRequest, db: Session = Depends(get_db)):
    new_user = sign_up_new_user(db, signup_data)

    if new_user is None:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, detail="User already exists")


    db.commit()
    return new_user


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data)

    if user is None:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    access_token =create_access_token({'sub': str(user.user_id)})

    return TokenResponse(access_token=access_token, token_type="bearer")


