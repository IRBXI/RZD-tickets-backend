from fastapi import APIRouter

from app.api.routes import auth, trains, stations, me

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(me.router)
api_router.include_router(trains.router)
api_router.include_router(stations.router)
