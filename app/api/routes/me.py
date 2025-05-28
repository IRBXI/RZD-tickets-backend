from fastapi import APIRouter, Depends
from typing import Annotated

from app.core.exceptions import AuthFailedException
from app.models import User
from app.services import AbstractAuthService, get_auth_service
from app.core.config import auth_settings

router = APIRouter(tags=["me"])


@router.get("/me", response_model=User)
async def get_me(
    token: Annotated[str, Depends(auth_settings.OAUTH2_MODEL)],
    auth_service: Annotated[AbstractAuthService, Depends(get_auth_service)],
):
    try:
        user = auth_service.get_current_active_user(token)
    except AuthFailedException:
        raise
    return user
