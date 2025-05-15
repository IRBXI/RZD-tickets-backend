from fastapi import APIRouter, BackgroundTasks
from starlette.background import BackgroundTask

# import api.models

router = APIRouter(tags=["login"])

# @router.post("/register", response_model=models.User)
# async def register_handler(
#     data: models.UserRegister,
#     bg_task: BackgroundTask,
# ):
