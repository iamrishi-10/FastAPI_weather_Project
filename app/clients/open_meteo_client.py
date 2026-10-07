import asyncio
from datetime import datetime, timezone

import httpx
import openmeteo_requests

from app.core.config import HTTP_TIMEOUT_SECONDS, OPEN_METEO_FORECAST_URL, OPEN_METEO_GEOCODING_URL

# Deliberate lifecycle choice: openmeteo_requests.AsyncClient holds no connection
# until first use, so a module-level singleton is fine for this project's scale.
# Revisit with FastAPI lifespan management if the app grows multiple external clients.
_forecast_client = openmeteo_requests.AsyncClient()

ALLOWED_COUNTRY_CODE = "IN"

# Requested in this exact order and read back by positional index below -
# current.Variables(i) corresponds to CURRENT_WEATHER_VARIABLES[i]. Keep the
# two in sync; the enumerate() loop ties them together so there is only one
# place to edit when adding/removing a variable.
CURRENT_WEATHER_VARIABLES = [
    "temperature_2m",
    "apparent_temperature",
    "relative_humidity_2m",
    "wind_speed_10m",
    "weather_code",
]
_VARIABLE_TO_FIELD = {
    "temperature_2m": "temperature",
    "apparent_temperature": "apparent_temperature",
    "relative_humidity_2m": "humidity",
    "wind_speed_10m": "wind_speed",
    "weather_code": "weather_code",
}


class OpenMeteoClientError(Exception):
    """Base error for all Open-Meteo client failures."""


class GeocodingError(OpenMeteoClientError):
    """Geocoding request failed or the provider was unreachable."""


class WeatherFetchError(OpenMeteoClientError):
    """Forecast request failed, timed out, or returned an unexpected shape."""


async def geocode_city(city_name: str, state_name: str | None = None) -> dict | None:
    try:
        async with httpx.AsyncClient(timeout=HTTP_TIMEOUT_SECONDS) as client:
            response = await client.get(
                OPEN_METEO_GEOCODING_URL,
                params={"name": city_name, "count": 10, "language": "en", "format": "json"},
            )
            response.raise_for_status()
    except httpx.TimeoutException as exc:
        raise GeocodingError(f"Geocoding provider timed out for '{city_name}'") from exc
    except httpx.HTTPError as exc:
        raise GeocodingError(f"Geocoding provider unavailable for '{city_name}'") from exc

    results = response.json().get("results") or []
    results = [r for r in results if r.get("country_code") == ALLOWED_COUNTRY_CODE]

    if state_name is not None:
        results = [
            r for r in results
            if (r.get("admin1") or "").casefold() == state_name.casefold()
        ] or results

    if not results:
        return None

    match = results[0]
    return {
        "city_name": match["name"],
        "state_name": match.get("admin1"),
        "country": match.get("country"),
        "country_code": match.get("country_code"),
        "latitude": match["latitude"],
        "longitude": match["longitude"],
    }


async def fetch_current_weather(latitude: float, longitude: float) -> dict:
    try:
        responses = await _forecast_client.weather_api(
            OPEN_METEO_FORECAST_URL,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": CURRENT_WEATHER_VARIABLES,
                "timezone": "UTC",
            },
        )
    except Exception as exc:
        raise WeatherFetchError(
            f"Weather provider request failed for ({latitude}, {longitude})"
        ) from exc

    if not responses:
        raise WeatherFetchError("Weather provider returned no responses")

    current = responses[0].Current()
    if current is None:
        raise WeatherFetchError("Weather provider response had no current-weather block")

    try:
        values = {
            _VARIABLE_TO_FIELD[name]: current.Variables(i).Value()
            for i, name in enumerate(CURRENT_WEATHER_VARIABLES)
        }
    except (IndexError, AttributeError) as exc:
        raise WeatherFetchError("Weather provider response was missing expected variables") from exc

    values["weather_code"] = int(values["weather_code"])
    values["observed_at"] = datetime.fromtimestamp(current.Time(), tz=timezone.utc)
    return values


if __name__ == "__main__":
    async def _demo() -> None:
        city = await geocode_city("Hyderabad")
        print("Geocoded city:", city)

        if city is not None:
            weather = await fetch_current_weather(city["latitude"], city["longitude"])
            print("Current weather:", weather)

    asyncio.run(_demo())
