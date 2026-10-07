from fastapi import FastAPI

from app.routes.auth_routes import router as auth_router
from app.routes.user_routes import router as user_router
from app.routes.allowed_cities_routes import router as allowed_cities_router
from app.routes.weather_routes import router as weather_router

app = FastAPI(
    title="Country Restricted Weather API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(allowed_cities_router)
app.include_router(weather_router)


@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Weather Project"}

@app.get("/health")
async def health():
    return {"message": "Healthy"}


