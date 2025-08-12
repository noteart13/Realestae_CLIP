from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "realestate-clip-api"
    ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    # HTTP
    USER_AGENT: str = "Mozilla/5.0 (compatible; RealestateBot/1.0)"
    HTTP_TIMEOUT: int = 20
    HTTP_RETRIES: int = 2

    # scraping control
    MAX_IMAGES: int = 5

    # CLIP
    CLIP_MODEL: str = "ViT-B/32"
    CLIP_DEVICE: str = "auto"  # "cuda" | "cpu" | "auto"

    # CORS (mở rộng nếu cần)
    CORS_ORIGINS: list[AnyHttpUrl] = []

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
