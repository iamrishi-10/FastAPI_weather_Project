from fastapi import APIRouter, Depends, HTTPException, status
from app.db.orm_models.user_orm_models import User
from app.schemas.user_schemas import  UserResponse
from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user


