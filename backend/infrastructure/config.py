from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./smart_city.db"
    max_mode: str = "mock"  # mock | real
    max_bot_token: str = ""
    jwt_secret: str = "dev-secret-change-me"
    jwt_algorithm: str = "HS256"
    sla_high_hours: int = 2
    sla_medium_hours: int = 8
    sla_low_hours: int = 24


def get_settings() -> Settings:
    return Settings()
