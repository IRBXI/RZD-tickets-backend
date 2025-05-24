from pydantic import ValidationError
from typing_extensions import Annotated
from app.core.jwt import JTI, decode_access_token, JWTError
from app.core.exceptions import NonExistentException, BadRequestException, AuthFailedException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.models import db_models, models
from app.core.jwt import SUB


oauth2_model = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_active_user(token: Annotated[str, Depends(oauth2_model)]):
    try:
        data = await decode_access_token(token=token)
        if not (user_id := data[SUB]):
            raise AuthFailedException("Invalid token format")

        if not (user := await db_models.User.get_or_none(id=user_id)):
            raise AuthFailedException("User not found")

        return models.User.model_validate(user)

    except JWTError:
        AuthFailedException("Invalid token")
