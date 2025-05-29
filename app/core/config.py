from collections.abc import Callable
from pydantic_core.core_schema import computed_field
from pydantic import computed_field
from pydantic_settings import BaseSettings

from fastapi.security import OAuth2PasswordBearer


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = [
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ]
    POSTGRES_SERVER: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    def DATABASE_URI(self) -> str:
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"


class AuthSettings(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRES_MINUTES: int
    REFRESH_TOKEN_EXPIRES_MINUTES: int
    OAUTH2_MODEL: Callable = OAuth2PasswordBearer(tokenUrl="login")


settings = Settings()
auth_settings = AuthSettings()
