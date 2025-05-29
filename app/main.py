from dotenv import load_dotenv

load_dotenv()

from app.core.config import settings

from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import RegisterTortoise
from app.services import setup_services
from app.repositories import setup_repos
from app.api.main import api_router
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await RegisterTortoise(
        app,
        db_url=str(settings.DATABASE_URI),
        modules={"models": ["app.models.db_models"]},
        generate_schemas=True,
    )

    await setup_services()
    setup_repos()

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
