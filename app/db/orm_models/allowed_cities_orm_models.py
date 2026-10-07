from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Identity, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.db.orm_models.user_orm_models import User
    from app.db.orm_models.weather_orm_models import WeatherSnapshot


class AllowedCity(Base):
    __tablename__ = "allowed_cities"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "city_name", "state_name", name="uq_allowed_cities_user_city_state"
        ),
    )

    city_id: Mapped[int] = mapped_column(Identity(), primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    city_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship(
        back_populates="allowed_cities"
    )
    weather_snapshots: Mapped[list["WeatherSnapshot"]] = relationship(
        back_populates="city", cascade="all, delete-orphan", passive_deletes=True
    )
