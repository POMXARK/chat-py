from pathlib import Path

from pydantic import BaseSettings

PROJECT_DIR = Path(__file__).parent.parent.parent.parent


class WebApiSettings(BaseSettings):
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    jwt_expires_access_m: int = 15
    jwt_expires_refresh_h: int = 48

    class Config:
        env_prefix = "app_"
        env_file = f"{PROJECT_DIR}/.env"
