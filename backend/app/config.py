from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    APP_NAME: str = "Zircon FRT"
    DEBUG: bool = False
    VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://zircon:zircon@postgres:5432/zircon"

    # Elasticsearch
    ELASTICSEARCH_URL: str = "http://elasticsearch:9200"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Security
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # AES-256 encryption key (base64-encoded 32 bytes)
    ENCRYPTION_KEY: str = "change-me-base64-encoded-32-bytes"

    # ClamAV
    CLAMAV_HOST: str = "clamav"
    CLAMAV_PORT: int = 3310

    # CORS
    CORS_ORIGINS: str = "http://localhost,http://localhost:3000,http://localhost:5173"

    # File upload
    UPLOAD_DIR: str = "/app/uploads"
    MAX_FILE_SIZE_MB: int = 100

    # Admin
    ADMIN_EMAIL: str = "admin@zircon.local"
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin123"

    # SMTP (optional)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "noreply@zircon.local"

    # Telegram (optional)
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
