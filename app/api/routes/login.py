from uuid import uuid4
from fastapi import APIRouter

router = APIRouter(tags=["login"])

from datetime import datetime
from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException
from fastapi import Cookie, Depends
from tortoise.exceptions import DoesNotExist
from typing_extensions import Annotated

from app.models import models, db_models
from app.models.db_models import hash_password
from app.core.users import get_current_active_user, oauth2_model
from app.core.jwt import create_token_pair, add_refresh_token_cookie, refresh_token_state, decode_access_token
from app.core.jwt import JTI, SUB, EXP
from app.core.exceptions import BadRequestException, ForbiddenException

router = APIRouter(tags=["login"])



@router.post("/register", response_model=models.User)
async def register(
    data: models.UserRegister
):
    if await db_models.User.filter(email=data.email):
        raise HTTPException(status_code=400, detail="User already exists")

    user = await db_models.User.create(
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        active=True
    )

    return models.User.from_orm(user)


@router.post("/login")
async def login(data: models.UserLogin, response: Response):
    user = await db_models.User.authorize(data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Wrong user auth info")

    if not user.active:
        raise ForbiddenException()

    user = models.User.from_orm(user)

    token_pair = create_token_pair(user=user)

    add_refresh_token_cookie(response=response, token=token_pair.refresh.token)

    return {"token": token_pair.access.token}


@router.post("/refresh")
async def refresh(refresh: Annotated[str | None, Cookie()] = None):
    if not refresh:
        raise BadRequestException(detail="Refresh token required")
    return refresh_token_state(token=refresh)


@router.get("/user/{id}", response_model=models.User)
async def get_user(user: Annotated[models.User, Depends(get_current_active_user)]):
    try:
        return user
    except DoesNotExist:
        raise BadRequestException


@router.post("/logout", response_model=models.SuccessfulResponse)
async def logout(token: Annotated[str, Depends(oauth2_model)]):
    data = await decode_access_token(token=token)

    banned_token = db_models.BannedToken(
        id=data[JTI], expired=datetime.utcfromtimestamp(data[EXP])
    )
    await banned_token.save()

    return {"msg": "Succesfully logout"}
