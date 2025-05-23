from uuid import uuid4
from fastapi import APIRouter

router = APIRouter(tags=["login"])

from datetime import datetime
from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException
from fastapi import status, Cookie, Depends
from fastapi.security import OAuth2PasswordBearer
from tortoise.exceptions import DoesNotExist
from typing import Any, Annotated

from app.models import models, db_models
from app.models.db_models import hash_password
from app.core.jwt import create_token_pair, add_refresh_token_cookie, refresh_token_state, decode_access_token
from curses.ascii import US
from app.core.jwt import JTI
from app.core.jwt import EXP

router = APIRouter(tags=["login"])

oauth2_model = OAuth2PasswordBearer(tokenUrl="login")

class ForbiddenException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail if detail else "Forbidden",
        )

class BadRequestException(HTTPException):
    def __init__(self, detail: Any = None) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail if detail else "Bad request"
        )

@router.post("/register", response_model=models.User)
async def register(
    data: models.UserRegister
):
    user = await db_models.User.find_by_email(email=data.email)
    if user:
        raise HTTPException(status_code=400, detail="User already exists")

    user_data = data.dict(exclude={"confirmed_password"})
    user_data["password"] = hash_password(user_data["password"])

    user = db_models.User(**user_data)
    user.active = True
    await user.save()

    user_model = models.User.from_orm(user)

    return user_model


@router.post("/login")
async def login(
    data: models.UserLogin,
    response: Response
):
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
async def get_user(id: str):
    try:
        user = await db_models.User.get(name=id)

        user_schema = models.User.from_orm(user)

        return user_schema
    except DoesNotExist:
        raise BadRequestException

@router.post("/logout", response_model=models.SuccessfulResponse)
async def logout(
    token: Annotated[str, Depends(oauth2_model)]
):
    print(token)
    data = await decode_access_token(token=token)
    print(data[JTI])

    banned_token = db_models.BannedToken(
        id=data[JTI], expired=datetime.utcfromtimestamp(data[EXP])
    )
    await banned_token.save()

    return {"msg": "Succesfully logout"}
