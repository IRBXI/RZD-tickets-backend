from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"

    # 60 minutes * 24 * 7 = 7 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # TODO: do some kind of loading of enviromental variables for these parameters
    # pydantic BaseSettings will handle the rest for us
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "1234"
    POSTGRES_DB: str = "rzd_database"

    @computed_field
    def DATABASE_URI(self) -> str:
        return f"postgres://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}"


class AuthSettings(BaseSettings):
    SECRET_KEY = "2d3a29f91e2c47f80394001c227622ac25eb40279b01df42d865fee9631dcaaf"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES = 30
    REFRESH_TOKEN_EXPIRES_MINUTES = 30 * 24 * 60 # in 20 days


settings = Settings()
