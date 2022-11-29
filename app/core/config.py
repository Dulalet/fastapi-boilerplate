import pathlib
from functools import lru_cache

from pydantic import BaseSettings

from app.core.vault import get_secrets

# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent


secrets = get_secrets()


class Settings(BaseSettings):
    DATABASE_URL: str = secrets.get("DATABASE_URL")

    class Config:
        case_sensitive = True


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()()
