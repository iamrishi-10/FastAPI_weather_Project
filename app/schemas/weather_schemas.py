from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WeatherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city_id: int
    temperature: float
    apparent_temperature: float
    humidity: float
    wind_speed: float
    weather_code: int
    observed_at: datetime
    fetched_at: datetime
