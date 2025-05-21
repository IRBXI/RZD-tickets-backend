from fastapi import APIRouter

from app.api.routes import login, train, stations

api_router = APIRouter()

api_router.include_router(login.router)
api_router.include_router(train.router)
api_router.include_router(stations.router)
