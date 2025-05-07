from fastapi import APIRouter

router = APIRouter(tags=["login"])


@router.get("/login")
async def hello() -> str:
    return "Hello world!"
