from pydantic_settings import BaseSettings
from typing import Optional
import json
import os


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Law Platform API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - accepts both string (JSON array) and list format
    ALLOWED_ORIGINS: str | list[str] = '["http://localhost:3000"]'

    class Config:
        # Use .env.production if ENV=production, otherwise use .env.local
        env_file = ".env.production" if os.getenv("ENV") == "production" else ".env.local"
        case_sensitive = True

    @property
    def cors_origins(self) -> list[str]:
        """Parse ALLOWED_ORIGINS if it's a string, otherwise return as-is"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            try:
                return json.loads(self.ALLOWED_ORIGINS)
            except json.JSONDecodeError:
                # If parsing fails, return as single-item list
                return [self.ALLOWED_ORIGINS]
        return self.ALLOWED_ORIGINS


settings = Settings()
