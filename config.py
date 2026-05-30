"""Centralized configuration using pydantic-settings"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "QC System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/qc_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = ""  # MUST be set via .env or environment variable
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"

    # Camera
    CAMERA_ID: int = 0
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_FPS: int = 30

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str] = None
    TELEGRAM_CHAT_ID: Optional[str] = None

    # Export
    EXPORT_DIR: str = "exports"
    CAPTURES_DIR: str = "captures"

    # Thresholds
    ALERT_THRESHOLD_RATE: float = 0.1  # 10% fail rate triggers alert
    CONSECUTIVE_FAIL_THRESHOLD: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Validate critical settings
if not settings.SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(64))' "
        "and add it to .env"
    )
