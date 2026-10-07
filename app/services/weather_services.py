from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.open_meteo_client import WeatherFetchError, fetch_current_weather
from app.db.orm_models.allowed_cities_orm_models import AllowedCity
from app.db.orm_models.weather_orm_models import WeatherSnapshot


class WeatherServiceError(Exception):
    """Base error for all weather service failures."""


class CityNotOwnedError(WeatherServiceError):
    """city_id does not belong to this user."""


class WeatherProviderUnavailableError(WeatherServiceError):
    """Weather provider could not be reached."""


def _get_owned_city(db: Session, user_id: int, city_id: int) -> AllowedCity | None:
    return db.scalars(
        select(AllowedCity).where(
            AllowedCity.user_id == user_id,
            AllowedCity.city_id == city_id,
        )
    ).one_or_none()


async def fetch_and_store_weather(db: Session, user_id: int, city_id: int) -> WeatherSnapshot:
    # verify city belongs to that user, read saved lat/lon
    city = _get_owned_city(db, user_id, city_id)
    if city is None:
        raise CityNotOwnedError(f"City {city_id} does not belong to user {user_id}")

    # await fetch_current_weather(...)
    try:
        weather = await fetch_current_weather(city.latitude, city.longitude)
    except WeatherFetchError as exc:
        raise WeatherProviderUnavailableError(str(exc)) from exc

    # build WeatherSnapshot
    snapshot = WeatherSnapshot(
        city_id=city.city_id,
        temperature=weather["temperature"],
        apparent_temperature=weather["apparent_temperature"],
        humidity=weather["humidity"],
        wind_speed=weather["wind_speed"],
        weather_code=weather["weather_code"],
        observed_at=weather["observed_at"],
    )

    # db.add() / db.flush() / db.refresh() / return snapshot
    db.add(snapshot)
    db.flush()
    db.refresh(snapshot)
    return snapshot


def get_latest_weather(db: Session, user_id: int, city_id: int) -> WeatherSnapshot | None:
    if _get_owned_city(db, user_id, city_id) is None:
        raise CityNotOwnedError(f"City {city_id} does not belong to user {user_id}")

    return db.scalars(
        select(WeatherSnapshot)
        .where(WeatherSnapshot.city_id == city_id)
        .order_by(WeatherSnapshot.fetched_at.desc(), WeatherSnapshot.weather_id.desc())
        .limit(1)
    ).one_or_none()


def get_weather_history(db: Session, user_id: int, city_id: int) -> list[WeatherSnapshot]:
    if _get_owned_city(db, user_id, city_id) is None:
        raise CityNotOwnedError(f"City {city_id} does not belong to user {user_id}")

    return list(
        db.scalars(
            select(WeatherSnapshot)
            .where(WeatherSnapshot.city_id == city_id)
            .order_by(WeatherSnapshot.fetched_at.desc(), WeatherSnapshot.weather_id.desc())
        )
    )
