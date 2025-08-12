# đổi import
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl  # AnyHttpUrl vẫn ở pydantic

from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "realestate-clip-api"
    ENV: str = "local"
    LOG_LEVEL: str = "INFO"
    USER_AGENT: str = "Mozilla/5.0 (compatible; RealestateBot/1.0)"
    HTTP_TIMEOUT: int = 20
    HTTP_RETRIES: int = 2
    MAX_IMAGES: int = 5
    CLIP_MODEL: str = "ViT-B/32"
    CLIP_DEVICE: str = "auto"
    CORS_ORIGINS: list[AnyHttpUrl] = []

    # v2: dùng model_config thay cho class Config
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

settings = Settings()
