from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise
from app.services.rzd_APIs import RZD_TrainAPI, RZD_StationAPI
from app.core.config import settings
from app.api.main import api_router
from contextlib import asynccontextmanager

# from app.core.db import load_stations


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # await RegisterTortoise(
    #     app,
    #     db_url=str(settings.DATABASE_URI),
    #     modules={"models": ["app.db_models"]},
    #     generate_schemas=True,
    # )

    # Creating an instances of a singleton classes which will be used by our routers
    await RZD_TrainAPI.create()
    await RZD_StationAPI.create()

    yield


app = FastAPI(openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_V1_STR)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
