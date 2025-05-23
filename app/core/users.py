from socket import fromfd
from re import I
from typing_extensions import Annotated
from app.api.routes.login import oauth2_model, NonExistentException, BadRequestException
from app.core.jwt import JTI, decode_access_token
from fastapi import Depends

from app.models import db_models, models


async def _get_current_user(token: Annotated[str, Depends(oauth2_model)]):
    data = await decode_access_token(token=token)
    user = db_models.User.get_or_none(id=data[JTI])
    if not user:
        raise NonExistentException

    return user


async def get_current_active_user(token: Annotated[str, Depends(oauth2_model)]):
    user = await _get_current_user(token=token)

    if not user.active:
        raise BadRequestException("User is inactive")

    return models.User.from_orm(user)
