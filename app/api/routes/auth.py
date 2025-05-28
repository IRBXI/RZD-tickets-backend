from fastapi import APIRouter

router = APIRouter(tags=["auth"])

from datetime import datetime, timezone
from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException
from fastapi import Cookie, Depends
from typing import Annotated
from app.core.exceptions import AuthFailedException

from app.models import User, SuccessfulResponse, UserLogin, UserRegister
from app.core.config import auth_settings
from app.core.exceptions import BadRequestException, ForbiddenException

from app.services import (
    AbstractUserService,
    AbstractAuthService,
    get_user_service,
    get_auth_service,
)

router = APIRouter(tags=["auth"])


@router.post("/register", response_model=User)
async def register(
    data: UserRegister,
    user_service: Annotated[AbstractUserService, Depends(get_user_service)],
):
    if await user_service.get_user_by_email(data.email):
        raise HTTPException(status_code=400, detail="User already exists")

    return await user_service.create_user(
        email=data.email, password=data.password, name=data.name, active=True
    )


@router.post("/login")
async def login(
    data: UserLogin,
    response: Response,
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
):
    user = await auth_service.authorize(data.email, data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Wrong user auth info")

    if not user.active:
        raise ForbiddenException()

    token_pair = auth_service.create_token(user)

    response.set_cookie(
        key="refresh",
        value=token_pair.refresh.token,
        expires=auth_service.get_expire_time(),
        httponly=True,
    )

    return {"token": token_pair.access.token}


@router.post("/refresh")
async def refresh(
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
    refresh: Annotated[str | None, Cookie()] = None,
):
    if not refresh:
        raise BadRequestException(detail="Refresh token required")

    try:
        token = auth_service.refresh_token_state(refresh)
    except AuthFailedException:
        raise

    return token


@router.post("/logout", response_model=SuccessfulResponse)
async def logout(
    token: Annotated[str, Depends(auth_settings.OAUTH2_MODEL)],
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
):
    try:
        data = await auth_service.decode_access_token(token)
    except AuthFailedException:
        raise

    await auth_service.add_banned_token(
        data["jti"], datetime.fromtimestamp(data["exp"], timezone.utc)
    )

    return {"msg": "Succesfully logout"}
