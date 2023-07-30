from pathlib import Path
from pydantic import BaseSettings, PostgresDsn, validator

PROJECT_DIR = Path(__file__).parent.parent.parent.parent


class DatabaseSettings(BaseSettings):

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str
    DEFAULT_DATABASE_USER: str
    DEFAULT_DATABASE_PASSWORD: str
    DEFAULT_DATABASE_PORT: str
    DEFAULT_DATABASE_DB: str
    DEFAULT_SQLALCHEMY_DATABASE_URI: str = ""

    @validator("DEFAULT_SQLALCHEMY_DATABASE_URI")
    def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values["DEFAULT_DATABASE_USER"],
            password=values["DEFAULT_DATABASE_PASSWORD"],
            host=values["DEFAULT_DATABASE_HOSTNAME"],
            port=values["DEFAULT_DATABASE_PORT"],
            path=f"/{values['DEFAULT_DATABASE_DB']}",
        )

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings: DatabaseSettings = DatabaseSettings()  # type: ignore
