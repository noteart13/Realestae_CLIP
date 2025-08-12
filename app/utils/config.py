# app/utils/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl

class Settings(BaseSettings):
    # App
    APP_NAME: str = "realestate-clip-api"
    ENV: str = "local"
    LOG_LEVEL: str = "INFO"

    # HTTP client
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
    HTTP_TIMEOUT: int = 20          # read-timeout (giây)
    HTTP_VERIFY: bool = True
    HTTP_LANG: str = "en-AU,en;q=0.8"
    HTTP_RETRIES: int = 2           # <-- BỔ SUNG

    # Search / DDG
    MAX_RESULTS: int = 3            # <-- BỔ SUNG
    SEARCH_RETRIES: int = 4         # <-- BỔ SUNG
    SEARCH_BACKOFF_BASE: float = 1.8  # <-- BỔ SUNG
    DDG_REGION: str = "au-en"       # hoặc "wt-wt"
    PROXY_URL: str = ""
    
    # Scrape / Images
    MAX_IMAGES: int = 4

    # CLIP
    CLIP_MODEL: str = "ViT-B/32"
    CLIP_DEVICE: str = "auto"

    # Pydantic v2 settings
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore",   # <-- cho phép có biến thừa trong .env
    )
    REQUEST_DELAY_MIN: float = 1.2
    REQUEST_DELAY_MAX: float = 3.5
    BACKOFF_BASE: float = 1.8
    MAX_BACKOFF_ATTEMPTS: int = 3
    ROTATE_UA: bool = True
    UA_POOL: list[str] = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36",
    ]
    PROXY_URL: str = ""  # ví dụ: http://user:pass@host:port

settings = Settings()
