from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.clients.open_meteo_client import GeocodingError, geocode_city
from app.db.orm_models.allowed_cities_orm_models import AllowedCity
from app.schemas.allowed_city_schemas import AllowedCityCreate

MAX_CITIES_PER_USER = 4


class AllowedCityServiceError(Exception):
    """Base error for all allowed-city service failures."""


class CityLimitExceededError(AllowedCityServiceError):
    """User already has the maximum number of allowed cities."""


class DuplicateCityError(AllowedCityServiceError):
    """User has already added this city."""


class CityNotFoundError(AllowedCityServiceError):
    """Geocoding provider found no matching city in India."""


class CityProviderUnavailableError(AllowedCityServiceError):
    """Geocoding provider could not be reached."""


def get_user_cities(db: Session, user_id: int) -> list[AllowedCity]:
    return list(db.scalars(select(AllowedCity).where(AllowedCity.user_id == user_id)))


def get_allowed_city(
    db: Session, user_id: int, city_name: str, state_name: str | None = None
) -> AllowedCity | None:
    conditions = [
        AllowedCity.user_id == user_id,
        func.lower(AllowedCity.city_name) == city_name.lower(),
    ]
    if state_name is None:
        conditions.append(AllowedCity.state_name.is_(None))
    else:
        conditions.append(func.lower(AllowedCity.state_name) == state_name.lower())

    return db.scalars(select(AllowedCity).where(*conditions)).one_or_none()


def count_user_cities(db: Session, user_id: int) -> int:
    return db.scalar(
        select(func.count()).select_from(AllowedCity).where(AllowedCity.user_id == user_id)
    ) or 0


async def create_allowed_city(db: Session, user_id: int, city_data: AllowedCityCreate) -> AllowedCity:
    # count >= 4?
    if count_user_cities(db, user_id) >= MAX_CITIES_PER_USER:
        raise CityLimitExceededError(
            f"User {user_id} already has the maximum of {MAX_CITIES_PER_USER} allowed cities"
        )

    # normalize input
    city_name = city_data.city_name.strip()

    # geocode (restricted to India internally by the client)
    try:
        geocoded = await geocode_city(city_name)
    except GeocodingError as exc:
        raise CityProviderUnavailableError(str(exc)) from exc

    # no result? reject
    if geocoded is None:
        raise CityNotFoundError(f"No city named '{city_name}' found in India")

    # duplicate check using the geocoded canonical city_name + state_name, not
    # the raw input - "Bangalore" and "Bengaluru" must collide here since
    # Open-Meteo returns one canonical name regardless of which alias was
    # requested. Same city name in a different state is NOT a duplicate.
    if get_allowed_city(db, user_id, geocoded["city_name"], geocoded["state_name"]) is not None:
        raise DuplicateCityError(f"'{geocoded['city_name']}' is already an allowed city for this user")

    # create ORM object
    new_city = AllowedCity(
        user_id=user_id,
        city_name=geocoded["city_name"],
        state_name=geocoded["state_name"],
        latitude=geocoded["latitude"],
        longitude=geocoded["longitude"],
    )

    # flush/refresh
    db.add(new_city)
    db.flush()
    db.refresh(new_city)
    return new_city


def delete_allowed_city(db: Session, user_id: int, city_id: int) -> bool:
    city = db.scalars(
        select(AllowedCity).where(
            AllowedCity.user_id == user_id,
            AllowedCity.city_id == city_id,
        )
    ).one_or_none()

    if city is None:
        return False

    db.delete(city)
    db.flush()
    return True
