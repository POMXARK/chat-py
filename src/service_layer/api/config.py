from pydantic import BaseSettings


class WebApiSettings(BaseSettings):
    ...

    class Config:
        env_prefix = "app_"
