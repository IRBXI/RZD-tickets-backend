from pydantic import computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://127.0.0.1:3000", "http://localhost:3000"]

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


settings = Settings()
