from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.orm_models.user_orm_models import User
from app.dependencies.auth import get_current_user
from app.schemas.weather_schemas import WeatherResponse
from app.services.weather_services import (
    CityNotOwnedError,
    WeatherProviderUnavailableError,
    fetch_and_store_weather,
    get_latest_weather,
    get_weather_history,
)


router = APIRouter(
    prefix="/weather",
    tags=["weather"],
)


@router.post("/fetch/{city_id}", response_model=WeatherResponse, status_code=status.HTTP_201_CREATED)
async def fetch_weather(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        snapshot = await fetch_and_store_weather(db, current_user.user_id, city_id)
    except CityNotOwnedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    except WeatherProviderUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))

    db.commit()
    return snapshot


@router.get("/latest/{city_id}", response_model=WeatherResponse)
def latest_weather(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        snapshot = get_latest_weather(db, current_user.user_id, city_id)
    except CityNotOwnedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))

    if snapshot is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stored weather for this city")

    return snapshot


@router.get("/history/{city_id}", response_model=list[WeatherResponse])
def weather_history(
    city_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return get_weather_history(db, current_user.user_id, city_id)
    except CityNotOwnedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
