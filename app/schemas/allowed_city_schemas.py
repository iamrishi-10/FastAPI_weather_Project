from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AllowedCityCreate(BaseModel):
    city_name: str


class AllowedCityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    city_id: int
    city_name: str
    state_name: str | None
    latitude: float
    longitude: float
    created_at: datetime
