from app.db.base import Base
from app.db.database import engine
from app.db.orm_models.user_orm_models import User
from app.db.orm_models.allowed_cities_orm_models import AllowedCity
from app.db.orm_models.weather_orm_models import WeatherSnapshot

Base.metadata.create_all(engine)

print(f"Tables created: {list(Base.metadata.tables.keys())}")
