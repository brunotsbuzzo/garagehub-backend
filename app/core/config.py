from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_SECRET_KEY: str = "change-me-in-production"

    API_V1_PREFIX: str = "/api/v1"

    PROJECT_NAME: str = "GarageHub API"
    PROJECT_VERSION: str = "0.1.0"

    DATABASE_URL: str = "postgresql+asyncpg://garagehub:garagehub@localhost:5432/garagehub"

    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()