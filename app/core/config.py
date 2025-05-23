from pydantic_settings import BaseSettings


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


settings = Settings()
authSettings = AuthSettings()
