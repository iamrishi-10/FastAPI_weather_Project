from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.orm_models.user_orm_models import User
from app.dependencies.auth import get_current_user
from app.schemas.allowed_city_schemas import AllowedCityCreate, AllowedCityResponse
from app.services.allowed_city_services import (
    CityLimitExceededError,
    CityNotFoundError,
    CityProviderUnavailableError,
    DuplicateCityError,
    create_allowed_city,
    delete_allowed_city,
    get_user_cities,
)


router = APIRouter(
    prefix="/users/cities",
    tags=["allowed-cities"]
)


@router.post("", response_model=AllowedCityResponse, status_code=status.HTTP_201_CREATED)
async def add_allowed_city(
    city_data: AllowedCityCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        new_city = await create_allowed_city(db, current_user.user_id, city_data)
    except CityLimitExceededError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except DuplicateCityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    except CityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except CityProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    db.commit()
    return new_city


@router.get("", response_model=list[AllowedCityResponse])
def list_allowed_cities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_user_cities(db, current_user.user_id)


@router.delete("/{city_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_allowed_city(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_allowed_city(db, current_user.user_id, city_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    db.commit()
