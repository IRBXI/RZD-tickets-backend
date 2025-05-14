from fastapi import APIRouter, BackgroundTasks
from fastapi.exceptions import HTTPException
from starlette.background import BackgroundTask
from app.core import db
import models
import db_models

router = APIRouter(tags=["login"])

@router.post("/register", response_model=models.User)
async def register_handler(
    data: models.UserRegister,
    bg_task: BackgroundTask
):
    user = await db_models.User.find_by_email(email=data.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists... Try anotha email vro...")

    user_data = data.dict(exclude={"confirmed_password"})
    user = db_models.User(**user_data)

    await user.save()
