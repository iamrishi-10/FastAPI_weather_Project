from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Identity, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.orm_models.allowed_cities_orm_models import AllowedCity


class WeatherSnapshot(Base):
    __tablename__ = "weather_snapshots"

    weather_id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    city_id: Mapped[int] = mapped_column(
        ForeignKey("allowed_cities.city_id", ondelete="CASCADE"), nullable=False
    )
    temperature: Mapped[float] = mapped_column(Float, nullable=False)
    apparent_temperature: Mapped[float] = mapped_column(Float, nullable=False)
    humidity: Mapped[float] = mapped_column(Float, nullable=False)
    wind_speed: Mapped[float] = mapped_column(Float, nullable=False)
    weather_code: Mapped[int] = mapped_column(Integer, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    city: Mapped["AllowedCity"] = relationship(
        back_populates="weather_snapshots"
    )
