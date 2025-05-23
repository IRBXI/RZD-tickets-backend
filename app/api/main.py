from fastapi import APIRouter

from app.api.routes import login, trains, stations

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(trains.router)
api_router.include_router(stations.router)
