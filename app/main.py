from collections.abc import AsyncGenerator
from fastapi import FastAPI
from tortoise.contrib.fastapi import RegisterTortoise
from app.core.config import settings
from app.api.main import api_router
from app.core.db import load_stations
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await RegisterTortoise(
        app,
        db_url=str(settings.DATABASE_URI),
        modules={"models": ["app.db_models"]},
        generate_schemas=True,
    )
    await load_stations()

    yield


app = FastAPI(openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)
app.include_router(api_router, prefix=settings.API_V1_STR)
