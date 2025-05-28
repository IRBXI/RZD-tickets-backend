from collections.abc import Callable
from pydantic_settings import BaseSettings

from fastapi.security import OAuth2PasswordBearer


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    REFRESH_TOKEN_EXPIRES_MINUTES: int
    OAUTH2_MODEL: Callable = OAuth2PasswordBearer(tokenUrl="login")


settings = Settings()
auth_settings = AuthSettings()
