from fastapi import APIRouter

router = APIRouter(tags=["login"])


@router.get("/login")
def hello() -> str:
    return "Hello world!"
