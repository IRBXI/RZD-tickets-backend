import uuid
import sys
from datetime import timedelta, datetime, timezone

from jose import jwt, JWTError
from fastapi import Response
from . import config

from app.models import User, JwtTokenSchema, TokenPair
from curses.ascii import ENQ
from curses.ascii import alt
from uuid import uuid4


REFRESH_COOKIE_NAME = "refresh"
SUB = "sub"
EXP = "exp"
IAT = "iat"
JTI = "jti"

def _get_utc_current():
    return datetime.now(timezone.utc)


def _create_access_token(
    data: dict,
    minutes: int | None = None
) -> JwtTokenSchema:
    expiration_date = _get_utc_current() + timedelta(
        minutes=minutes or config.AuthSettings.ACCESS_TOKEN_EXPIRES_MINUTES
    )

    data[EXP] = expiration_date

    token = JwtTokenSchema(
        token=jwt.encode(data, config.AuthSettings.SECRET_KEY, algorithm=config.AuthSettings.ALGORITHM),
        payload=data,
        expire=expiration_date
    )

    return token

def _create_refresh_token(
    data: dict
) -> JwtTokenSchema:
    expiration_date = _get_utc_current() + timedelta(config.AuthSettings.REFRESH_TOKEN_EXPIRES_MINUTES)

    data[EXP] = expiration_date

    token = JwtTokenSchema(
        token=jwt.encode(data, config.AuthSettings.SECRET_KEY, algorithm=config.AuthSettings.ALGORITHM),
        payload=data,
        expire=expiration_date
    )

    return token

def create_token_pair(
    user: User
) -> TokenPair:
    data = {SUB: str(user.id), JTI: str(uuid.uuid4()), IAT: _get_utc_current()}

    return TokenPair(
        access=_create_access_token(data={**data}),
        refresh=_create_refresh_token(data={**data})
    )

async def decode_access_token(
    token: str
):
    try:
        data = jwt.decode(token, config.AuthSettings.SECRET_KEY, algorithms=[config.AuthSettings.ALGORITHM])
