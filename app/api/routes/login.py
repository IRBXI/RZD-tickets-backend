from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException
from fastapi.security import OAuth2AuthorizationCodeBearer

import app.models as models
import app.db_models as db_models

router = APIRouter(tags=["login"])

@router.post("/register", response_model=models.User)
async def register_handler(
    data: models.UserRegister,
):
    user = await db_models.User.find_by_email(email=data.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists... Try anotha email vro...")

    user_data = data.dict(exclude={"confirmed_password"})
    user = db_models.User(**user_data)

    await user.save()

@router.post("/login")
async def login(
    data: models.UserLogin,
    response: Response
):
    user = await db_models.User.authorize(data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Wrong user auth info")

    user_data =
