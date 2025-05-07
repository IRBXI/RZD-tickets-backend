from fastapi import FastAPI
from tortoise import Tortoise, run_async
from app.core.config import settings
from app.api.main import api_router


async def main():
    await Tortoise.init(
        db_url=str(settings.DATABASE_URI),
        modules={"models": ["app.db_models"]},
    )
    await Tortoise.generate_schemas()

    app = FastAPI(
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)
    pass


run_async(main())
