from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise
from app.api.routes.train import setup_api
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
    await setup_api()
    # await load_stations()

    yield


app = FastAPI(openapi_url=f"{settings.API_V1_STR}/openapi.json", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.API_V1_STR)
