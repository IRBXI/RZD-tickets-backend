from datetime import timedelta, datetime, timezone

from jose import jwt, JWTError
from fastapi import Response, status, HTTPException

from app.models import db_models
from app.models.db_models import BannedToken
from app.core.exceptions import AuthFailedException
from . import config

from app.models.models import User, JwtTokenSchema, TokenPair
from uuid import uuid4

REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"


def _get_utc_current():
    return datetime.now(timezone.utc)


def _create_access_token(data: dict, minutes: int | None = None) -> JwtTokenSchema:
    expiration_date = _get_utc_current() + timedelta(
        minutes=minutes or config.authSettings.ACCESS_TOKEN_EXPIRES_MINUTES
    )

    data[EXP] = expiration_date

    token = JwtTokenSchema(
        token=jwt.encode(
            data,
            config.authSettings.SECRET_KEY,
            algorithm=config.authSettings.ALGORITHM,
        ),
        payload=data,
        expire=expiration_date,
    )

    return token


def _create_refresh_token(data: dict) -> JwtTokenSchema:
    expiration_date = _get_utc_current() + timedelta(
        config.authSettings.REFRESH_TOKEN_EXPIRES_MINUTES
    )

    data[EXP] = expiration_date

    token = JwtTokenSchema(
        token=jwt.encode(
            data,
            config.authSettings.SECRET_KEY,
            algorithm=config.authSettings.ALGORITHM,
        ),
        payload=data,
        expire=expiration_date,
    )

    return token


def create_token_pair(user: User) -> TokenPair:
    data = {SUB: str(user.id), JTI: str(uuid4()), IAT: _get_utc_current()}

    return TokenPair(
        access=_create_access_token(data={**data}),
        refresh=_create_refresh_token(data={**data}),
    )


async def decode_access_token(token: str):
    try:
        data = jwt.decode(
            token,
            config.AuthSettings.SECRET_KEY,
            algorithms=[config.AuthSettings.ALGORITHM],
        )
        banned_token = await BannedToken.get_by_id(data[JTI])
        if banned_token:
            raise JWTError("This token is banned")
    except JWTError:
        raise AuthFailedException()

    return data


def refresh_token_state(token: str):
    try:
        data = jwt.decode(
            token,
            config.AuthSettings.SECRET_KEY,
            algorithms=[config.AuthSettings.ALGORITHM],
        )
    except JWTError as e:
        print("ERROR: ", str(e))
        raise AuthFailedException()

    print(data[JTI])

    return {"token": _create_access_token(data=data).token}


def add_refresh_token_cookie(response: Response, token: str):
    exp = _get_utc_current() + timedelta(
        minutes=config.authSettings.REFRESH_TOKEN_EXPIRES_MINUTES
    )
    exp.replace(tzinfo=timezone.utc)

    response.set_cookie(
        key="refresh", value=token, expires=int(exp.timestamp()), httponly=True
    )
