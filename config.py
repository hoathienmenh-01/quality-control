"""Centralized configuration using pydantic-settings"""
from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "QC System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/qc_db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Auth
    SECRET_KEY: str = ""  # MUST be set via .env or environment variable
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    ALGORITHM: str = "HS256"

    # Camera — accept both CAMERA_WIDTH and CAMERA_RESOLUTION_WIDTH
    CAMERA_ID: int = 0
    CAMERA_WIDTH: int = Field(default=1920, alias="CAMERA_RESOLUTION_WIDTH")
    CAMERA_HEIGHT: int = Field(default=1080, alias="CAMERA_RESOLUTION_HEIGHT")
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

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "populate_by_name": True,  # allow both alias and field name
    }


settings = Settings()

# Validate critical settings
if not settings.SECRET_KEY:
    raise RuntimeError(
        "SECRET_KEY is not set. "
        "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(64))' "
        "and add it to .env"
    )
